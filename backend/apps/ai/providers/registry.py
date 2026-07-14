"""Provider factory — maps the configured name to a provider instance."""
from django.conf import settings

from apps.ai.exceptions import ProviderError
from apps.ai.providers.base import AIProvider

# Import paths are resolved lazily inside get_provider so that importing this
# module never pulls in an optional SDK.
_ALIASES = {
    "fake": ("apps.ai.providers.fake", "FakeProvider"),
    "openai": ("apps.ai.providers.openai_provider", "OpenAIProvider"),
    "anthropic": ("apps.ai.providers.claude_provider", "ClaudeProvider"),
    "claude": ("apps.ai.providers.claude_provider", "ClaudeProvider"),
    "gemini": ("apps.ai.providers.gemini_provider", "GeminiProvider"),
    "google": ("apps.ai.providers.gemini_provider", "GeminiProvider"),
}


def get_provider(name: str | None = None) -> AIProvider:
    key = (name or settings.LLM_PROVIDER).lower()
    if key not in _ALIASES:
        raise ProviderError(
            f"Unknown LLM provider '{key}'. "
            f"Valid options: {', '.join(sorted(_ALIASES))}."
        )
    module_path, class_name = _ALIASES[key]
    import importlib

    provider_cls = getattr(importlib.import_module(module_path), class_name)
    return provider_cls()
