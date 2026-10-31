"""
Vector store service wrapping Qdrant.

Two operating modes (chosen via VectorStoreSettings):
  - local (default): embedded Qdrant persisted to a directory. No server,
    no Docker - suitable for development and this project's scale.
  - server: talks to a running Qdrant instance (Docker or Qdrant Cloud)
    when ``url`` is configured.

What is actually stored per point:
  - id: deterministic UUIDv5 derived from (document_id, chunk_index) so
    re-upserting the same document is idempotent (overwrite, not duplicate).
  - vector: the embedding of the chunk content (L2-normalized).
  - payload: the full serialized Chunk (content + lineage metadata), which
    enables metadata filtering and citation reconstruction.

Similarity: COSINE. Because embeddings are normalized, cosine similarity
equals dot product and scores land in [0, 1] for non-negative spaces.
"""
import logging
import uuid
from typing import List, Optional, Sequence

from qdrant_client import QdrantClient
from qdrant_client import models as qmodels

from backend.app.core.config import VectorStoreSettings
from backend.app.core.exceptions import VectorStoreError
from backend.app.models.chunk import Chunk
from backend.app.models.retrieval import ScoredChunk

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """Chunk vector store with upsert, dedup-aware search, and filtering."""

    def __init__(self, settings: VectorStoreSettings, dimension: int):
        self.settings = settings
        self.dimension = dimension
        try:
            if settings.url:
                self.client = QdrantClient(url=settings.url, api_key=settings.api_key or None)
            else:
                self.client = QdrantClient(path=settings.path)
        except Exception as exc:
            raise VectorStoreError(f"Could not initialize Qdrant client: {exc}") from exc
        self._ensure_collection()

    # -------- schema management --------

    def _ensure_collection(self) -> None:
        try:
            if not self.client.collection_exists(self.settings.collection):
                self.client.create_collection(
                    collection_name=self.settings.collection,
                    vectors_config=qmodels.VectorParams(
                        size=self.dimension,
                        distance=qmodels.Distance.COSINE,
                    ),
                )
                logger.info(
                    "Created Qdrant collection '%s' (dim=%d, cosine).",
                    self.settings.collection,
                    self.dimension,
                )
        except Exception as exc:
            raise VectorStoreError(
                f"Could not ensure collection '{self.settings.collection}': {exc}"
            ) from exc

    # -------- write path --------

    @staticmethod
    def point_id_for(chunk: Chunk) -> str:
        """
        Deterministic id derived from (file_hash, chunk_index) -> idempotent
        re-upserts even when a document is re-ingested with a fresh
        document_id. Identical files map to identical points.
        """
        raw = f"{chunk.metadata.file_hash}:{chunk.metadata.chunk_index}"
        return str(uuid.uuid5(uuid.NAMESPACE_URL, raw))

    def upsert_chunks(
        self, chunks: Sequence[Chunk], vectors: Sequence[Sequence[float]]
    ) -> int:
        """Upsert chunks with their embeddings. Returns number of points."""
        if len(chunks) != len(vectors):
            raise VectorStoreError(
                f"Chunk/vector count mismatch: {len(chunks)} vs {len(vectors)}."
            )
        if not chunks:
            return 0

        for chunk, vector in zip(chunks, vectors):
            if len(vector) != self.dimension:
                raise VectorStoreError(
                    f"Vector dimension {len(vector)} != collection "
                    f"dimension {self.dimension}. Re-embed with the "
                    "configured model or recreate the collection."
                )

        points = [
            qmodels.PointStruct(
                id=self.point_id_for(chunk),
                vector=list(vector),
                payload=chunk.to_dict(),
            )
            for chunk, vector in zip(chunks, vectors)
        ]
        try:
            self.client.upsert(collection_name=self.settings.collection, points=points)
        except Exception as exc:
            raise VectorStoreError(f"Qdrant upsert failed: {exc}") from exc

        logger.info("Upserted %d point(s) into '%s'.", len(points), self.settings.collection)
        return len(points)

    def document_exists(self, file_hash: str) -> bool:
        """True if any stored point carries this source file hash
        (ingestion-level deduplication)."""
        try:
            result = self.client.count(
                collection_name=self.settings.collection,
                count_filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="metadata.file_hash",
                            match=qmodels.MatchValue(value=file_hash),
                        )
                    ]
                ),
                exact=True,
            )
        except Exception as exc:
            raise VectorStoreError(f"Qdrant count failed: {exc}") from exc
        return result.count > 0

    # -------- read path --------

    def search(
        self,
        query_vector: Sequence[float],
        top_k: int = 5,
        document_id: Optional[str] = None,
        extra_filters: Optional[dict] = None,
    ) -> List[ScoredChunk]:
        """Nearest-neighbour search returning ScoredChunks.

        ``document_id`` restricts results to one source document;
        ``extra_filters`` matches exact payload values, e.g.
        {"metadata.extra.category": "contracts"}.
        """
        if len(query_vector) != self.dimension:
            raise VectorStoreError(
                f"Query vector dim {len(query_vector)} != {self.dimension}."
            )

        must = []
        if document_id is not None:
            must.append(
                qmodels.FieldCondition(
                    key="metadata.document_id",
                    match=qmodels.MatchValue(value=document_id),
                )
            )
        for key, value in (extra_filters or {}).items():
            must.append(
                qmodels.FieldCondition(key=key, match=qmodels.MatchValue(value=value))
            )

        query_filter = qmodels.Filter(must=must) if must else None

        try:
            response = self.client.query_points(
                collection_name=self.settings.collection,
                query=list(query_vector),
                limit=top_k,
                query_filter=query_filter,
                with_payload=True,
            )
        except Exception as exc:
            raise VectorStoreError(f"Qdrant search failed: {exc}") from exc

        scored: List[ScoredChunk] = []
        for point in response.points:
            payload = point.payload or {}
            try:
                chunk = Chunk.model_validate(payload)
            except Exception as exc:
                logger.warning("Skipping point %s with invalid payload: %s", point.id, exc)
                continue
            scored.append(ScoredChunk(chunk=chunk, score=float(point.score)))

        logger.info("Vector search returned %d hit(s).", len(scored))
        return scored

    def count(self) -> int:
        """Total number of stored chunk vectors."""
        try:
            return self.client.count(collection_name=self.settings.collection, exact=True).count
        except Exception as exc:
            raise VectorStoreError(f"Qdrant count failed: {exc}") from exc

    # -------- document management --------

    def list_documents(self) -> List[dict]:
        """Aggregate distinct source documents from stored payloads.

        Returns a list of dicts:
            {document_id, filename, file_hash, total_pages, chunk_count}
        """
        documents: dict = {}
        offset = None
        try:
            while True:
                points, offset = self.client.scroll(
                    collection_name=self.settings.collection,
                    limit=256,
                    with_payload=True,
                    offset=offset,
                )
                for point in points:
                    meta = (point.payload or {}).get("metadata", {}) or {}
                    doc_id = meta.get("document_id")
                    if not doc_id:
                        continue
                    if doc_id not in documents:
                        documents[doc_id] = {
                            "document_id": doc_id,
                            "filename": meta.get("filename"),
                            "file_hash": meta.get("file_hash"),
                            "total_pages": meta.get("total_pages"),
                            "chunk_count": 0,
                        }
                    documents[doc_id]["chunk_count"] += 1
                if offset is None:
                    break
        except Exception as exc:
            raise VectorStoreError(f"Qdrant scroll failed: {exc}") from exc
        return list(documents.values())

    def delete_document(self, document_id: str) -> int:
        """Delete every chunk belonging to a document. Returns count removed."""
        try:
            existing = self.client.count(
                collection_name=self.settings.collection,
                count_filter=qmodels.Filter(
                    must=[
                        qmodels.FieldCondition(
                            key="metadata.document_id",
                            match=qmodels.MatchValue(value=document_id),
                        )
                    ]
                ),
                exact=True,
            ).count
            if existing == 0:
                return 0
            self.client.delete(
                collection_name=self.settings.collection,
                points_selector=qmodels.FilterSelector(
                    filter=qmodels.Filter(
                        must=[
                            qmodels.FieldCondition(
                                key="metadata.document_id",
                                match=qmodels.MatchValue(value=document_id),
                            )
                        ]
                    )
                ),
            )
        except Exception as exc:
            raise VectorStoreError(f"Qdrant delete failed: {exc}") from exc
        logger.info("Deleted %d point(s) for document %s.", existing, document_id)
        return existing
