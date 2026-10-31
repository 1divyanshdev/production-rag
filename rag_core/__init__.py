"""
Production RAG - A production-ready RAG library.

This package provides reusable components for building Retrieval-Augmented
Generation systems with document ingestion, chunking, embedding, vector storage,
retrieval, and grounded answer generation.

Public API:
    - RAGPipeline: Main orchestrator for RAG operations
    - RAGConfig: Configuration dataclass
    - QueryResult: Query response with answer and citations
    - IndexingResult: Document indexing result

Basic Usage:
    ```python
    from rag_core import RAGPipeline, RAGConfig

    # Initialize with environment-based config
    config = RAGConfig()
    rag = RAGPipeline(config=config)

    # Index a document
    result = rag.index_document("document.pdf")

    # Query the corpus
    answer = rag.query("What is the main topic?")
    print(answer.answer)
    ```

For advanced usage, configuration, and provider details, see the documentation.
"""

from rag_core.config import (
    EmbeddingSettings,
    LLMSettings,
    RetrievalSettings,
    VectorStoreSettings,
)
from rag_core.exceptions import (
    DocumentIngestionError,
    EmbeddingError,
    LLMError,
    NoTextExtractedError,
    PDFParseError,
    VectorStoreError,
)
from rag_core.generation import GeneratedAnswer
from rag_core.ingestion import IndexingResult
from rag_core.models import Chunk, ChunkMetadata, Document, DocumentMetadata, ScoredChunk
from rag_core.pipeline import RAGConfig, RAGPipeline, QueryResult

__version__ = "0.1.0"

__all__ = [
    # Main public API
    "RAGPipeline",
    "RAGConfig",
    "QueryResult",
    # Configuration
    "EmbeddingSettings",
    "LLMSettings",
    "RetrievalSettings",
    "VectorStoreSettings",
    # Results and models
    "IndexingResult",
    "GeneratedAnswer",
    "Chunk",
    "ChunkMetadata",
    "Document",
    "DocumentMetadata",
    "ScoredChunk",
    # Exceptions
    "DocumentIngestionError",
    "PDFParseError",
    "NoTextExtractedError",
    "EmbeddingError",
    "VectorStoreError",
    "LLMError",
]
