"""Offline unit tests for the Google Gemini LLM provider.

All tests use httpx.MockTransport — no real API calls are made.
Covers config validation, happy-path generation, auth (403) errors,
rate-limit retries, timeouts, and response-parse failures.
"""
import json

import httpx
import pytest

from rag_core.config import LLMSettings
from rag_core.exceptions import LLMError
from rag_core.llm.gemini_provider import GoogleGeminiProvider


def _settings(**overrides):
    base = dict(
        api_key="AIzaSy-test-key",
        base_url="https://generativelanguage.googleapis.com/v1beta",
        model="gemini-1.5-flash",
    )
    base.update(overrides)
    return LLMSettings(**base)


def _ok_transport(captured=None):
    """Returns a transport that emits a valid Gemini generateContent response."""

    def handler(req: httpx.Request) -> httpx.Response:
        if captured is not None:
            captured.append(req)
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [{"text": "Grounded answer. [1]"}],
                            "role": "model",
                        },
                        "finishReason": "STOP",
                    }
                ],
                "usageMetadata": {"promptTokenCount": 10, "candidatesTokenCount": 5},
            },
            request=req,
        )

    return httpx.MockTransport(handler)


class TestConfigValidation:
    def test_missing_api_key_raises(self):
        with pytest.raises(LLMError, match="LLM_API_KEY"):
            GoogleGeminiProvider(_settings(api_key=""))

    def test_missing_model_raises(self):
        with pytest.raises(LLMError, match="LLM_MODEL"):
            GoogleGeminiProvider(_settings(model=""))


class TestGenerate:
    def test_success_returns_text_content(self):
        provider = GoogleGeminiProvider(_settings(), transport=_ok_transport())
        result = provider.generate("You are a helpful assistant.", "What is RAG?")
        assert result == "Grounded answer. [1]"

    def test_api_key_sent_in_url_not_header(self):
        captured = []
        provider = GoogleGeminiProvider(_settings(), transport=_ok_transport(captured))
        provider.generate("sys", "usr")

        req = captured[0]
        assert "key=AIzaSy-test-key" in str(req.url)
        # Key must NOT appear in a standard Authorization header.
        assert "authorization" not in {k.lower() for k in req.headers}

    def test_request_targets_correct_endpoint(self):
        captured = []
        provider = GoogleGeminiProvider(_settings(), transport=_ok_transport(captured))
        provider.generate("sys", "usr")

        req = captured[0]
        assert "gemini-1.5-flash:generateContent" in req.url.path

    def test_request_body_has_contents_field(self):
        captured = []
        provider = GoogleGeminiProvider(_settings(), transport=_ok_transport(captured))
        provider.generate("system prompt", "user question")

        body = json.loads(captured[0].read())
        assert "contents" in body
        assert isinstance(body["contents"], list)
        assert body["contents"][0]["parts"][0]["text"]  # combined prompt present

    def test_403_raises_immediately(self):
        calls = {"n": 0}

        def handler(req):
            calls["n"] += 1
            return httpx.Response(403, json={"error": {"message": "forbidden"}}, request=req)

        provider = GoogleGeminiProvider(_settings(), transport=httpx.MockTransport(handler))
        with pytest.raises(LLMError, match="[Rr]estrict|[Ff]orbid|key"):
            provider.generate("s", "u")

    def test_400_surfaces_api_error_message(self):
        def handler(req):
            return httpx.Response(
                400,
                json={"error": {"code": 400, "message": "invalid model", "status": "INVALID_ARGUMENT"}},
                request=req,
            )

        provider = GoogleGeminiProvider(_settings(), transport=httpx.MockTransport(handler))
        with pytest.raises(LLMError, match="invalid model|[Gg]emini"):
            provider.generate("s", "u")

    def test_persistent_429_raises_after_exhaustion(self):
        def handler(req):
            return httpx.Response(429, json={"error": "quota exceeded"}, request=req)

        provider = GoogleGeminiProvider(_settings(), transport=httpx.MockTransport(handler))
        with pytest.raises(LLMError, match="attempt"):
            provider.generate("s", "u")

    def test_transient_429_then_success(self):
        calls = {"n": 0}

        def handler(req):
            calls["n"] += 1
            if calls["n"] <= 2:
                return httpx.Response(429, json={}, request=req)
            return httpx.Response(
                200,
                json={
                    "candidates": [
                        {"content": {"parts": [{"text": "ok"}]}}
                    ]
                },
                request=req,
            )

        provider = GoogleGeminiProvider(_settings(), transport=httpx.MockTransport(handler))
        assert provider.generate("s", "u") == "ok"
        assert calls["n"] == 3

    def test_network_timeout_raises_llm_error(self):
        def handler(req):
            raise httpx.ReadTimeout("too slow")

        provider = GoogleGeminiProvider(_settings(), transport=httpx.MockTransport(handler))
        with pytest.raises(LLMError, match="[Nn]etwork"):
            provider.generate("s", "u")

    def test_missing_candidates_field_raises(self):
        provider = GoogleGeminiProvider(
            _settings(),
            transport=httpx.MockTransport(
                lambda req: httpx.Response(200, json={"usageMetadata": {}}, request=req)
            ),
        )
        with pytest.raises(LLMError, match="candidates"):
            provider.generate("s", "u")

    def test_empty_candidates_raises(self):
        provider = GoogleGeminiProvider(
            _settings(),
            transport=httpx.MockTransport(
                lambda req: httpx.Response(200, json={"candidates": []}, request=req)
            ),
        )
        with pytest.raises(LLMError, match="candidates"):
            provider.generate("s", "u")

    def test_empty_parts_raises(self):
        provider = GoogleGeminiProvider(
            _settings(),
            transport=httpx.MockTransport(
                lambda req: httpx.Response(
                    200,
                    json={"candidates": [{"content": {"parts": []}}]},
                    request=req,
                )
            ),
        )
        with pytest.raises(LLMError, match="[Pp]arts"):
            provider.generate("s", "u")
