"""Offline API tests: TestClient + dependency overrides with fakes."""
import pytest
from fastapi.testclient import TestClient

from backend.app.api.deps import Services, get_services
from backend.app.api.routes import router
from backend.app.main import create_app
from backend.app.services.chunking_service import ChunkingService
from backend.app.services.generation_service import GenerationService
from backend.app.services.ingestion_pipeline import IngestionPipeline
from backend.app.services.ingestion_service import DocumentIngestionService
from backend.app.services.retrieval_service import RetrievalService


@pytest.fixture
def services(fake_embedder, memory_store, fake_llm):
    retrieval_settings = __import__(
        "backend.app.core.config", fromlist=["RetrievalSettings"]
    ).RetrievalSettings(top_k=5, score_threshold=0.2)
    pipeline = IngestionPipeline(
        ingestion=DocumentIngestionService(),
        chunker=ChunkingService(),
        embedder=fake_embedder,
        store=memory_store,
    )
    retrieval = RetrievalService(fake_embedder, memory_store, retrieval_settings)
    return Services(
        embedder=fake_embedder,
        store=memory_store,
        pipeline=pipeline,
        retrieval=retrieval,
        retrieval_settings=retrieval_settings,
        _llm=fake_llm,
        _llm_settings=None,
    )


@pytest.fixture
def client(services):
    app = create_app()
    app.router.routes = [
        r for r in app.router.routes if getattr(r, "path", "").startswith(("/api", "/openapi", "/docs", "/redoc"))
    ] or app.router.routes
    app.include_router(router)
    app.dependency_overrides[get_services] = lambda: services
    return TestClient(app, raise_server_exceptions=True)


class TestHealth:
    def test_health_ok(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ok"
        assert body["version"]


class TestUpload:
    def test_upload_pdf_indexes_document(self, client, make_pdf_bytes, services):
        resp = client.post(
            "/api/documents",
            files={"file": ("report.pdf", make_pdf_bytes(["Vector search text here."]), "application/pdf")},
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["filename"] == "report.pdf"
        assert body["indexed_chunks"] >= 1
        assert body["skipped_duplicate"] is False
        assert body["document_id"]

    def test_duplicate_upload_is_flagged_not_duplicated(self, client, make_pdf_bytes):
        data = make_pdf_bytes(["Same content twice."])
        first = client.post("/api/documents", files={"file": ("a.pdf", data, "application/pdf")})
        second = client.post("/api/documents", files={"file": ("b.pdf", data, "application/pdf")})

        assert first.json()["skipped_duplicate"] is False
        assert second.json()["skipped_duplicate"] is True
        assert second.json()["indexed_chunks"] == 0

    def test_non_pdf_rejected(self, client):
        resp = client.post(
            "/api/documents",
            files={"file": ("notes.txt", b"plain text", "text/plain")},
        )
        assert resp.status_code == 400
        assert "pdf" in resp.json()["detail"].lower()

    def test_empty_pdf_rejected(self, client):
        resp = client.post(
            "/api/documents",
            files={"file": ("empty.pdf", b"", "application/pdf")},
        )
        assert resp.status_code == 400

    def test_corrupt_pdf_maps_to_400(self, client):
        resp = client.post(
            "/api/documents",
            files={"file": ("broken.pdf", b"not a pdf", "application/pdf")},
        )
        assert resp.status_code == 400


class TestAsk:
    def test_ask_returns_grounded_answer_with_sources(self, client, make_pdf_bytes):
        client.post(
            "/api/documents",
            files={"file": ("kb.pdf", make_pdf_bytes(["Reranking reorders retrieved chunks for precision."]), "application/pdf")},
        )

        resp = client.post("/api/ask", json={"question": "reranking chunks precision"})

        assert resp.status_code == 200
        body = resp.json()
        assert body["refused"] is False
        assert body["answer"]
        assert len(body["sources"]) >= 1
        assert body["sources"][0]["filename"] == "kb.pdf"
        assert body["sources"][0]["page_number"] == 1

    def test_ask_refuses_on_empty_index(self, client):
        resp = client.post("/api/ask", json={"question": "anything"})

        assert resp.status_code == 200
        body = resp.json()
        assert body["refused"] is True
        assert body["sources"] == []

    def test_ask_validation_error_on_empty_question(self, client):
        resp = client.post("/api/ask", json={"question": ""})
        assert resp.status_code == 422

    def test_ask_respects_top_k_override(self, client, make_pdf_bytes):
        client.post(
            "/api/documents",
            files={"file": ("kb.pdf", make_pdf_bytes(["Qdrant stores embeddings."]), "application/pdf")},
        )
        resp = client.post("/api/ask", json={"question": "qdrant embeddings", "top_k": 1})
        body = resp.json()
        assert len(body["sources"]) == 1


class TestStats:
    def test_stats_reflect_indexed_content(self, client, make_pdf_bytes):
        before = client.get("/api/stats").json()["total_chunks"]
        client.post(
            "/api/documents",
            files={"file": ("s.pdf", make_pdf_bytes(["Stats check content."]), "application/pdf")},
        )
        after = client.get("/api/stats").json()
        assert after["total_chunks"] > before
        assert after["collection"]


class TestDocumentManagement:
    def test_list_documents_after_upload(self, client, make_pdf_bytes):
        client.post(
            "/api/documents",
            files={"file": ("kb.pdf", make_pdf_bytes(["Doc listing content one.", "Doc listing content two."]), "application/pdf")},
        )

        resp = client.get("/api/documents")

        assert resp.status_code == 200
        docs = resp.json()
        assert len(docs) == 1
        assert docs[0]["filename"] == "kb.pdf"
        assert docs[0]["chunk_count"] >= 2
        assert docs[0]["document_id"]

    def test_delete_document_removes_chunks(self, client, make_pdf_bytes):
        upload = client.post(
            "/api/documents",
            files={"file": ("gone.pdf", make_pdf_bytes(["Delete me content."]), "application/pdf")},
        ).json()
        doc_id = upload["document_id"]
        chunks_before = client.get("/api/stats").json()["total_chunks"]

        resp = client.delete(f"/api/documents/{doc_id}")

        assert resp.status_code == 200
        assert resp.json()["deleted_chunks"] == upload["indexed_chunks"]
        assert client.get("/api/stats").json()["total_chunks"] == chunks_before - upload["indexed_chunks"]
        assert client.get("/api/documents").json() == []

    def test_delete_unknown_document_404(self, client):
        resp = client.delete("/api/documents/does-not-exist")
        assert resp.status_code == 404
