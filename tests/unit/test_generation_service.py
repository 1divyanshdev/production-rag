"""Offline tests for the generation service (grounded RAG answers)."""
import pytest

from rag_core.config import RetrievalSettings
from rag_core.chunking import ChunkingService
from rag_core.generation.generation_service import (
    REFUSAL_ANSWER,
    GenerationService,
    GeneratedAnswer,
)
from rag_core.ingestion import IngestionPipeline
from rag_core.ingestion.ingestion_service import DocumentIngestionService
from rag_core.retrieval import RetrievalService


def _pdf_bytes(text):
    import pymupdf

    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), text)
    data = doc.tobytes()
    doc.close()
    return data


@pytest.fixture
def gen(fake_embedder, memory_store, fake_llm):
    pipeline = IngestionPipeline(
        ingestion=DocumentIngestionService(),
        chunker=ChunkingService(),
        embedder=fake_embedder,
        store=memory_store,
    )
    pipeline.index_pdf(
        _pdf_bytes(
            "Reranking improves retrieval precision by reordering candidate chunks."
        ),
        filename="kb.pdf",
    )
    retrieval = RetrievalService(
        fake_embedder, pipeline.store,
        RetrievalSettings(top_k=5, score_threshold=0.2),
    )
    return GenerationService(retrieval, fake_llm), fake_llm


class TestGroundedAnswers:
    def test_answer_with_sources(self, gen):
        service, _fake_llm = gen

        result = service.ask("How does reranking help retrieval precision?")

        assert isinstance(result, GeneratedAnswer)
        assert result.refused is False
        assert len(result.answer) > 0
        assert len(result.sources) >= 1
        assert result.sources[0]["filename"] == "kb.pdf"
        assert result.sources[0]["page_number"] == 1

    def test_llm_receives_numbered_context_with_provenance(self, gen):
        service, fake_llm = gen
        service.ask("reranking precision")
        system_prompt, user_prompt = fake_llm.calls[0]

        assert "context passages" in user_prompt.lower()
        assert "[1] (source: kb.pdf, page 1)" in user_prompt
        assert "only using the numbered context" in system_prompt.lower()
        assert "[1] or [2][4]" in system_prompt

    def test_cited_indices_parsed_from_answer(self, gen, fake_llm):
        service, _ = gen
        fake_llm.canned_answer = "Sources [1] and [3] confirm this. [3]"
        result = service.ask("reranking")

        assert result.cited_indices == [1, 3]

    def test_answer_without_citations_has_empty_cited_indices(self, gen, fake_llm):
        service, _ = gen
        fake_llm.canned_answer = "A plain answer with no markers."
        result = service.ask("reranking")

        assert result.cited_indices == []


class TestLowConfidenceRefusal:
    def test_refusal_when_index_empty(self, fake_embedder, memory_store, fake_llm):
        retrieval = RetrievalService(
            fake_embedder, memory_store,
            RetrievalSettings(top_k=5, score_threshold=0.2),
        )
        service = GenerationService(retrieval, fake_llm)

        result = service.ask("anything at all")

        assert result.refused is True
        assert result.answer == REFUSAL_ANSWER
        assert result.sources == []
        assert fake_llm.calls == []  # LLM never called on refusal

    def test_refusal_when_threshold_not_met(
        self, fake_embedder, memory_store, fake_llm
    ):
        pipeline = IngestionPipeline(
            DocumentIngestionService(), ChunkingService(), fake_embedder, memory_store
        )
        pipeline.index_pdf(
            _pdf_bytes("Chocolate cake requires sugar, flour and cocoa."),
            filename="recipes.pdf",
        )
        retrieval = RetrievalService(
            fake_embedder, memory_store,
            RetrievalSettings(top_k=5, score_threshold=0.99),
        )
        service = GenerationService(retrieval, fake_llm)

        result = service.ask("quantum physics equations")

        assert result.refused is True
        assert fake_llm.calls == []
