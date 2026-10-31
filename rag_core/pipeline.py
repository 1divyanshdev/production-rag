"""
Public RAG pipeline API.

This module provides the high-level interface for using Production RAG as a library.
External applications should primarily interact with RAGPipeline and RAGConfig.
"""
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

from rag_core.chunking import ChunkingService
from rag_core.config import (
    EmbeddingSettings,
    LLMSettings,
    RetrievalSettings,
    VectorStoreSettings,
    load_embedding_settings,
    load_llm_settings,
    load_retrieval_settings,
    load_vector_store_settings,
)
from rag_core.embeddings import EmbeddingProvider, get_embedding_provider
from rag_core.generation import GeneratedAnswer, GenerationService
from rag_core.ingestion import IngestionPipeline, IndexingResult
from rag_core.ingestion.ingestion_service import DocumentIngestionService
from rag_core.llm import LLMProvider, OpenAICompatibleLLMProvider
from rag_core.retrieval import RetrievalService
from rag_core.vector_stores import QdrantVectorStore

logger = logging.getLogger(__name__)


@dataclass
class RAGConfig:
    """
    Configuration for the RAG pipeline.

    All settings have defaults and can be loaded from environment variables.
    Explicit settings passed here override environment values.

    Args:
        embedding_settings: Configuration for the embedding provider.
        vector_store_settings: Configuration for the vector store.
        llm_settings: Configuration for the LLM provider.
        retrieval_settings: Configuration for retrieval behavior.
    """

    embedding_settings: Optional[EmbeddingSettings] = None
    vector_store_settings: Optional[VectorStoreSettings] = None
    llm_settings: Optional[LLMSettings] = None
    retrieval_settings: Optional[RetrievalSettings] = None

    def __post_init__(self):
        """Load settings from environment if not explicitly provided."""
        if self.embedding_settings is None:
            self.embedding_settings = load_embedding_settings()
        if self.vector_store_settings is None:
            self.vector_store_settings = load_vector_store_settings()
        if self.llm_settings is None:
            self.llm_settings = load_llm_settings()
        if self.retrieval_settings is None:
            self.retrieval_settings = load_retrieval_settings()


@dataclass
class QueryResult:
    """
    Result of a RAG query operation.

    Attributes:
        question: The original question.
        answer: The generated answer text.
        sources: List of source citations with metadata.
        refused: Whether the system refused to answer due to low confidence.
        cited_indices: List of [n] citation numbers found in the answer.
    """

    question: str
    answer: str
    sources: List[Dict]
    refused: bool = False
    cited_indices: List[int] = field(default_factory=list)


class RAGPipeline:
    """
    Main RAG pipeline orchestrator.

    This is the primary public interface for the Production RAG library.
    It coordinates document ingestion, retrieval, and answer generation.

    Example:
        ```python
        from rag_core import RAGPipeline, RAGConfig

        # Use environment variables for configuration
        config = RAGConfig()
        rag = RAGPipeline(config=config)

        # Index a document
        result = rag.index_document("path/to/document.pdf")
        print(f"Indexed {result.indexed_chunks} chunks")

        # Ask a question
        answer = rag.query("What is the main topic?")
        print(answer.answer)
        for source in answer.sources:
            print(f"  [{source['index']}] {source['filename']}, p.{source['page_number']}")
        ```
    """

    def __init__(self, config: Optional[RAGConfig] = None):
        """
        Initialize the RAG pipeline.

        Args:
            config: Configuration object. If None, loads from environment.
        """
        self.config = config or RAGConfig()

        # Initialize embedding provider
        self.embedder: EmbeddingProvider = get_embedding_provider(
            self.config.embedding_settings
        )

        # Initialize vector store
        self.vector_store = QdrantVectorStore(
            self.config.vector_store_settings, dimension=self.embedder.dimension
        )

        # Initialize ingestion pipeline
        self.ingestion_pipeline = IngestionPipeline(
            ingestion=DocumentIngestionService(),
            chunker=ChunkingService(),
            embedder=self.embedder,
            store=self.vector_store,
        )

        # Initialize retrieval service
        self.retrieval_service = RetrievalService(
            embedder=self.embedder,
            store=self.vector_store,
            settings=self.config.retrieval_settings,
        )

        # Initialize LLM provider (lazy - only if needed)
        self._llm_provider: Optional[LLMProvider] = None

        # Initialize generation service (lazy - only if needed)
        self._generation_service: Optional[GenerationService] = None

        logger.info("RAG pipeline initialized successfully")

    @property
    def llm_provider(self) -> LLMProvider:
        """Lazy initialization of LLM provider."""
        if self._llm_provider is None:
            self._llm_provider = OpenAICompatibleLLMProvider(self.config.llm_settings)
        return self._llm_provider

    @property
    def generation_service(self) -> GenerationService:
        """Lazy initialization of generation service."""
        if self._generation_service is None:
            self._generation_service = GenerationService(
                retrieval=self.retrieval_service,
                llm=self.llm_provider,
                settings=self.config.retrieval_settings,
            )
        return self._generation_service

    def index_document(
        self,
        file_source: Union[str, Path, bytes],
        filename: Optional[str] = None,
        custom_metadata: Optional[dict] = None,
        force_reindex: bool = False,
    ) -> IndexingResult:
        """
        Index a PDF document for retrieval.

        Args:
            file_source: Path to PDF file or raw bytes.
            filename: Name of the file (required if file_source is bytes).
            custom_metadata: Optional dict of custom metadata to attach.
            force_reindex: If True, reindex even if document was already indexed.

        Returns:
            IndexingResult with information about the indexing operation.

        Raises:
            FileNotFoundError: If path-based source does not exist.
            ValueError: If inputs are invalid.
            PDFParseError: If PDF cannot be parsed (corrupt or encrypted).
            NoTextExtractedError: If PDF has no extractable text.
            EmbeddingError: If embedding provider fails.
            VectorStoreError: If vector store operation fails.
        """
        return self.ingestion_pipeline.index_pdf(
            file_source=file_source,
            filename=filename,
            custom_metadata=custom_metadata,
            force_reindex=force_reindex,
        )

    def query(
        self,
        question: str,
        document_id: Optional[str] = None,
        extra_filters: Optional[dict] = None,
        top_k: Optional[int] = None,
    ) -> QueryResult:
        """
        Ask a question over the indexed corpus.

        Returns a grounded answer with source citations. If retrieval confidence
        is below the configured threshold, returns a refusal instead of a
        potentially hallucinated answer.

        Args:
            question: The question to answer.
            document_id: Optional document ID to restrict retrieval to.
            extra_filters: Optional metadata filters for retrieval.
            top_k: Number of chunks to retrieve (overrides config default).

        Returns:
            QueryResult containing the answer and source citations.

        Raises:
            ValueError: If question is empty.
            EmbeddingError: If embedding the question fails.
            VectorStoreError: If retrieval fails.
            LLMError: If answer generation fails.
        """
        result: GeneratedAnswer = self.generation_service.ask(
            question=question,
            document_id=document_id,
            extra_filters=extra_filters,
            top_k=top_k,
        )

        return QueryResult(
            question=result.question,
            answer=result.answer,
            sources=result.sources,
            refused=result.refused,
            cited_indices=result.cited_indices,
        )

    def list_documents(self) -> List[Dict]:
        """
        List all indexed documents with chunk counts.

        Returns:
            List of dictionaries with document metadata and chunk counts.
        """
        return self.vector_store.list_documents()

    def delete_document(self, document_id: str) -> int:
        """
        Delete all chunks of a specific document.

        Args:
            document_id: The document ID to delete.

        Returns:
            Number of chunks deleted.
        """
        return self.vector_store.delete_document(document_id)

    def get_stats(self) -> Dict[str, any]:
        """
        Get statistics about the indexed corpus.

        Returns:
            Dictionary with collection name and total chunk count.
        """
        return {
            "collection": self.vector_store.settings.collection,
            "total_chunks": self.vector_store.count(),
        }
