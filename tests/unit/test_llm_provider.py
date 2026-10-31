"""Offline tests for the OpenAI-compatible LLM provider."""
import httpx
import pytest

from rag_core.config import LLMSettings
from rag_core.exceptions import LLMError
from rag_core.llm.openai_compat import OpenAICompatibleLLMProvider


def _settings(**overrides):
    base = dict(
        api_key="test-key",
        base_url="https://fake-llm.example/v1",
        model="fake-chat-model",
    )
    base.update(overrides)
    return LLMSettings(**base)


def _ok_transport(captured=None):
    def handler(req: httpx.Request) -> httpx.Response:
        if captured is not None:
            captured.append(req)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"role": "assistant", "content": "Grounded answer. [1]"}}
                ]
            },
            request=req,
        )

    return httpx.MockTransport(handler)


class TestConfigValidation:
    def test_missing_api_key_raises_immediately(self):
        with pytest.raises(LLMError, match="LLM_API_KEY"):
            OpenAICompatibleLLMProvider(_settings(api_key=""))

    def test_missing_base_url_raises_immediately(self):
        with pytest.raises(LLMError, match="LLM_BASE_URL"):
            OpenAICompatibleLLMProvider(_settings(base_url=""))

    def test_missing_model_raises_immediately(self):
        with pytest.raises(LLMError, match="LLM_MODEL"):
            OpenAICompatibleLLMProvider(_settings(model=""))


class TestGenerate:
    def test_success_returns_content(self):
        provider = OpenAICompatibleLLMProvider(_settings(), transport=_ok_transport())

        answer = provider.generate("system rules", "user question")

        assert answer == "Grounded answer. [1]"

    def test_request_shape_is_openai_chat_completions(self):
        captured = []
        provider = OpenAICompatibleLLMProvider(_settings(), transport=_ok_transport(captured))

        provider.generate("sys", "usr")

        req = captured[0]
        assert req.url.path.endswith("/chat/completions")
        body = httpx.Request(
            method=req.method, url=req.url, headers=req.headers, content=req.read()
        )
        import json

        payload = json.loads(body.read())
        assert payload["model"] == "fake-chat-model"
        assert payload["messages"][0]["role"] == "system"
        assert payload["messages"][1]["role"] == "user"

    def test_401_raises_without_retries(self):
        calls = {"n": 0}

        def handler(req):
            calls["n"] += 1
            return httpx.Response(401, json={"error": "bad key"}, request=req)

        provider = OpenAICompatibleLLMProvider(
            _settings(), transport=httpx.MockTransport(handler)
        )
        with pytest.raises(LLMError, match="unauthorized"):
            provider.generate("s", "u")
        assert calls["n"] == 1  # no retries on auth failure

    def test_persistent_429_raises_after_exhaustion(self):
        def handler(req):
            return httpx.Response(429, json={"error": "rate limit"}, request=req)

        provider = OpenAICompatibleLLMProvider(
            _settings(), transport=httpx.MockTransport(handler)
        )
        with pytest.raises(LLMError, match="attempts"):
            provider.generate("s", "u")

    def test_transient_429_then_success(self):
        calls = {"n": 0}

        def handler(req):
            calls["n"] += 1
            if calls["n"] <= 2:
                return httpx.Response(429, json={}, request=req)
            return httpx.Response(
                200,
                json={"choices": [{"message": {"content": "ok"}}]},
                request=req,
            )

        provider = OpenAICompatibleLLMProvider(
            _settings(), transport=httpx.MockTransport(handler)
        )
        assert provider.generate("s", "u") == "ok"

    def test_timeout_raises_llm_error(self):
        def handler(req):
            raise httpx.ReadTimeout("too slow")

        provider = OpenAICompatibleLLMProvider(
            _settings(), transport=httpx.MockTransport(handler)
        )
        with pytest.raises(LLMError, match="Network error"):
            provider.generate("s", "u")

    def test_malformed_response_raises(self):
        provider = OpenAICompatibleLLMProvider(
            _settings(),
            transport=httpx.MockTransport(
                lambda req: httpx.Response(200, json={"weird": True}, request=req)
            ),
        )
        with pytest.raises(LLMError, match="parse"):
            provider.generate("s", "u")
