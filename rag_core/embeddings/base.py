"""Abstract interface for embedding providers.

All providers must implement :meth:`embed_documents` and
:meth:`embed_query`.  The query variant typically uses a different
instruction prefix (query/passage asymmetry) but returns a vector of the
same dimensionality.
"""
from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    """Strategy interface for text-embedding services."""

    @property
    @abstractmethod
    def model(self) -> str:
        """Name of the model backing this provider."""
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Dimensionality of the vectors emitted by this provider."""
        ...

    @property
    @abstractmethod
    def normalizes_vectors(self) -> bool:
        """Whether this provider returns L2-normalized vectors (cosine
        similarity degenerates to dot product)."""
        ...

    @abstractmethod
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of chunk texts.

        Returns a list parallel to the input: ``len(results) == len(texts)``.
        Raises :class:`EmbeddingError` on auth/quota/network trouble or
        unexpected response shape.
        """
        ...

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query string.

        Some models treat queries differently (instruction prefix, separate
        model, etc.).  This method encapsulates that concern so the rest of
        the pipeline stays model-agnostic.
        """
        ...