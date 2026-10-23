"""Pydantic request/response schemas for the RAG API."""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(description="'ok' when the API is reachable")
    version: str = Field(description="API version")


class IndexResponse(BaseModel):
    filename: str
    indexed_chunks: int = Field(description="Number of chunk vectors stored")
    skipped_duplicate: bool = Field(
        description="True when the file hash was already indexed"
    )
    document_id: Optional[str] = None


class AskRequest(BaseModel):
    question: str = Field(min_length=1, description="Natural-language question")
    document_id: Optional[str] = Field(
        default=None, description="Restrict the answer to one indexed document"
    )
    extra_filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description='Exact payload filters, e.g. {"metadata.extra.category": "contracts"}',
    )
    top_k: Optional[int] = Field(
        default=None, ge=1, le=50, description="Override number of retrieved chunks"
    )


class SourceCitation(BaseModel):
    filename: str
    page_number: int
    chunk_index: int
    document_id: str
    score: float


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceCitation] = Field(default_factory=list)
    refused: bool = Field(
        description="True when retrieval confidence was too low to answer"
    )
    cited_indices: List[int] = Field(
        description="[n] markers found in the answer text"
    )


class StatsResponse(BaseModel):
    collection: str
    total_chunks: int


class DocumentSummary(BaseModel):
    document_id: str
    filename: str
    file_hash: str
    total_pages: int
    chunk_count: int


class DeleteResponse(BaseModel):
    document_id: str
    deleted_chunks: int
