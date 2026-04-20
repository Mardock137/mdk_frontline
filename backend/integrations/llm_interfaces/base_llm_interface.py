"""Abstract interface for LLM providers.

Placeholder for Fase 1: guarantees that every concrete LLM adapter
(Anthropic, OpenAI, etc.) exposes the same set of methods.
"""

from abc import ABC, abstractmethod


class BaseLLMInterface(ABC):
    """Uniform contract shared by every LLM integration."""

    def __init__(self, model: str) -> None:
        self.model = model

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """Return a single text completion for the given prompt."""
        raise NotImplementedError
