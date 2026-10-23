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


@dataclass
class VectorStoreSettings:
    """Settings for the vector store (Qdrant).

    Two modes:
      - Local mode (default): an embedded Qdrant persisted to ``path``.
        Requires no server or Docker - zero infrastructure.
      - Server mode: set ``url`` (e.g. http://localhost:6333 or a Qdrant
        Cloud endpoint) to talk to a running Qdrant instance instead.
    """

    #: Filesystem path for embedded/local Qdrant storage.
    path: str = field(
        default_factory=lambda: os.getenv("VECTOR_STORE_PATH", "./qdrant_storage")
    )

    #: Optional server URL; when set, takes priority over local path mode.
    url: str = field(default_factory=lambda: os.getenv("VECTOR_STORE_URL", ""))

    #: Optional API key for Qdrant Cloud (never logged).
    api_key: str = field(default_factory=lambda: os.getenv("VECTOR_STORE_API_KEY", ""))

    #: Name of the collection holding chunk vectors.
    collection: str = field(
        default_factory=lambda: os.getenv("VECTOR_COLLECTION", "rag_chunks")
    )


def load_vector_store_settings() -> VectorStoreSettings:
    return VectorStoreSettings()


@dataclass
class LLMSettings:
    """Settings for the LLM provider (OpenAI-compatible chat completions).

    Works with any OpenAI-compatible free endpoint (Groq, OpenRouter,
    Cohere compatibility API, etc.) by adjusting base_url/model.
    """

    api_key: str = field(default_factory=lambda: os.getenv("LLM_API_KEY", ""))

    #: Base URL of the OpenAI-compatible API, e.g. https://api.groq.com/openai/v1
    base_url: str = field(default_factory=lambda: os.getenv("LLM_BASE_URL", ""))

    #: Chat model name, e.g. llama-3.1-8b-instant (Groq, free tier).
    model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", ""))

    temperature: float = field(
        default_factory=lambda: float(os.getenv("LLM_TEMPERATURE", "0.1"))
    )

    max_tokens: int = field(
        default_factory=lambda: int(os.getenv("LLM_MAX_TOKENS", "1024"))
    )

    timeout_seconds: int = field(
        default_factory=lambda: int(os.getenv("LLM_TIMEOUT_SECONDS", "60"))
    )


def load_llm_settings() -> LLMSettings:
    return LLMSettings()


@dataclass
class RetrievalSettings:
    """Tuning knobs for retrieval and grounded generation."""

    #: How many chunks to retrieve per query.
    top_k: int = field(default_factory=lambda: int(os.getenv("RETRIEVAL_TOP_K", "5")))

    #: Minimum cosine similarity for the best hit; below this the system
    #: refuses to answer rather than hallucinate.
    score_threshold: float = field(
        default_factory=lambda: float(os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.35"))
    )


def load_retrieval_settings() -> RetrievalSettings:
    return RetrievalSettings()