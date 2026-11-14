"""
Anthropic Claude chat provider.

Implements Claude's Messages API for RAG answer generation.
Compatible with Claude 3 models (Opus, Sonnet, Haiku).
"""
import time
from typing import Any

import httpx

from rag_core.config import LLMSettings
from rag_core.exceptions import LLMError


class AnthropicClaudeProvider:
    """Chat completions using Anthropic's Claude API."""

    def __init__(self, settings: LLMSettings, transport: Any = None):
        if not settings.api_key:
            raise LLMError(
                "LLM_API_KEY is not set. Get your Anthropic API key at "
                "https://console.anthropic.com/account/keys"
            )
        if not settings.model:
            raise LLMError(
                "LLM_MODEL is not set. Examples: claude-3-5-sonnet-20241022, "
                "claude-3-opus-20240229, claude-3-haiku-20240307"
            )

        self.settings = settings
        self.client = httpx.Client(
            transport=transport,
            timeout=settings.timeout_seconds,
            headers={
                "x-api-key": settings.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
        )

    @property
    def model(self) -> str:
        return self.settings.model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate answer using Claude's Messages API.
        
        Args:
            system_prompt: System instructions (RAG prompt template)
            user_prompt: User query with retrieved context
            
        Returns:
            Generated answer text
            
        Raises:
            LLMError: On API failures, auth errors, or network issues
        """
        payload = {
            "model": self.settings.model,
            "max_tokens": self.settings.max_tokens,
            "temperature": self.settings.temperature,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
        }

        attempt = 0
        max_attempts = 3
        resp = None
        
        while attempt < max_attempts:
            try:
                resp = self.client.post(
                    "https://api.anthropic.com/v1/messages",
                    json=payload,
                )
                
                # Handle rate limits and server errors with retry
                if resp.status_code == 429 or 500 <= resp.status_code < 600:
                    time.sleep(2 ** attempt)
                    attempt += 1
                    continue
                    
                resp.raise_for_status()
                break
                
            except httpx.HTTPStatusError as exc:
                if exc.response is not None:
                    if exc.response.status_code == 401:
                        raise LLMError(
                            "Invalid Anthropic API key. Check your LLM_API_KEY."
                        ) from exc
                    if exc.response.status_code == 400:
                        # Parse error details from Anthropic
                        try:
                            error_data = exc.response.json()
                            error_msg = error_data.get("error", {}).get("message", "Bad request")
                            raise LLMError(f"Claude API error: {error_msg}") from exc
                        except Exception:
                            raise LLMError(f"Claude API bad request: {exc}") from exc
                            
                if attempt < max_attempts - 1:
                    time.sleep(2 ** attempt)
                    attempt += 1
                    continue
                raise LLMError(f"HTTP error from Claude API: {exc}") from exc
                
            except httpx.RequestError as exc:
                if attempt < max_attempts - 1:
                    time.sleep(2 ** attempt)
                    attempt += 1
                    continue
                raise LLMError(f"Network error contacting Claude API: {exc}") from exc
        else:
            status = getattr(resp, "status_code", None)
            raise LLMError(
                f"Claude request failed after {max_attempts} attempts "
                f"(last HTTP status: {status})."
            )

        try:
            data = resp.json()
            
            # Claude response format: {"content": [{"type": "text", "text": "..."}], ...}
            if "content" not in data:
                raise LLMError("Claude response missing 'content' field")
                
            content_blocks = data["content"]
            if not content_blocks:
                raise LLMError("Claude response has empty content")
                
            # Extract text from first content block
            text = content_blocks[0].get("text", "")
            if not isinstance(text, str):
                raise LLMError("Claude response content is not a string")
                
            return text
            
        except LLMError:
            raise
        except Exception as exc:
            raise LLMError(f"Failed to parse Claude response: {exc}") from exc
