"""
Dependency wiring for the API.

``get_services`` builds the full RAG stack once per process from env
settings. Tests override this dependency with a container built from
offline fakes, so no live API is ever contacted in the test suite.

The LLM provider is constructed lazily: uploading documents only needs
the embedding key, so a missing LLM_* config must not break /documents.
"""
import functools
import logging
from dataclasses import dataclass
from typing import Optional

from rag_core.chunking import ChunkingService
from rag_core.config import (
    load_embedding_settings,
    load_llm_settings,
    load_retrieval_settings,
    load_vector_store_settings,
)
from rag_core.embeddings import EmbeddingProvider, get_embedding_provider
from rag_core.generation import GenerationService
from rag_core.ingestion import IngestionPipeline
from rag_core.ingestion.ingestion_service import DocumentIngestionService
from rag_core.llm import LLMProvider, OpenAICompatibleLLMProvider
from rag_core.retrieval import RetrievalService
from rag_core.vector_stores import QdrantVectorStore

logger = logging.getLogger(__name__)


@dataclass
class Services:
    embedder: EmbeddingProvider
    store: QdrantVectorStore
    pipeline: IngestionPipeline
    retrieval: RetrievalService
    retrieval_settings: object
    _llm: Optional[LLMProvider] = None
    _llm_settings: Optional[object] = None
    _generation: Optional[GenerationService] = None

    @property
    def generation(self) -> GenerationService:
        """Generation service with lazy LLM construction."""
        if self._generation is None:
            if self._llm is None:
                llm_settings = self._llm_settings
                self._llm = OpenAICompatibleLLMProvider(llm_settings)
            self._generation = GenerationService(
                self.retrieval, self._llm, self.retrieval_settings
            )
        return self._generation


def build_services_from_settings() -> Services:
    """Construct the real service stack from environment configuration."""
    embedder = get_embedding_provider(load_embedding_settings())
    store = QdrantVectorStore(
        load_vector_store_settings(), dimension=embedder.dimension
    )
    retrieval_settings = load_retrieval_settings()
    pipeline = IngestionPipeline(
        ingestion=DocumentIngestionService(),
        chunker=ChunkingService(),
        embedder=embedder,
        store=store,
    )
    retrieval = RetrievalService(embedder, store, retrieval_settings)
    return Services(
        embedder=embedder,
        store=store,
        pipeline=pipeline,
        retrieval=retrieval,
        retrieval_settings=retrieval_settings,
        _llm=None,
        _llm_settings=load_llm_settings(),
    )


@functools.lru_cache(maxsize=1)
def get_services() -> Services:
    """FastAPI dependency: process-wide singleton service stack."""
    logger.info("Building RAG service stack from settings...")
    return build_services_from_settings()
