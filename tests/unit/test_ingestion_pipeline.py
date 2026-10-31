"""Offline tests for the ingestion -> chunk -> embed -> index pipeline."""
import pytest

from rag_core.chunking import ChunkingService
from rag_core.ingestion import IngestionPipeline
from rag_core.ingestion.ingestion_service import DocumentIngestionService


@pytest.fixture
def pipeline(fake_embedder, memory_store):
    return IngestionPipeline(
        ingestion=DocumentIngestionService(),
        chunker=ChunkingService(),
        embedder=fake_embedder,
        store=memory_store,
    )


class TestIndexing:
    def test_index_pdf_end_to_end(self, pipeline, make_pdf_bytes, memory_store):
        data = make_pdf_bytes(["First page about vector search.", "Second page about citations."])

        result = pipeline.index_pdf(data, filename="doc.pdf")

        assert result.skipped_duplicate is False
        assert result.indexed_chunks >= 2
        assert result.document_id is not None
        assert memory_store.count() == result.indexed_chunks

    def test_duplicate_hash_is_skipped(self, pipeline, make_pdf_bytes, memory_store):
        data = make_pdf_bytes(["Same file content."])

        first = pipeline.index_pdf(data, filename="a.pdf")
        second = pipeline.index_pdf(data, filename="b.pdf")

        assert first.skipped_duplicate is False
        assert second.skipped_duplicate is True
        assert second.indexed_chunks == 0
        assert memory_store.count() == first.indexed_chunks

    def test_force_reindex_overwrites_not_duplicates(
        self, pipeline, make_pdf_bytes, memory_store
    ):
        data = make_pdf_bytes(["Forced reindex content."])
        first = pipeline.index_pdf(data, filename="a.pdf")
        second = pipeline.index_pdf(data, filename="a.pdf", force_reindex=True)

        assert second.skipped_duplicate is False
        assert memory_store.count() == first.indexed_chunks

    def test_invalid_pdf_propagates_error(self, pipeline):
        from rag_core.exceptions import PDFParseError

        with pytest.raises(PDFParseError):
            pipeline.index_pdf(b"not a pdf", filename="bad.pdf")


class TestIndexedContentIsSearchable:
    def test_indexed_document_is_retrievable(self, pipeline, make_pdf_bytes, fake_embedder):
        from rag_core.retrieval import RetrievalService

        data = make_pdf_bytes(["Qdrant stores chunk embeddings for retrieval."])
        pipeline.index_pdf(data, filename="kb.pdf")

        retrieval = RetrievalService(fake_embedder, pipeline.store)
        hits = retrieval.retrieve("chunk embeddings retrieval")

        assert len(hits) >= 1
        assert "Qdrant" in hits[0].chunk.content
        assert hits[0].chunk.metadata.filename == "kb.pdf"
