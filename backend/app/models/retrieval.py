"""Retrieval models: scored search results."""
from typing import Any, Dict

from pydantic import BaseModel, Field

from backend.app.models.chunk import Chunk


class ScoredChunk(BaseModel):
    """A retrieved chunk paired with its similarity score from the vector
    store. Score is cosine similarity in [0, 1] for normalized vectors."""

    chunk: Chunk = Field(description="The retrieved chunk with full lineage")
    score: float = Field(description="Similarity score (cosine) for this hit")

    def to_citation(self) -> Dict[str, Any]:
        """Compact citation view for surfacing sources in answers."""
        meta = self.chunk.metadata
        return {
            "filename": meta.filename,
            "page_number": meta.page_number,
            "chunk_index": meta.chunk_index,
            "document_id": meta.document_id,
            "score": round(self.score, 4),
        }
