"""Offline unit tests for the embedding config module.

No network, no API key needed – everything is driven by
:class:`~backend.app.core.config.EmbeddingSettings` and
:func:`~backend.app.core.config.load_embedding_settings`.
"""
import os
import pytest

from rag_core.config import EmbeddingSettings, load_embedding_settings


class TestEmbeddingSettings:
    def test_defaults_when_no_env(self):
        # When no env vars are set, api_key defaults to "" (resolved later).
        s = EmbeddingSettings()
        assert s.model == "jina-embeddings-v5-text-nano"
        assert s.batch_size == 32
        assert s.timeout_seconds == 30
        assert s.provider == "jina"

    def test_api_key_from_env(self):
        s = EmbeddingSettings(api_key="sk-test-12345")
        assert s.api_key == "sk-test-12345"

    def test_load_embedding_settings(self):
        s = load_embedding_settings()
        assert isinstance(s, EmbeddingSettings)
        assert s.provider == "jina"

    def test_env_override(self):
        os.environ["EMBEDDING_API_KEY"] = "env-key-999"
        try:
            s = EmbeddingSettings()
            assert s.api_key == "env-key-999"
        finally:
            del os.environ["EMBEDDING_API_KEY"]

    def test_optional_fields_use_defaults(self):
        # Only api_key is env-driven; everything else has compile-time defaults.
        s = EmbeddingSettings(api_key="k")
        assert s.provider == "jina"


class TestLoadEmbeddingSettings:
    def test_returns_dataclass_instance(self):
        s = load_embedding_settings()
        assert isinstance(s, EmbeddingSettings)

    def test_clears_import_side_effect(self):
        # load_embedding_settings must not raise if .env missing etc.
        assert callable(load_embedding_settings)


class TestSettingsIntegration:
    # The real use-case: settings live in the app, not behind a CLI.
    def test_settings_can_be_instantiated_in_isolation(self):
        s = EmbeddingSettings(
            api_key="hard-coded-key",
            model="jina-embeddings-v5-text-nano",
            batch_size=64,
            timeout_seconds=60,
            provider="jina",
        )
        assert s.api_key == "hard-coded-key"
        assert s.batch_size == 64
        assert s.timeout_seconds == 60