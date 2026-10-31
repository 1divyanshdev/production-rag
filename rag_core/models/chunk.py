"""Chunk models: the atomic retrieval units produced by the chunking stage."""
from datetime import datetime, timezone
from typing import Dict, Any

from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    """
    Metadata attached to each chunk.

    Identity fields are inherited from the source Document so a chunk can
    always be traced back to its origin file and page (required for citations).
    """
    document_id: str = Field(description="UUID of the parent document (inherited)")
    filename: str = Field(description="Original filename of the parent document")
    file_type: str = Field(default="pdf", description="File extension/MIME type")
    file_hash: str = Field(description="SHA-256 hash of the parent document (inherited)")
    page_number: int = Field(description="1-indexed page this chunk originated from")
    total_pages: int = Field(description="Total pages in the parent document")
    chunk_index: int = Field(
        description="0-indexed position of this chunk within the whole document"
    )
    total_chunks: int = Field(description="Total chunks produced for the parent document")
    start_offset: int = Field(
        description="Character offset of this chunk in the source page text (inclusive)"
    )
    end_offset: int = Field(
        description="Character offset of this chunk in the source page text (exclusive)"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of chunk creation",
    )
    extra: Dict[str, Any] = Field(
        default_factory=dict,
        description="Custom metadata propagated from the parent document",
    )


class Chunk(BaseModel):
    """
    Standardized retrieval unit: a coherent span of text plus full lineage.
    Serves as the output of chunking and input to embedding.
    """
    content: str = Field(description="Chunk text (may include overlap from the previous chunk)")
    metadata: ChunkMetadata = Field(description="Lineage and positioning metadata")

    def to_dict(self) -> Dict[str, Any]:
        """Convert Chunk model to standard dictionary for serialization."""
        return self.model_dump()
