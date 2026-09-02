"""
Domain exceptions for the document ingestion pipeline.

Raising typed exceptions (instead of letting low-level library errors leak)
lets callers react to specific failure modes without depending on PyMuPDF
internals.
"""


class DocumentIngestionError(Exception):
    """Base class for all document processing failures."""


class PDFParseError(DocumentIngestionError):
    """Raised when a PDF cannot be opened or parsed (corrupt or encrypted)."""


class NoTextExtractedError(DocumentIngestionError):
    """Raised when a PDF parses but no page contains extractable text."""


class EmbeddingError(Exception):
    """Base class for all embedding-related failures.

    Sub-raises distinguish auth issues, quota exhaustion, network problems,
    and malformed responses from the embedding service.
    """
