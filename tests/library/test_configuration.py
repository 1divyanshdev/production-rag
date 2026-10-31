"""
Tests for library configuration and settings management.
"""
import os
import pytest

from rag_core import (
    EmbeddingSettings,
    VectorStoreSettings,
    LLMSettings,
    RetrievalSettings,
)


class TestEmbeddingSettingsLibrary:
    """Test embedding settings for library usage."""

    def test_settings_accept_api_key_directly(self):
        """Settings should accept API key without environment."""
        settings = EmbeddingSettings(api_key="direct-key")
        assert settings.api_key == "direct-key"

    def test_settings_with_all_parameters(self):
        """Settings should accept all configuration parameters."""
        settings = EmbeddingSettings(
            api_key="test-key",
            model="custom-model",
            batch_size=64,
            timeout_seconds=60,
            provider="jina",
            dimension=512,
        )
        
        assert settings.api_key == "test-key"
        assert settings.model == "custom-model"
        assert settings.batch_size == 64
        assert settings.timeout_seconds == 60
        assert settings.provider == "jina"
        assert settings.dimension == 512


class TestVectorStoreSettingsLibrary:
    """Test vector store settings for library usage."""

    def test_local_mode_settings(self):
        """Settings should support local embedded mode."""
        settings = VectorStoreSettings(path="./local_qdrant")
        assert settings.path == "./local_qdrant"
        assert settings.url == ""

    def test_server_mode_settings(self):
        """Settings should support server mode."""
        settings = VectorStoreSettings(
            url="http://localhost:6333",
            api_key="qdrant-key",
        )
        assert settings.url == "http://localhost:6333"
        assert settings.api_key == "qdrant-key"

    def test_custom_collection_name(self):
        """Settings should support custom collection names."""
        settings = VectorStoreSettings(collection="custom_collection")
        assert settings.collection == "custom_collection"


class TestLLMSettingsLibrary:
    """Test LLM settings for library usage."""

    def test_openai_compatible_settings(self):
        """Settings should support OpenAI-compatible endpoints."""
        settings = LLMSettings(
            api_key="llm-key",
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.1-8b-instant",
        )
        
        assert settings.api_key == "llm-key"
        assert settings.base_url == "https://api.groq.com/openai/v1"
        assert settings.model == "llama-3.1-8b-instant"

    def test_generation_parameters(self):
        """Settings should support generation parameters."""
        settings = LLMSettings(
            api_key="key",
            base_url="http://test",
            model="test",
            temperature=0.7,
            max_tokens=2048,
            timeout_seconds=120,
        )
        
        assert settings.temperature == 0.7
        assert settings.max_tokens == 2048
        assert settings.timeout_seconds == 120


class TestRetrievalSettingsLibrary:
    """Test retrieval settings for library usage."""

    def test_custom_top_k(self):
        """Settings should support custom top_k."""
        settings = RetrievalSettings(top_k=10)
        assert settings.top_k == 10

    def test_custom_score_threshold(self):
        """Settings should support custom score threshold."""
        settings = RetrievalSettings(score_threshold=0.5)
        assert settings.score_threshold == 0.5

    def test_combined_retrieval_settings(self):
        """Settings should support all retrieval parameters."""
        settings = RetrievalSettings(top_k=7, score_threshold=0.4)
        assert settings.top_k == 7
        assert settings.score_threshold == 0.4


class TestConfigurationValidation:
    """Test configuration validation and error handling."""

    def test_missing_embedding_key_allows_construction(self):
        """Missing embedding key should not fail at construction."""
        # Settings construction should succeed even without key
        settings = EmbeddingSettings(api_key="")
        assert settings.api_key == ""

    def test_empty_llm_settings_allow_construction(self):
        """Empty LLM settings should allow construction."""
        # Settings construction should succeed
        settings = LLMSettings()
        # Validation happens at provider initialization, not here
        assert isinstance(settings, LLMSettings)
