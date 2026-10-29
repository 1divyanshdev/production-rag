"""
Tests for the public RAG library API.

These tests verify that the library can be used independently without
FastAPI and that the public API is stable and well-behaved.
"""
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from rag_core import (
    RAGConfig,
    RAGPipeline,
    QueryResult,
    EmbeddingSettings,
    VectorStoreSettings,
    LLMSettings,
    RetrievalSettings,
)
from rag_core.exceptions import EmbeddingError, PDFParseError


class TestRAGConfigInitialization:
    """Test configuration loading and validation."""

    def test_default_config_loads_from_environment(self, monkeypatch):
        """RAGConfig should load defaults from environment when not specified."""
        monkeypatch.setenv("EMBEDDING_API_KEY", "test-key")
        monkeypatch.setenv("LLM_API_KEY", "llm-key")
        monkeypatch.setenv("LLM_BASE_URL", "http://test")
        monkeypatch.setenv("LLM_MODEL", "test-model")
        
        config = RAGConfig()
        
        assert config.embedding_settings is not None
        assert config.vector_store_settings is not None
        assert config.llm_settings is not None
        assert config.retrieval_settings is not None

    def test_explicit_settings_override_environment(self, monkeypatch):
        """Explicit settings should take precedence over environment."""
        monkeypatch.setenv("EMBEDDING_API_KEY", "env-key")
        
        custom_embedding = EmbeddingSettings(api_key="explicit-key")
        config = RAGConfig(embedding_settings=custom_embedding)
        
        assert config.embedding_settings.api_key == "explicit-key"

    def test_config_with_all_explicit_settings(self):
        """All settings can be provided explicitly."""
        config = RAGConfig(
            embedding_settings=EmbeddingSettings(api_key="emb-key"),
            vector_store_settings=VectorStoreSettings(path="./test_store"),
            llm_settings=LLMSettings(api_key="llm-key", base_url="http://test", model="test"),
            retrieval_settings=RetrievalSettings(top_k=10, score_threshold=0.5),
        )
        
        assert config.embedding_settings.api_key == "emb-key"
        assert config.vector_store_settings.path == "./test_store"
        assert config.llm_settings.api_key == "llm-key"
        assert config.retrieval_settings.top_k == 10


class TestRAGPipelineInitialization:
    """Test pipeline construction and component initialization."""

    def test_pipeline_initializes_with_default_config(self, fake_embedding_provider, tmp_path):
        """Pipeline should initialize successfully with default config."""
        config = RAGConfig(
            embedding_settings=EmbeddingSettings(api_key="test", dimension=128),
            vector_store_settings=VectorStoreSettings(path=str(tmp_path / "qdrant")),
        )
        
        with patch("rag_core.pipeline.get_embedding_provider", return_value=fake_embedding_provider):
            pipeline = RAGPipeline(config=config)
            
            assert pipeline.embedder is not None
            assert pipeline.vector_store is not None
            assert pipeline.ingestion_pipeline is not None
            assert pipeline.retrieval_service is not None

    def test_pipeline_initializes_without_config(self, monkeypatch, fake_embedding_provider, tmp_path):
        """Pipeline should work with environment-based config."""
        monkeypatch.setenv("EMBEDDING_API_KEY", "test-key")
        monkeypatch.setenv("VECTOR_STORE_PATH", str(tmp_path / "qdrant"))
        
        with patch("rag_core.pipeline.get_embedding_provider", return_value=fake_embedding_provider):
            pipeline = RAGPipeline()
            
            assert pipeline.config is not None
            assert pipeline.embedder is not None

    def test_llm_provider_lazy_initialization(self, fake_embedding_provider, tmp_path, monkeypatch):
        """LLM provider should only initialize when needed."""
        config = RAGConfig(
            embedding_settings=EmbeddingSettings(api_key="test", dimension=128),
            vector_store_settings=VectorStoreSettings(path=str(tmp_path / "qdrant")),
            llm_settings=LLMSettings(api_key="llm", base_url="http://test", model="test"),
        )
        
        with patch("rag_core.pipeline.get_embedding_provider", return_value=fake_embedding_provider):
            pipeline = RAGPipeline(config=config)
            
            # LLM provider should not be initialized yet
            assert pipeline._llm_provider is None
            
            # Accessing the property should initialize it
            llm = pipeline.llm_provider
            assert llm is not None
            assert pipeline._llm_provider is not None


class TestIndexingAPI:
    """Test document indexing through the public API."""

    def test_index_document_from_path(self, pipeline_with_mocks, sample_pdf_path):
        """Should index a document from a file path."""
        pipeline = pipeline_with_mocks
        
        result = pipeline.index_document(sample_pdf_path)
        
        assert result.filename == "sample.pdf"
        assert result.indexed_chunks > 0
        assert not result.skipped_duplicate

    def test_index_document_from_bytes(self, pipeline_with_mocks, sample_pdf_bytes):
        """Should index a document from raw bytes with filename."""
        pipeline = pipeline_with_mocks
        
        result = pipeline.index_document(sample_pdf_bytes, filename="test.pdf")
        
        assert result.filename == "test.pdf"
        assert result.indexed_chunks > 0

    def test_index_document_duplicate_skipped(self, pipeline_with_mocks, sample_pdf_path):
        """Should skip duplicate documents based on hash."""
        pipeline = pipeline_with_mocks
        
        # Index once
        result1 = pipeline.index_document(sample_pdf_path)
        assert not result1.skipped_duplicate
        
        # Index again - should skip
        result2 = pipeline.index_document(sample_pdf_path)
        assert result2.skipped_duplicate
        assert result2.indexed_chunks == 0

    def test_index_document_force_reindex(self, pipeline_with_mocks, sample_pdf_path):
        """Should reindex when force_reindex is True."""
        pipeline = pipeline_with_mocks
        
        # Index once
        pipeline.index_document(sample_pdf_path)
        
        # Force reindex
        result = pipeline.index_document(sample_pdf_path, force_reindex=True)
        assert not result.skipped_duplicate
        assert result.indexed_chunks > 0

    def test_index_invalid_pdf_raises(self, pipeline_with_mocks):
        """Should raise PDFParseError for invalid PDF."""
        pipeline = pipeline_with_mocks
        
        with pytest.raises(PDFParseError):
            pipeline.index_document(b"not a pdf", filename="bad.pdf")


class TestQueryAPI:
    """Test question answering through the public API."""

    def test_query_returns_result(self, pipeline_with_indexed_docs, fake_llm_provider):
        """Should return QueryResult with answer and sources."""
        pipeline = pipeline_with_indexed_docs
        pipeline._llm_provider = fake_llm_provider
        
        result = pipeline.query("What is this document about?")
        
        assert isinstance(result, QueryResult)
        assert result.question == "What is this document about?"
        assert result.answer != ""
        assert isinstance(result.sources, list)
        assert isinstance(result.refused, bool)
        assert isinstance(result.cited_indices, list)

    def test_query_with_document_filter(self, pipeline_with_indexed_docs, fake_llm_provider):
        """Should support filtering by document_id."""
        pipeline = pipeline_with_indexed_docs
        pipeline._llm_provider = fake_llm_provider
        
        # Get document ID from indexed documents
        docs = pipeline.list_documents()
        if docs:
            doc_id = docs[0]["document_id"]
            result = pipeline.query("Test question", document_id=doc_id)
            assert isinstance(result, QueryResult)

    def test_query_with_custom_top_k(self, pipeline_with_indexed_docs, fake_llm_provider):
        """Should support custom top_k parameter."""
        pipeline = pipeline_with_indexed_docs
        pipeline._llm_provider = fake_llm_provider
        
        result = pipeline.query("Test question", top_k=3)
        assert isinstance(result, QueryResult)

    def test_query_empty_raises(self, pipeline_with_mocks):
        """Should raise ValueError for empty question."""
        pipeline = pipeline_with_mocks
        
        with pytest.raises(ValueError):
            pipeline.query("")

    def test_query_refusal_on_low_confidence(self, pipeline_with_mocks):
        """Should return refused=True when confidence is low."""
        pipeline = pipeline_with_mocks
        
        # Query with no indexed documents - should refuse
        result = pipeline.query("Test question")
        assert result.refused is True


class TestDocumentManagementAPI:
    """Test document listing and deletion through the public API."""

    def test_list_documents_empty(self, pipeline_with_mocks):
        """Should return empty list when no documents indexed."""
        pipeline = pipeline_with_mocks
        
        docs = pipeline.list_documents()
        assert docs == []

    def test_list_documents_after_indexing(self, pipeline_with_mocks, sample_pdf_path):
        """Should list indexed documents with metadata."""
        pipeline = pipeline_with_mocks
        
        pipeline.index_document(sample_pdf_path)
        docs = pipeline.list_documents()
        
        assert len(docs) > 0
        doc = docs[0]
        assert "document_id" in doc
        assert "filename" in doc
        assert "chunk_count" in doc

    def test_delete_document(self, pipeline_with_indexed_docs):
        """Should delete document and return chunk count."""
        pipeline = pipeline_with_indexed_docs
        
        docs = pipeline.list_documents()
        if docs:
            doc_id = docs[0]["document_id"]
            deleted = pipeline.delete_document(doc_id)
            assert deleted > 0

    def test_delete_nonexistent_document(self, pipeline_with_mocks):
        """Should return 0 for nonexistent document."""
        pipeline = pipeline_with_mocks
        
        deleted = pipeline.delete_document("nonexistent-id")
        assert deleted == 0

    def test_get_stats(self, pipeline_with_indexed_docs):
        """Should return collection stats."""
        pipeline = pipeline_with_indexed_docs
        
        stats = pipeline.get_stats()
        assert "collection" in stats
        assert "total_chunks" in stats
        assert stats["total_chunks"] >= 0


class TestLibraryIndependence:
    """Test that the library doesn't depend on FastAPI or backend."""

    def test_no_fastapi_imports_in_source(self):
        """Verify rag_core source files don't import FastAPI."""
        import ast
        from pathlib import Path
        
        rag_core_path = Path(__file__).parent.parent.parent / "rag_core"
        
        for py_file in rag_core_path.rglob("*.py"):
            with open(py_file, "r", encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read(), filename=str(py_file))
                except SyntaxError:
                    continue  # Skip files with syntax errors
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            assert not alias.name.startswith("fastapi"), \
                                f"{py_file.name} imports {alias.name}"
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            assert not node.module.startswith("fastapi"), \
                                f"{py_file.name} imports from {node.module}"
                            assert not node.module.startswith("backend."), \
                                f"{py_file.name} imports from backend package: {node.module}"

    def test_no_backend_imports_in_source(self):
        """Verify rag_core source files don't import from backend."""
        import ast
        from pathlib import Path
        
        rag_core_path = Path(__file__).parent.parent.parent / "rag_core"
        
        for py_file in rag_core_path.rglob("*.py"):
            with open(py_file, "r", encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read(), filename=str(py_file))
                except SyntaxError:
                    continue
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith("backend."):
                            pytest.fail(f"{py_file.name} imports from backend: {node.module}")


# Fixtures

@pytest.fixture
def fake_embedding_provider():
    """Mock embedding provider for tests."""
    mock = Mock()
    mock.dimension = 128
    
    def embed_documents_side_effect(texts):
        """Return one vector per input text."""
        return [[0.1] * 128 for _ in texts]
    
    def embed_query_side_effect(text):
        """Return a single vector for query."""
        return [0.1] * 128
    
    mock.embed_documents.side_effect = embed_documents_side_effect
    mock.embed_query.side_effect = embed_query_side_effect
    return mock


@pytest.fixture
def fake_llm_provider():
    """Mock LLM provider for tests."""
    mock = Mock()
    mock.generate.return_value = "This is a test answer with citation [1]."
    return mock


@pytest.fixture
def sample_pdf_path(tmp_path):
    """Create a sample PDF file for testing."""
    import fitz  # PyMuPDF
    
    pdf_path = tmp_path / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "This is a test document.\nIt has some content for testing.")
    doc.save(pdf_path)
    doc.close()
    
    return str(pdf_path)


@pytest.fixture
def sample_pdf_bytes(sample_pdf_path):
    """Load sample PDF as bytes."""
    with open(sample_pdf_path, "rb") as f:
        return f.read()


@pytest.fixture
def pipeline_with_mocks(fake_embedding_provider, tmp_path, monkeypatch):
    """RAGPipeline with mocked providers for testing."""
    config = RAGConfig(
        embedding_settings=EmbeddingSettings(api_key="test", dimension=128),
        vector_store_settings=VectorStoreSettings(path=str(tmp_path / "qdrant")),
        llm_settings=LLMSettings(api_key="test", base_url="http://test", model="test"),
    )
    
    with patch("rag_core.pipeline.get_embedding_provider", return_value=fake_embedding_provider):
        pipeline = RAGPipeline(config=config)
        return pipeline


@pytest.fixture
def pipeline_with_indexed_docs(pipeline_with_mocks, sample_pdf_path):
    """RAGPipeline with an indexed document."""
    pipeline = pipeline_with_mocks
    pipeline.index_document(sample_pdf_path)
    return pipeline
