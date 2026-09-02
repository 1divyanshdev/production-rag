"""
Chunking service: converts page-level Documents into retrievable Chunks.

Strategy (v1): each page is chunked independently, so a chunk's page_number
is always exact. Chunk indices are assigned document-globally in reading
order, and identity/metadata fields are inherited from the source Document.
"""
import logging
from typing import Dict, List, Optional, Sequence

from backend.app.models.chunk import Chunk, ChunkMetadata
from backend.app.models.document import Document
from backend.app.services.text_splitter import RecursiveTextSplitter

logger = logging.getLogger(__name__)


class ChunkingService:
    """Fan-out stage of the pipeline: many chunks out per page in."""

    def __init__(self, splitter: Optional[RecursiveTextSplitter] = None):
        self.splitter = splitter or RecursiveTextSplitter()

    def chunk_documents(self, documents: Sequence[Document]) -> List[Chunk]:
        """
        Chunk a batch of Documents (typically all pages of one file).

        Args:
            documents: Page-level documents from the ingestion service.

        Returns:
            List[Chunk]: ordered by document, then reading order within pages.
                ``chunk_index`` runs over the whole document; ``total_chunks``
                counts that document's chunks.

        Raises:
            ValueError: If a list item is not a Document instance.
        """
        if not documents:
            return []

        # Group pages per parent document, preserving input order.
        grouped: Dict[str, List[Document]] = {}
        for document in documents:
            if not isinstance(document, Document):
                raise ValueError(
                    f"Expected Document instances, got {type(document).__name__}."
                )
            grouped.setdefault(document.metadata.document_id, []).append(document)

        chunks: List[Chunk] = []
        for document_id, pages in grouped.items():
            chunks.extend(self._chunk_single_document(pages))
        return chunks

    def _chunk_single_document(self, pages: Sequence[Document]) -> List[Chunk]:
        # First pass: split every page, collecting (content, source_page, span).
        staged: List[tuple] = []
        for page in pages:
            if not page.page_content.strip():
                logger.warning(
                    "Skipping page %d of '%s': no text content to chunk.",
                    page.metadata.page_number,
                    page.metadata.filename,
                )
                continue

            pieces = self.splitter.split_text_with_offsets(page.page_content)
            for piece in pieces:
                staged.append((piece.text, page, piece.start, piece.end))

        total_chunks = len(staged)
        chunks: List[Chunk] = []
        for chunk_index, (content, page, start, end) in enumerate(staged):
            source_meta = page.metadata
            metadata = ChunkMetadata(
                document_id=source_meta.document_id,
                filename=source_meta.filename,
                file_type=source_meta.file_type,
                file_hash=source_meta.file_hash,
                page_number=source_meta.page_number,
                total_pages=source_meta.total_pages,
                chunk_index=chunk_index,
                total_chunks=total_chunks,
                start_offset=start,
                end_offset=end,
                extra=dict(source_meta.extra),
            )
            chunks.append(Chunk(content=content, metadata=metadata))

        if chunks:
            logger.info(
                "Chunked '%s': %d page(s) -> %d chunk(s).",
                pages[0].metadata.filename,
                len(pages),
                total_chunks,
            )
        return chunks
