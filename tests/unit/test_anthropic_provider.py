"""Offline unit tests for the Anthropic Claude LLM provider.

All tests use httpx.MockTransport — no real API calls are made.
Covers config validation, happy-path generation, auth errors, rate-limit
retries, timeouts, and response-parse failures.
"""
import json

import httpx
import pytest

from rag_core.config import LLMSettings
from rag_core.exceptions import LLMError
from rag_core.llm.anthropic_provider import AnthropicClaudeProvider


def _settings(**overrides):
    base = dict(
        api_key="sk-ant-test-key",
        base_url="https://api.anthropic.com/v1",
        model="claude-3-5-sonnet-20241022",
    )
    base.update(overrides)
    return LLMSettings(**base)


def _ok_transport(captured=None):
    """Returns a transport that emits a valid Claude Messages API response."""

    def handler(req: httpx.Request) -> httpx.Response:
        if captured is not None:
            captured.append(req)
        return httpx.Response(
            200,
            json={
                "id": "msg_01",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": "Grounded answer. [1]"}],
                "model": "claude-3-5-sonnet-20241022",
                "stop_reason": "end_turn",
                "usage": {"input_tokens": 10, "output_tokens": 5},
            },
            request=req,
        )

    return httpx.MockTransport(handler)


class TestConfigValidation:
    def test_missing_api_key_raises(self):
        with pytest.raises(LLMError, match="LLM_API_KEY"):
            AnthropicClaudeProvider(_settings(api_key=""))

    def test_missing_model_raises(self):
        with pytest.raises(LLMError, match="LLM_MODEL"):
            AnthropicClaudeProvider(_settings(model=""))


class TestGenerate:
    def test_success_returns_text_content(self):
        provider = AnthropicClaudeProvider(_settings(), transport=_ok_transport())
        result = provider.generate("You are a helpful assistant.", "What is RAG?")
        assert result == "Grounded answer. [1]"

    def test_request_uses_correct_endpoint_and_headers(self):
        captured = []
        provider = AnthropicClaudeProvider(_settings(), transport=_ok_transport(captured))
        provider.generate("sys", "usr")

        req = captured[0]
        assert req.url.path == "/v1/messages"
        assert req.headers.get("x-api-key") == "sk-ant-test-key"
        assert req.headers.get("anthropic-version") == "2023-06-01"

    def test_request_body_shape(self):
        captured = []
        provider = AnthropicClaudeProvider(_settings(), transport=_ok_transport(captured))
        provider.generate("system instructions", "user question")

        body = json.loads(captured[0].read())
        assert body["model"] == "claude-3-5-sonnet-20241022"
        assert body["system"] == "system instructions"
        assert body["messages"] == [{"role": "user", "content": "user question"}]
        assert "max_tokens" in body

    def test_401_raises_immediately_without_retry(self):
        calls = {"n": 0}

        def handler(req):
            calls["n"] += 1
            return httpx.Response(401, json={"error": {"message": "bad key"}}, request=req)

        provider = AnthropicClaudeProvider(_settings(), transport=httpx.MockTransport(handler))
        with pytest.raises(LLMError, match="[Aa]nthrop|key"):
            provider.generate("s", "u")
        assert calls["n"] == 1

    def test_400_surfaces_api_error_message(self):
        def handler(req):
            return httpx.Response(
                400,
                json={"error": {"type": "invalid_request_error", "message": "bad input"}},
                request=req,
            )

        provider = AnthropicClaudeProvider(_settings(), transport=httpx.MockTransport(handler))
        with pytest.raises(LLMError, match="bad input|[Cc]laude"):
            provider.generate("s", "u")

    def test_persistent_429_raises_after_exhaustion(self):
        def handler(req):
            return httpx.Response(429, json={"error": "rate limit"}, request=req)

        provider = AnthropicClaudeProvider(_settings(), transport=httpx.MockTransport(handler))
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
                json={"content": [{"type": "text", "text": "ok"}]},
                request=req,
            )

        provider = AnthropicClaudeProvider(_settings(), transport=httpx.MockTransport(handler))
        assert provider.generate("s", "u") == "ok"
        assert calls["n"] == 3

    def test_network_timeout_raises_llm_error(self):
        def handler(req):
            raise httpx.ReadTimeout("too slow")

        provider = AnthropicClaudeProvider(_settings(), transport=httpx.MockTransport(handler))
        with pytest.raises(LLMError, match="[Nn]etwork"):
            provider.generate("s", "u")

    def test_missing_content_field_raises(self):
        provider = AnthropicClaudeProvider(
            _settings(),
            transport=httpx.MockTransport(
                lambda req: httpx.Response(200, json={"id": "msg_01"}, request=req)
            ),
        )
        with pytest.raises(LLMError, match="content"):
            provider.generate("s", "u")

    def test_empty_content_raises(self):
        provider = AnthropicClaudeProvider(
            _settings(),
            transport=httpx.MockTransport(
                lambda req: httpx.Response(200, json={"content": []}, request=req)
            ),
        )
        with pytest.raises(LLMError, match="[Ee]mpty"):
            provider.generate("s", "u")
