"""AI-layer exceptions (kept separate from HTTP concerns)."""


class AIError(Exception):
    """Base class for all AI-layer failures."""


class ProviderError(AIError):
    """A provider call failed (network, auth, rate limit, unknown provider)."""


class ResponseParseError(AIError):
    """The model returned output that could not be parsed/validated."""
