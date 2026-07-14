"""AIGateway — the single choke point for LLM calls.

Responsibilities: pick the provider (config-driven), enforce timeout, retry
transient failures with backoff, measure latency, compute cost, and write an
`AIGenerationLog` row per attempt. Callers get a normalized `ProviderResponse`
and never touch a vendor SDK directly.
"""
import logging
import time
from decimal import Decimal

from django.conf import settings

from apps.ai.exceptions import ProviderError
from apps.ai.models import AIGenerationLog
from apps.ai.providers import AIProvider, ProviderResponse, get_provider

logger = logging.getLogger("apps.ai")


class AIGateway:
    def __init__(self, provider: AIProvider | None = None) -> None:
        self.provider = provider or get_provider()

    def complete(
        self,
        messages: list[dict],
        *,
        model: str,
        prompt_version: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
        json_mode: bool = True,
        user=None,
        analysis=None,
    ) -> ProviderResponse:
        temperature = settings.LLM_TEMPERATURE if temperature is None else temperature
        max_tokens = max_tokens or settings.LLM_MAX_TOKENS
        attempts = settings.LLM_MAX_RETRIES + 1

        last_exc: Exception | None = None
        for attempt in range(attempts):
            started = time.monotonic()
            try:
                resp = self.provider.complete(
                    messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    json_mode=json_mode,
                    timeout=settings.LLM_REQUEST_TIMEOUT,
                )
                self._log(
                    user, analysis, prompt_version, model, resp,
                    latency_ms=int((time.monotonic() - started) * 1000),
                    status=AIGenerationLog.Status.SUCCESS,
                )
                return resp
            except Exception as exc:  # noqa: BLE001 — normalized below
                last_exc = exc
                logger.warning(
                    "LLM attempt %d/%d failed (%s): %s",
                    attempt + 1, attempts, self.provider.name, exc,
                )
                if attempt == attempts - 1:
                    self._log(
                        user, analysis, prompt_version, model, None,
                        latency_ms=int((time.monotonic() - started) * 1000),
                        status=AIGenerationLog.Status.ERROR, error=str(exc),
                    )
                    break
                time.sleep(0.5 * (attempt + 1))  # linear backoff

        raise ProviderError(str(last_exc)) from last_exc

    def _log(
        self, user, analysis, prompt_version, model,
        resp: ProviderResponse | None, *, latency_ms: int, status: str,
        error: str = "",
    ) -> None:
        tokens_in = resp.tokens_in if resp else 0
        tokens_out = resp.tokens_out if resp else 0
        try:
            AIGenerationLog.objects.create(
                user=user,
                analysis=analysis,
                provider=self.provider.name,
                model=(resp.model if resp else model),
                prompt_version=prompt_version,
                status=status,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost_usd=self._cost(model, tokens_in, tokens_out),
                latency_ms=latency_ms,
                error=error[:2000],
            )
        except Exception:  # pragma: no cover — logging must never break the call
            logger.exception("Failed to write AIGenerationLog")

    @staticmethod
    def _cost(model: str, tokens_in: int, tokens_out: int) -> Decimal:
        rates = settings.LLM_COST_PER_1K.get(model)
        if not rates:
            return Decimal("0")
        in_rate, out_rate = rates
        cost = (tokens_in * in_rate + tokens_out * out_rate) / 1000
        return Decimal(str(round(cost, 5)))
