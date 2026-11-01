"""
Retrieval service: turn a natural-language query into scored chunks.

    question -> embed_query -> vector search (+ optional filters) -> hits
"""
import logging
from typing import Optional

from rag_core.config import RetrievalSettings
from rag_core.exceptions import EmbeddingError, VectorStoreError
from rag_core.models.retrieval import ScoredChunk
from rag_core.embeddings.base import EmbeddingProvider
from rag_core.vector_stores.qdrant_store import QdrantVectorStore

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
        """
        Retrieve the most relevant chunks for a question.

        Embeds the question and performs semantic vector search over the
        indexed chunks. Results are ranked by cosine similarity and can be
        filtered by document ID or custom metadata.

        Args:
            question: The question text to search for.
            document_id: Optional document ID to restrict search.
            extra_filters: Optional metadata filters (dict of key-value pairs).
            top_k: Maximum number of results (overrides config default).

        Returns:
            List of ScoredChunk objects ordered by relevance (highest first).

        Raises:
            ValueError: If question is empty.
            EmbeddingError: If embedding the question fails.
            VectorStoreError: If vector search fails.
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
