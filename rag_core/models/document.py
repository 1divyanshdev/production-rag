from datetime import datetime, timezone
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """
    Metadata attached to each ingested document page/chunk.
    Ensures strict typing and consistency across the pipeline.
    """
    document_id: str = Field(description="Unique ID (UUID) generated for the uploaded document")
    filename: str = Field(description="Original filename of the ingested document")
    file_type: str = Field(default="pdf", description="File extension/MIME type")
    file_hash: str = Field(description="SHA-256 hash of the binary file content for deduplication")
    file_size_bytes: int = Field(description="Size of the raw document file in bytes")
    page_number: int = Field(description="1-indexed page number of this specific document content")
    total_pages: int = Field(description="Total number of pages in the parent document")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of ingestion"
    )
    extra: Dict[str, Any] = Field(default_factory=dict, description="Custom metadata fields if needed")


class Document(BaseModel):
    """
    Standardized internal document object representation.
    Serves as the output of ingestion and input to chunking.
    """
    page_content: str = Field(description="Extracted clean text content of the page")
    metadata: DocumentMetadata = Field(description="Associated metadata for lineage and citation")

    def to_dict(self) -> Dict[str, Any]:
        """Convert Document model to standard dictionary for serialization."""
        return self.model_dump()
