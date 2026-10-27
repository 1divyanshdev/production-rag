"""Offline tests for the retrieval service."""
import pytest

from backend.app.core.config import RetrievalSettings
from backend.app.core.exceptions import VectorStoreError
from backend.app.services.chunking_service import ChunkingService
from backend.app.services.ingestion_pipeline import IngestionPipeline
from backend.app.services.ingestion_service import DocumentIngestionService
from backend.app.services.retrieval_service import RetrievalService


@pytest.fixture
def indexed(fake_embedder, memory_store, make_pdf_bytes):
    """Index two distinct documents and return (pipeline, retrieval)."""
    pipeline = IngestionPipeline(
        ingestion=DocumentIngestionService(),
        chunker=ChunkingService(),
        embedder=fake_embedder,
        store=memory_store,
    )
    pipeline.index_pdf(
        make_pdf_bytes(["Vector search finds similar text using embeddings."]),
        filename="search.pdf",
    )
    pipeline.index_pdf(
        make_pdf_bytes(["Chocolate cake requires sugar, flour and cocoa."]),
        filename="recipes.pdf",
    )
    return pipeline, RetrievalService(fake_embedder, memory_store)


class TestRetrieve:
    def test_relevant_document_ranks_first(self, indexed, fake_embedder):
        _pipeline, retrieval = indexed

        hits = retrieval.retrieve("similar text using embeddings")

        assert hits[0].chunk.metadata.filename == "search.pdf"
        assert hits[0].score > hits[-1].score

    def test_top_k_limits_results(self, indexed):
        _pipeline, retrieval = indexed

        hits = retrieval.retrieve("embeddings text", top_k=1)

        assert len(hits) == 1

    def test_document_filter_restricts_scope(self, indexed):
        _pipeline, retrieval = indexed
        doc_id = None
        # find doc id of recipes.pdf via a search
        all_hits = retrieval.retrieve("cocoa sugar flour", top_k=10)
        for hit in all_hits:
            if hit.chunk.metadata.filename == "recipes.pdf":
                doc_id = hit.chunk.metadata.document_id
                break
        assert doc_id is not None

        hits = retrieval.retrieve("sugar flour cocoa", document_id=doc_id, top_k=10)
        assert all(h.chunk.metadata.document_id == doc_id for h in hits)
        assert all(h.chunk.metadata.filename == "recipes.pdf" for h in hits)

    def test_score_threshold_metadata_exposed(self, fake_embedder, memory_store):
        retrieval = RetrievalService(
            fake_embedder, memory_store, RetrievalSettings(top_k=3, score_threshold=0.5)
        )
        assert retrieval.settings.top_k == 3

    def test_empty_question_raises(self, indexed):
        _pipeline, retrieval = indexed
        with pytest.raises(ValueError):
            retrieval.retrieve("   ")

    def test_wrong_query_dimension_raises(self, fake_embedder, memory_store):
        store = memory_store
        store.search = store.search  # sanity
        retrieval = RetrievalService(fake_embedder, store)

        from backend.app.services.vector_store import QdrantVectorStore

        original = store.search

        def bad_dim_search(*args, **kwargs):
            kwargs["query_vector"] = [0.1] * 8
            return original(*args, **kwargs)

        store.search = bad_dim_search
        try:
            with pytest.raises(VectorStoreError):
                retrieval.retrieve("anything")
        finally:
            store.search = original
