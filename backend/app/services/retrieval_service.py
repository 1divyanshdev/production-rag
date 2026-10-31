"""
Retrieval service: turn a natural-language query into scored chunks.

    question -> embed_query -> vector search (+ optional filters) -> hits
"""
import logging
from typing import Optional

from backend.app.core.config import RetrievalSettings
from backend.app.core.exceptions import EmbeddingError, VectorStoreError
from backend.app.models.retrieval import ScoredChunk
from backend.app.services.embeddings.base import EmbeddingProvider
from backend.app.services.vector_store import QdrantVectorStore

logger = logging.getLogger(__name__)


class RetrievalService:
    """Dense (semantic) retrieval over the indexed chunk store."""

    def __init__(
        self,
        embedder: EmbeddingProvider,
        store: QdrantVectorStore,
        settings: Optional[RetrievalSettings] = None,
    ):
        self.embedder = embedder
        self.store = store
        self.settings = settings or RetrievalSettings()

    def retrieve(
        self,
        question: str,
        document_id: Optional[str] = None,
        extra_filters: Optional[dict] = None,
        top_k: Optional[int] = None,
    ) -> list:
        """Return up to top_k scored chunks for the question.

        Raises:
            ValueError: empty question.
            EmbeddingError / VectorStoreError: provider or store failure.
        """
        if not question or not question.strip():
            raise ValueError("Question must be a non-empty string.")

        query_vector = self.embedder.embed_query(question.strip())
        hits = self.store.search(
            query_vector=query_vector,
            top_k=top_k or self.settings.top_k,
            document_id=document_id,
            extra_filters=extra_filters,
        )
        logger.info(
            "Retrieval for %r: %d hit(s), best score %.3f",
            question[:60],
            len(hits),
            hits[0].score if hits else 0.0,
        )
        return hits
