"""Tests for LLM provider factory auto-detection."""
import pytest

from rag_core.config import LLMSettings
from rag_core.llm import (
    get_llm_provider,
    OpenAICompatibleLLMProvider,
    AnthropicClaudeProvider,
    GoogleGeminiProvider,
)


class TestProviderAutoDetection:
    """Test that get_llm_provider returns the correct provider class."""

    def test_anthropic_detected_by_base_url(self):
        settings = LLMSettings(
            api_key="sk-ant-test",
            base_url="https://api.anthropic.com/v1",
            model="claude-3-5-sonnet-20241022",
        )
        provider = get_llm_provider(settings)
        assert isinstance(provider, AnthropicClaudeProvider)

    def test_anthropic_detected_by_model_name(self):
        settings = LLMSettings(
            api_key="sk-ant-test",
            base_url="https://example.com",
            model="claude-3-opus-20240229",
        )
        provider = get_llm_provider(settings)
        assert isinstance(provider, AnthropicClaudeProvider)

    def test_gemini_detected_by_base_url(self):
        settings = LLMSettings(
            api_key="AIza-test",
            base_url="https://generativelanguage.googleapis.com/v1",
            model="gemini-1.5-pro",
        )
        provider = get_llm_provider(settings)
        assert isinstance(provider, GoogleGeminiProvider)

    def test_gemini_detected_by_model_name(self):
        settings = LLMSettings(
            api_key="AIza-test",
            base_url="https://example.com",
            model="gemini-1.5-flash",
        )
        provider = get_llm_provider(settings)
        assert isinstance(provider, GoogleGeminiProvider)

    def test_openai_compatible_default_groq(self):
        settings = LLMSettings(
            api_key="gsk-test",
            base_url="https://api.groq.com/openai/v1",
            model="openai/gpt-oss-20b",
        )
        provider = get_llm_provider(settings)
        assert isinstance(provider, OpenAICompatibleLLMProvider)

    def test_openai_compatible_default_openrouter(self):
        settings = LLMSettings(
            api_key="sk-or-test",
            base_url="https://openrouter.ai/api/v1",
            model="mistralai/mistral-7b-instruct:free",
        )
        provider = get_llm_provider(settings)
        assert isinstance(provider, OpenAICompatibleLLMProvider)

    def test_openai_compatible_default_openai(self):
        settings = LLMSettings(
            api_key="sk-test",
            base_url="https://api.openai.com/v1",
            model="gpt-4o-mini",
        )
        provider = get_llm_provider(settings)
        assert isinstance(provider, OpenAICompatibleLLMProvider)
