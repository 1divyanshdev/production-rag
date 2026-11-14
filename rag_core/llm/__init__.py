"""LLM providers for answer generation."""

from typing import Any, Optional

from rag_core.config import LLMSettings
from rag_core.llm.base import LLMProvider
from rag_core.llm.openai_compat import OpenAICompatibleLLMProvider
from rag_core.llm.anthropic_provider import AnthropicClaudeProvider
from rag_core.llm.gemini_provider import GoogleGeminiProvider

__all__ = [
    "LLMProvider",
    "OpenAICompatibleLLMProvider",
    "AnthropicClaudeProvider",
    "GoogleGeminiProvider",
    "get_llm_provider",
]


def get_llm_provider(
    settings: LLMSettings,
    transport: Optional[Any] = None
) -> LLMProvider:
    """Factory function that returns the appropriate LLM provider based on settings.
    
    Auto-detects provider based on base_url or model name:
    - Anthropic: base_url contains "anthropic.com" or model starts with "claude"
    - Google: base_url contains "googleapis.com" or model starts with "gemini"
    - OpenAI-compatible: everything else (Groq, OpenRouter, OpenAI, etc.)
    
    Args:
        settings: LLM configuration from environment
        transport: Optional httpx transport for testing
        
    Returns:
        Appropriate LLMProvider instance
        
    Examples:
        >>> # Claude
        >>> settings = LLMSettings(
        ...     api_key="sk-ant-...",
        ...     base_url="https://api.anthropic.com/v1",
        ...     model="claude-3-5-sonnet-20241022"
        ... )
        >>> provider = get_llm_provider(settings)  # AnthropicClaudeProvider
        
        >>> # Gemini
        >>> settings = LLMSettings(
        ...     api_key="AIza...",
        ...     base_url="https://generativelanguage.googleapis.com/v1",
        ...     model="gemini-1.5-pro"
        ... )
        >>> provider = get_llm_provider(settings)  # GoogleGeminiProvider
        
        >>> # OpenAI-compatible (Groq, OpenRouter, etc.)
        >>> settings = LLMSettings(
        ...     api_key="gsk_...",
        ...     base_url="https://api.groq.com/openai/v1",
        ...     model="openai/gpt-oss-20b"
        ... )
        >>> provider = get_llm_provider(settings)  # OpenAICompatibleLLMProvider
    """
    base_url = settings.base_url.lower() if settings.base_url else ""
    model = settings.model.lower() if settings.model else ""
    
    # Detect Anthropic/Claude
    if "anthropic.com" in base_url or model.startswith("claude"):
        return AnthropicClaudeProvider(settings, transport=transport)
    
    # Detect Google/Gemini
    if "googleapis.com" in base_url or model.startswith("gemini"):
        return GoogleGeminiProvider(settings, transport=transport)
    
    # Default to OpenAI-compatible (Groq, OpenRouter, OpenAI, etc.)
    return OpenAICompatibleLLMProvider(settings, transport=transport)
