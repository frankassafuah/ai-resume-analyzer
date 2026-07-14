"""Provider abstraction.

Every LLM vendor is hidden behind `AIProvider.complete`, which takes a
provider-neutral list of chat messages and returns a `ProviderResponse`. The
rest of the app depends only on this interface — swapping OpenAI ↔ Claude ↔
Gemini is a config change, never a code change (ADR-0002).
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

# Provider-neutral chat message, e.g. {"role": "system"|"user"|"assistant", "content": "..."}
Message = dict[str, str]


@dataclass
class ProviderResponse:
    content: str
    model: str
    tokens_in: int = 0
    tokens_out: int = 0
    raw: Any = None


class AIProvider(ABC):
    """Interface all concrete providers implement."""

    name: str = "base"

    @abstractmethod
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
        """Send a chat completion request and return the normalized response."""
        raise NotImplementedError

    @staticmethod
    def split_system(messages: list[Message]) -> tuple[str | None, list[Message]]:
        """Helper for providers (Claude/Gemini) that take the system prompt
        separately from the message list."""
        system = next((m["content"] for m in messages if m["role"] == "system"), None)
        rest = [m for m in messages if m["role"] != "system"]
        return system, rest
