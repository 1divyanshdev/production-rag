"""
OpenAI-compatible chat provider.

One implementation covers many free-tier LLM APIs (Groq, OpenRouter,
Cohere compatibility endpoint, ...) because they all expose
``POST {base_url}/chat/completions`` with the same request/response shape.

The API key and base URL come from LLMSettings env vars - never hard-coded.
"""
import time
from typing import Any

import httpx

from rag_core.config import LLMSettings
from rag_core.exceptions import LLMError


class OpenAICompatibleLLMProvider:
    """Chat completions against any OpenAI-compatible endpoint."""

    def __init__(self, settings: LLMSettings, transport: Any = None):
        if not settings.api_key:
            raise LLMError(
                "LLM_API_KEY is not set. Add it to your environment or .env file."
            )
        if not settings.base_url:
            raise LLMError(
                "LLM_BASE_URL is not set (e.g. https://api.groq.com/openai/v1)."
            )
        if not settings.model:
            raise LLMError("LLM_MODEL is not set.")

        self.settings = settings
        self.client = httpx.Client(
            transport=transport,
            timeout=settings.timeout_seconds,
            headers={
                "Authorization": f"Bearer {settings.api_key}",
                "Content-Type": "application/json",
            },
        )

    @property
    def model(self) -> str:
        return self.settings.model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        payload = {
            "model": self.settings.model,
            "temperature": self.settings.temperature,
            "max_tokens": self.settings.max_tokens,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }

        attempt = 0
        max_attempts = 3
        resp = None
        while attempt < max_attempts:
            try:
                resp = self.client.post(
                    f"{self.settings.base_url.rstrip('/')}/chat/completions",
                    json=payload,
                )
                if resp.status_code == 429 or 500 <= resp.status_code < 600:
                    time.sleep(2 ** attempt)
                    attempt += 1
                    continue
                resp.raise_for_status()
                break
            except httpx.HTTPStatusError as exc:
                if exc.response is not None and exc.response.status_code == 401:
                    raise LLMError("Invalid LLM API key or unauthorized access.") from exc
                if attempt < max_attempts - 1:
                    time.sleep(2 ** attempt)
                    attempt += 1
                    continue
                raise LLMError(f"HTTP error from LLM API: {exc}") from exc
            except httpx.RequestError as exc:
                if attempt < max_attempts - 1:
                    time.sleep(2 ** attempt)
                    attempt += 1
                    continue
                raise LLMError(f"Network error contacting LLM API: {exc}") from exc
        else:
            status = getattr(resp, "status_code", None)
            raise LLMError(
                f"LLM request failed after {max_attempts} attempts "
                f"(last HTTP status: {status})."
            )

        try:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            if not isinstance(content, str):
                raise LLMError("LLM response content is not a string.")
            return content
        except LLMError:
            raise
        except Exception as exc:
            raise LLMError(f"Failed to parse LLM response: {exc}") from exc
