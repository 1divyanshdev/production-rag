import hashlib
import logging
import uuid
from typing import List, Union, Optional
from pathlib import Path

from rag_core.exceptions import NoTextExtractedError
from rag_core.models.document import Document, DocumentMetadata
from rag_core.ingestion.pdf_parser import PDFParser

logger = logging.getLogger(__name__)


class DocumentIngestionService:
    """
    Orchestration service for document ingestion.
    Coordinates file processing, hashing, metadata generation, and page extraction.
    """

    def __init__(self):
        self.pdf_parser = PDFParser()

    def ingest_pdf(
        self,
        file_source: Union[str, Path, bytes],
        filename: Optional[str] = None,
        custom_metadata: Optional[dict] = None
    ) -> List[Document]:
        """
        Main entry point for ingesting a PDF document.

        Args:
            file_source: Path to PDF file or raw bytes.
            filename: Name of the file (required if file_source is bytes).
            custom_metadata: Optional dict of custom metadata tags to append.

        Returns:
            List[Document]: Standardized internal document objects, one per
            page that yielded extractable text. Pages without text are
            skipped (logged as warnings).

        Raises:
            FileNotFoundError: If a path-based source does not exist.
            ValueError: If inputs are missing or of the wrong type.
            PDFParseError: If the underlying PDF cannot be parsed.
            NoTextExtractedError: If no page of the document contains text
                (typical for scanned/image-only PDFs).
        """
        # Resolve raw bytes and filename
        if isinstance(file_source, (str, Path)):
            path = Path(file_source)
            if not path.exists():
                raise FileNotFoundError(f"File not found at path: {file_source}")
            
            filename = filename or path.name
            with open(path, "rb") as f:
                file_bytes = f.read()
        elif isinstance(file_source, bytes):
            if not filename:
                raise ValueError("filename must be provided when file_source is raw bytes.")
            file_bytes = file_source
        else:
            raise ValueError("file_source must be a file path or raw bytes.")

        file_size_bytes = len(file_bytes)
        file_hash = self._compute_sha256(file_bytes)
        document_id = str(uuid.uuid4())

        # Parse text page by page
        pages_content, total_pages = self.pdf_parser.parse_pdf(file_bytes)

        # Build Document objects, skipping pages that yielded no extractable text
        documents: List[Document] = []
        skipped_pages: List[int] = []
        for page_data in pages_content:
            if not page_data["text"]:
                skipped_pages.append(page_data["page_number"])
                continue

            metadata = DocumentMetadata(
                document_id=document_id,
                filename=filename,
                file_type="pdf",
                file_hash=file_hash,
                file_size_bytes=file_size_bytes,
                page_number=page_data["page_number"],
                total_pages=total_pages,
                extra=custom_metadata or {}
            )

            doc = Document(
                page_content=page_data["text"],
                metadata=metadata
            )
            documents.append(doc)

        if not documents:
            raise NoTextExtractedError(
                f"No extractable text in '{filename}' ({total_pages} page(s)). "
                "The document may be scanned/image-only."
            )

        if skipped_pages:
            logger.warning(
                "Skipped %d page(s) without text in '%s': %s",
                len(skipped_pages), filename, skipped_pages,
            )

        logger.info(
            "Ingested '%s' (%d bytes, sha256:%s): %d/%d pages kept.",
            filename, file_size_bytes, file_hash[:12], len(documents), total_pages,
        )

        return documents

    @staticmethod
    def _compute_sha256(file_bytes: bytes) -> str:
        """Computes SHA-256 hash of binary content for tracking and deduplication."""
        return hashlib.sha256(file_bytes).hexdigest()
