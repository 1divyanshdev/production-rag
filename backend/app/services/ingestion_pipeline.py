"""
Ingestion pipeline: the full indexing flow in one orchestrator.

    PDF (path/bytes) -> parse -> chunks -> embeddings -> Qdrant

Deduplication: if the file hash was indexed before, the document is
skipped entirely (idempotent re-indexing). Point ids are deterministic,
so even a forced re-index overwrites rather than duplicates.
"""
import logging
from typing import List, Optional, Union

from backend.app.core.exceptions import EmbeddingError, VectorStoreError
from backend.app.models.chunk import Chunk
from backend.app.services.chunking_service import ChunkingService
from backend.app.services.embeddings.base import EmbeddingProvider
from backend.app.services.ingestion_service import DocumentIngestionService
from backend.app.services.vector_store import QdrantVectorStore

logger = logging.getLogger(__name__)


class IndexingResult:
    """Summary of one indexing run."""

    def __init__(
        self,
        filename: str,
        indexed_chunks: int,
        skipped_duplicate: bool,
        document_id: Optional[str] = None,
    ):
        self.filename = filename
        self.indexed_chunks = indexed_chunks
        self.skipped_duplicate = skipped_duplicate
        self.document_id = document_id

    def __repr__(self) -> str:  # pragma: no cover - debug convenience
        return (
            f"IndexingResult(filename={self.filename!r}, "
            f"indexed_chunks={self.indexed_chunks}, "
            f"skipped_duplicate={self.skipped_duplicate})"
        )


class IngestionPipeline:
    """End-to-end document indexing."""

    def __init__(
        self,
        ingestion: DocumentIngestionService,
        chunker: ChunkingService,
        embedder: EmbeddingProvider,
        store: QdrantVectorStore,
    ):
        self.ingestion = ingestion
        self.chunker = chunker
        self.embedder = embedder
        self.store = store

    def index_pdf(
        self,
        file_source: Union[str, bytes],
        filename: Optional[str] = None,
        custom_metadata: Optional[dict] = None,
        force_reindex: bool = False,
    ) -> IndexingResult:
        """Ingest, chunk, embed and store a PDF.

        Raises:
            FileNotFoundError, ValueError: invalid input (from ingestion).
            PDFParseError / NoTextExtractedError: unusable PDF content.
            EmbeddingError: embedding provider failure.
            VectorStoreError: storage failure.
        """
        documents = self.ingestion.ingest_pdf(
            file_source, filename=filename, custom_metadata=custom_metadata
        )
        fname = documents[0].metadata.filename
        file_hash = documents[0].metadata.file_hash

        if not force_reindex and self.store.document_exists(file_hash):
            logger.info("'%s' already indexed (hash %s...); skipping.", fname, file_hash[:12])
            return IndexingResult(
                filename=fname, indexed_chunks=0, skipped_duplicate=True
            )

        chunks: List[Chunk] = self.chunker.chunk_documents(documents)
        if not chunks:
            raise VectorStoreError(f"'{fname}' produced no chunks to index.")

        vectors = self.embedder.embed_documents([c.content for c in chunks])
        self.store.upsert_chunks(chunks, vectors)

        logger.info("Indexed '%s': %d chunk(s).", fname, len(chunks))
        return IndexingResult(
            filename=fname,
            indexed_chunks=len(chunks),
            skipped_duplicate=False,
            document_id=chunks[0].metadata.document_id,
        )
