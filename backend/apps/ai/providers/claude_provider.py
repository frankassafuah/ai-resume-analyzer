"""Anthropic Claude provider. SDK imported lazily (install `providers` extra)."""
from django.conf import settings

from apps.ai.exceptions import ProviderError
from apps.ai.providers.base import AIProvider, Message, ProviderResponse


class ClaudeProvider(AIProvider):
    name = "anthropic"

    def _client(self):
        try:
            from anthropic import Anthropic
        except ImportError as exc:  # pragma: no cover - optional extra
            raise ProviderError(
                "anthropic package not installed. `pip install '.[providers]'`."
            ) from exc
        if not settings.ANTHROPIC_API_KEY:
            raise ProviderError("ANTHROPIC_API_KEY is not configured.")
        return Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    def complete(
        self,
        messages: list[Message],
        *,
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 2000,
        json_mode: bool = True,
        timeout: int = 60,
    ) -> ProviderResponse:
        client = self._client()
        # Claude takes the system prompt separately from the turn messages.
        system, turns = self.split_system(messages)
        if json_mode:
            system = (system or "") + "\n\nRespond with a single valid JSON object only."
        try:
            resp = client.messages.create(
                model=model,
                system=system or "",
                messages=turns,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=timeout,
            )
        except Exception as exc:  # pragma: no cover - network
            raise ProviderError(f"Anthropic request failed: {exc}") from exc

        text = "".join(
            block.text for block in resp.content if getattr(block, "type", "") == "text"
        )
        usage = resp.usage
        return ProviderResponse(
            content=text,
            model=resp.model,
            tokens_in=getattr(usage, "input_tokens", 0) or 0,
            tokens_out=getattr(usage, "output_tokens", 0) or 0,
            raw=resp,
        )
