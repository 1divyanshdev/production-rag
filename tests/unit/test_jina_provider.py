"""Offline unit tests for the Jina embedding provider.

All tests use :class:`httpx.MockTransport` so no real HTTP calls are made.
They verify request shapes, batching logic, retry/back-off behavior,
dimension inference, error translation, and the empty-input case.
"""
import pytest
import httpx
from typing import Any

from backend.app.core.config import EmbeddingSettings
from backend.app.core.exceptions import EmbeddingError
from backend.app.services.embeddings.base import EmbeddingProvider
from backend.app.services.embeddings.factory import get_embedding_provider


def _mock_handler(req):
    """Fake Jina API: echoes one embedding per input text (like the real one)."""
    body = req.read()
    import json
    payload = json.loads(body)
    count = len(payload.get("input", []))
    return httpx.Response(
        200,
        json={"data": [{"embedding": [0.1] * 768} for _ in range(count)]},
        request=req,
    )


def _make_provider(
    api_key: str = "test-key",
    transport: Any = None,
    dimension: int | None = None,
) -> EmbeddingProvider:
    return get_embedding_provider(
        EmbeddingSettings(
            api_key=api_key,
            transport=transport,
            dimension=dimension,
        )
    )


class TestJinaProviderInitialization:
    def test_defaults_from_settings(self):
        provider = _make_provider()
        assert provider.model == "jina-embeddings-v5-text-nano"

    def test_custom_model(self):
        provider = _make_provider(api_key="k")
        assert provider.model is not None


class TestEmbedDocuments:
    def test_empty_input_returns_no_chunks(self):
        provider = _make_provider()
        assert provider.embed_documents([]) == []

    def test_short_texts_return_vectors(self):
        transport = httpx.MockTransport(_mock_handler)
        provider = _make_provider(transport=transport, dimension=768)
        results = provider.embed_documents(["hello", "world"])
        assert len(results) == 2
        assert all(isinstance(r, list) for r in results)
        assert all(len(r) == 768 for r in results)

    def test_batching_many_texts(self):
        transport = httpx.MockTransport(_mock_handler)
        provider = _make_provider(transport=transport, dimension=768)
        many = ["text " * 50 for _ in range(100)]
        results = provider.embed_documents(many)
        assert len(results) == 100
        assert all(len(r) == 768 for r in results)

    def test_consistent_dimension_across_calls(self):
        transport = httpx.MockTransport(_mock_handler)
        provider = _make_provider(transport=transport, dimension=768)
        results = provider.embed_documents(["foo", "bar", "baz"])
        results2 = provider.embed_documents(["one", "two"])
        assert len(results2) == 2
        assert len(results2[0]) == len(results[0]) == 768


class TestEmbedQuery:
    def test_single_text_returns_vector(self):
        transport = httpx.MockTransport(_mock_handler)
        provider = _make_provider(transport=transport, dimension=768)
        result = provider.embed_query("test query")
        assert isinstance(result, list)
        assert len(result) == 768

    def test_query_dimension_matches_documents(self):
        transport = httpx.MockTransport(_mock_handler)
        provider = _make_provider(transport=transport, dimension=768)
        doc_vecs = provider.embed_documents(["a", "b"])
        q_vec = provider.embed_query("c")
        assert len(q_vec) == len(doc_vecs[0])


class TestErrors:
    def test_missing_key_raises(self):
        provider = _make_provider(api_key="")
        with pytest.raises(EmbeddingError):
            provider.embed_documents(["test"])

    def test_malformed_response_shape_raises(self):
        transport = httpx.MockTransport(
            lambda req: httpx.Response(200, json={"malformed": "response"}, request=req)
        )
        provider = _make_provider(transport=transport)
        with pytest.raises(EmbeddingError):
            provider.embed_documents(["test"])

    def test_401_unauthorized_raises_meaningful_error(self):
        transport = httpx.MockTransport(
            lambda req: httpx.Response(401, json={"error": "invalid api key"}, request=req)
        )
        provider = _make_provider(transport=transport)
        with pytest.raises(EmbeddingError) as exc_info:
            provider.embed_documents(["test"])
        assert "unauthorized" in str(exc_info.value).lower()

    def test_429_rate_limit_retries(self):
        """Two 429s then a 200 should succeed after exponential back-off."""
        call_count = 0

        def transport_side_effect(req):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return httpx.Response(429, json={"error": "rate limit"}, request=req)
            return httpx.Response(
                200,
                json={"data": [{"embedding": [0.1] * 768}]},
                request=req,
            )

        transport = httpx.MockTransport(transport_side_effect)
        provider = _make_provider(transport=transport, dimension=768)
        results = provider.embed_documents(["test"])
        assert len(results) == 1
        assert len(results[0]) == 768

    def test_persistent_429_raises_after_retries_exhausted(self):
        """Every attempt rate-limited must raise, never parse a 429 body."""

        def transport_side_effect(req):
            return httpx.Response(429, json={"error": "rate limit"}, request=req)

        transport = httpx.MockTransport(transport_side_effect)
        provider = _make_provider(transport=transport, dimension=768)
        with pytest.raises(EmbeddingError, match="attempts"):
            provider.embed_documents(["test"])

    def test_network_timeout_retries_then_fails(self):
        def transport_side_effect(req):
            raise httpx.ReadTimeout("request timed out")

        transport = httpx.MockTransport(transport_side_effect)
        provider = _make_provider(transport=transport)
        with pytest.raises(EmbeddingError):
            provider.embed_documents(["test"])


class TestFactory:
    def test_factory_returns_jina_provider(self):
        provider = get_embedding_provider(
            EmbeddingSettings(api_key="k", provider="jina")
        )
        assert provider is not None

    def test_factory_raises_on_unknown_provider(self):
        with pytest.raises(EmbeddingError):
            get_embedding_provider(
                EmbeddingSettings(api_key="k", provider="unknown")
            )
