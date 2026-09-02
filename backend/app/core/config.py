"""Embedding configuration loaded from environment variables.

All values have sensible defaults; only the API key needs to be provided
via the environment (never committed to source).
"""
import os
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EmbeddingSettings:
    """Settings for the embedding provider, read from environment variables."""

    #: Free-form API key for the chosen provider (Jina, Cohere, etc.).
    #: Must be set before calling embed_documents/embed_query; a clear
    #: error is raised if the key is missing.
    api_key: str = field(default="", metadata={"env": "EMBEDDING_API_KEY"})

    #: model name used for embedding; default depends on the provider
    #: selected (Jina's free tier models are fine choices).
    model: str = field(default="jina-embeddings-v5-text-nano")

    #: Number of chunk texts to send per HTTP request to the embedding API.
    #: Most providers support batching; too-large batches risk 429 errors.
    batch_size: int = field(default=32, metadata={"env": "EMBEDDING_BATCH_SIZE"})

    #: Request timeout in seconds; guards against hanging calls.
    timeout_seconds: int = field(default=30, metadata={"env": "EMBEDDING_TIMEOUT_SECONDS"})

    #: Which provider implementation to use. Subclasses of
    #: EmbeddingProvider are mapped by this string in the factory.
    provider: str = field(default="jina")

    #: Optional transport override for injection during tests.
    transport: Any = field(default=None, metadata={"env": None})

    #: Optional pre-known vector dimensionality; when set the provider
    #: skips the dimensionality-discovery call.
    dimension: int | None = field(default=None, metadata={"env": None})

    def __post_init__(self) -> None:
        if self.api_key == "":
            self.api_key = os.getenv("EMBEDDING_API_KEY", "")


def load_embedding_settings() -> EmbeddingSettings:
    """Convenience wrapper that returns a settings instance from process env."""
    return EmbeddingSettings()