"""OpenAI (and OpenAI-compatible) provider.

The SDK is imported lazily so the base image needn't ship it unless this provider
is actually configured. Install with the `providers` extra.
"""
from django.conf import settings

from apps.ai.exceptions import ProviderError
from apps.ai.providers.base import AIProvider, Message, ProviderResponse


class OpenAIProvider(AIProvider):
    name = "openai"

    def _client(self):
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - depends on optional extra
            raise ProviderError(
                "openai package not installed. `pip install '.[providers]'`."
            ) from exc
        if not settings.OPENAI_API_KEY:
            raise ProviderError("OPENAI_API_KEY is not configured.")
        return OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL or None,
        )

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
        kwargs: dict = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timeout": timeout,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        try:
            resp = client.chat.completions.create(**kwargs)
        except Exception as exc:  # pragma: no cover - network
            raise ProviderError(f"OpenAI request failed: {exc}") from exc

        usage = resp.usage
        return ProviderResponse(
            content=resp.choices[0].message.content or "",
            model=resp.model,
            tokens_in=getattr(usage, "prompt_tokens", 0) or 0,
            tokens_out=getattr(usage, "completion_tokens", 0) or 0,
            raw=resp,
        )
