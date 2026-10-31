"""Abstract interface for LLM chat providers (grounded generation step)."""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Strategy interface for chat-completion backends."""

    @property
    @abstractmethod
    def model(self) -> str:
        """Name of the chat model backing this provider."""
        ...

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Return the assistant reply for the given prompts.

        Implementations must raise :class:`LLMError` on auth/quota/network
        failures or malformed responses - never leak raw HTTP exceptions.
        """
        ...
