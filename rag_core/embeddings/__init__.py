"""Embedding providers and factory."""

from rag_core.embeddings.base import EmbeddingProvider
from rag_core.embeddings.factory import get_embedding_provider
from rag_core.embeddings.jina_provider import JinaEmbeddingProvider

__all__ = [
    "EmbeddingProvider",
    "get_embedding_provider",
    "JinaEmbeddingProvider",
]
