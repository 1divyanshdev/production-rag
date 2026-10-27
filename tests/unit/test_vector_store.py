"""Offline tests for the Qdrant vector store (local :memory: mode)."""
import pytest

from backend.app.core.config import VectorStoreSettings
from backend.app.core.exceptions import VectorStoreError
from backend.app.models.chunk import Chunk, ChunkMetadata
from backend.app.services.vector_store import QdrantVectorStore


def make_chunk(content, page_number=1, document_id="doc-1", chunk_index=0,
               filename="f.pdf", file_hash="ab" * 32):
    meta = ChunkMetadata(
        document_id=document_id,
        filename=filename,
        file_hash=file_hash,
        file_size_bytes=100,
        page_number=page_number,
        total_pages=2,
        chunk_index=chunk_index,
        total_chunks=4,
        start_offset=0,
        end_offset=len(content),
        extra={"category": "docs"},
    )
    return Chunk(content=content, metadata=meta)


@pytest.fixture
def store(fake_embedder):
    return QdrantVectorStore(
        VectorStoreSettings(path=":memory:"), dimension=fake_embedder.dimension
    )


class TestUpsertAndSearch:
    def test_roundtrip_finds_own_content(self, store, fake_embedder):
        chunks = [make_chunk("vector databases store embeddings")]
        vectors = fake_embedder.embed_documents([c.content for c in chunks])
        assert store.upsert_chunks(chunks, vectors) == 1

        qv = fake_embedder.embed_query("vector databases store embeddings")
        hits = store.search(qv, top_k=1)

        assert len(hits) == 1
        assert hits[0].chunk.content == chunks[0].content
        assert hits[0].score > 0.99  # cosine of identical normalized vectors

    def test_relevant_outranks_irrelevant(self, store, fake_embedder):
        chunks = [
            make_chunk("embedding vectors power semantic search", chunk_index=0),
            make_chunk("the recipe needs two cups of flour", chunk_index=1),
        ]
        vectors = fake_embedder.embed_documents([c.content for c in chunks])
        store.upsert_chunks(chunks, vectors)

        hits = store.search(fake_embedder.embed_query("semantic search embeddings"))

        assert "semantic search" in hits[0].chunk.content
        assert hits[0].score > hits[1].score

    def test_reupsert_same_chunk_is_idempotent(self, store, fake_embedder):
        chunk = make_chunk("deterministic id chunk")
        vec = fake_embedder.embed_documents([chunk.content])
        store.upsert_chunks(chunk and [chunk], vec)
        store.upsert_chunks([chunk], vec)
        assert store.count() == 1

    def test_payload_roundtrip_preserves_lineage(self, store, fake_embedder):
        chunk = make_chunk("lineage check", page_number=2, chunk_index=3)
        store.upsert_chunks([chunk], fake_embedder.embed_documents([chunk.content]))

        hit = store.search(fake_embedder.embed_query("lineage check"))[0]
        assert hit.chunk.metadata.page_number == 2
        assert hit.chunk.metadata.chunk_index == 3
        assert hit.chunk.metadata.extra == {"category": "docs"}


class TestValidation:
    def test_count_mismatch_raises(self, store, fake_embedder):
        chunks = [make_chunk("a"), make_chunk("b")]
        vectors = fake_embedder.embed_documents(["a"])
        with pytest.raises(VectorStoreError, match="mismatch"):
            store.upsert_chunks(chunks, vectors)

    def test_wrong_dimension_raises(self, store):
        with pytest.raises(VectorStoreError, match="[Dd]imension"):
            store.upsert_chunks([make_chunk("x")], [[0.1] * 8])

    def test_wrong_query_dimension_raises(self, store):
        with pytest.raises(VectorStoreError, match="dim"):
            store.search([0.1] * 8)

    def test_empty_upsert_is_noop(self, store):
        assert store.upsert_chunks([], []) == 0


class TestDedupAndFilters:
    def test_document_exists_by_hash(self, store, fake_embedder):
        chunk = make_chunk("hashable content", file_hash="cd" * 32)
        store.upsert_chunks([chunk], fake_embedder.embed_documents([chunk.content]))

        assert store.document_exists("cd" * 32) is True
        assert store.document_exists("ef" * 32) is False

    def test_filter_by_document_id(self, store, fake_embedder):
        chunks = [
            make_chunk("alpha document text", document_id="doc-a", chunk_index=0),
            make_chunk("alpha document text", document_id="doc-b", chunk_index=0),
        ]
        vectors = fake_embedder.embed_documents([c.content for c in chunks])
        store.upsert_chunks(chunks, vectors)

        hits = store.search(
            fake_embedder.embed_query("alpha document text"),
            top_k=10,
            document_id="doc-b",
        )
        assert len(hits) == 1
        assert hits[0].chunk.metadata.document_id == "doc-b"

    def test_filter_by_extra_metadata(self, store, fake_embedder):
        contract = make_chunk("payment terms apply", chunk_index=0)
        contract.metadata.extra = {"category": "contracts"}
        letter = make_chunk("payment terms apply", chunk_index=1)
        letter.metadata.extra = {"category": "letters"}
        store.upsert_chunks(
            [contract, letter],
            fake_embedder.embed_documents([c.content for c in (contract, letter)]),
        )

        hits = store.search(
            fake_embedder.embed_query("payment terms"),
            top_k=10,
            extra_filters={"metadata.extra.category": "letters"},
        )
        assert len(hits) == 1
        assert hits[0].chunk.metadata.extra["category"] == "letters"


class TestPointIds:
    def test_point_id_deterministic(self):
        chunk = make_chunk("same")
        assert (
            QdrantVectorStore.point_id_for(chunk)
            == QdrantVectorStore.point_id_for(make_chunk("same"))
        )

    def test_point_id_differs_per_chunk_index(self):
        assert QdrantVectorStore.point_id_for(
            make_chunk("x", chunk_index=0)
        ) != QdrantVectorStore.point_id_for(make_chunk("x", chunk_index=1))


class TestDocumentManagement:
    def test_list_documents_aggregates_distinct_sources(
        self, store, fake_embedder
    ):
        chunks = [
            make_chunk("doc a part one", document_id="doc-a", chunk_index=0,
                       filename="a.pdf", file_hash="aa" * 32),
            make_chunk("doc a part two", document_id="doc-a", chunk_index=1,
                       filename="a.pdf", file_hash="aa" * 32),
            make_chunk("doc b part one", document_id="doc-b", chunk_index=0,
                       filename="b.pdf", file_hash="bb" * 32),
        ]
        vectors = fake_embedder.embed_documents([c.content for c in chunks])
        store.upsert_chunks(chunks, vectors)

        docs = store.list_documents()

        assert {d["document_id"] for d in docs} == {"doc-a", "doc-b"}
        by_id = {d["document_id"]: d for d in docs}
        assert by_id["doc-a"]["chunk_count"] == 2
        assert by_id["doc-a"]["filename"] == "a.pdf"
        assert by_id["doc-b"]["chunk_count"] == 1

    def test_list_documents_empty_index(self, store):
        assert store.list_documents() == []

    def test_delete_document_removes_only_target(self, store, fake_embedder):
        chunks = [
            make_chunk("keep me", document_id="doc-a", chunk_index=0,
                       file_hash="aa" * 32),
            make_chunk("drop me", document_id="doc-b", chunk_index=0,
                       file_hash="bb" * 32),
        ]
        vectors = fake_embedder.embed_documents([c.content for c in chunks])
        store.upsert_chunks(chunks, vectors)

        deleted = store.delete_document("doc-b")

        assert deleted == 1
        assert store.count() == 1
        assert {d["document_id"] for d in store.list_documents()} == {"doc-a"}

    def test_delete_unknown_document_returns_zero(self, store):
        assert store.delete_document("ghost-id") == 0

    def test_delete_is_repeatable(self, store, fake_embedder):
        chunk = make_chunk("once", document_id="doc-a", chunk_index=0)
        store.upsert_chunks([chunk], fake_embedder.embed_documents([chunk.content]))

        assert store.delete_document("doc-a") == 1
        assert store.delete_document("doc-a") == 0
