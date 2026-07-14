"""Google Gemini provider. SDK imported lazily (install `providers` extra)."""
from django.conf import settings

from apps.ai.exceptions import ProviderError
from apps.ai.providers.base import AIProvider, Message, ProviderResponse


class GeminiProvider(AIProvider):
    name = "gemini"

    def _client(self):
        try:
            from google import genai
        except ImportError as exc:  # pragma: no cover - optional extra
            raise ProviderError(
                "google-genai package not installed. `pip install '.[providers]'`."
            ) from exc
        if not settings.GEMINI_API_KEY:
            raise ProviderError("GEMINI_API_KEY is not configured.")
        return genai.Client(api_key=settings.GEMINI_API_KEY)

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
        from google.genai import types

        client = self._client()
        system, turns = self.split_system(messages)
        # Flatten remaining turns into a single prompt (analysis is single-shot).
        prompt = "\n\n".join(m["content"] for m in turns)

        config = types.GenerateContentConfig(
            system_instruction=system,
            temperature=temperature,
            max_output_tokens=max_tokens,
            response_mime_type="application/json" if json_mode else "text/plain",
        )
        try:
            resp = client.models.generate_content(
                model=model, contents=prompt, config=config
            )
        except Exception as exc:  # pragma: no cover - network
            raise ProviderError(f"Gemini request failed: {exc}") from exc

        usage = getattr(resp, "usage_metadata", None)
        return ProviderResponse(
            content=resp.text or "",
            model=model,
            tokens_in=getattr(usage, "prompt_token_count", 0) or 0,
            tokens_out=getattr(usage, "candidates_token_count", 0) or 0,
            raw=resp,
        )
