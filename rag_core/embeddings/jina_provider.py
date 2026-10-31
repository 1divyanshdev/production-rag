import time
from typing import Any, List

import httpx

from rag_core.config import EmbeddingSettings
from rag_core.exceptions import EmbeddingError


class JinaEmbeddingProvider:
    """Concrete embedding provider wrapping Jina AI's embedding API.

    The free API key tier provides 100 RPM / 100 K TPM; the client batches
    requests and retries on 429 / 5xx with exponential back-off.

    Args:
        settings: Embedding configuration (API key, model, batch size, timeout).
        transport: Optional ``httpx`` transport subclass for injection during
            tests. When omitted a real HTTP transport is used.
        dimension: Optional pre-known vector dimensionality. When omitted the
            provider probes the API on first property access to discover it.
    """

    def __init__(
        self,
        settings: EmbeddingSettings,
        transport: Any = None,
        dimension: int | None = None,
    ):
        if not settings.api_key:
            raise EmbeddingError(
                "EMBEDDING_API_KEY is not set. Add it to your environment "
                "or .env file (see .env.example)."
            )
        self.settings = settings
        self.base_url = "https://api.jina.ai/v1/embeddings"
        self._dimension = dimension
        self._normalizes_vectors = True  # Jina defaults to L2 norm
        self.client = httpx.Client(
            transport=transport,
            timeout=self.settings.timeout_seconds,
            headers={
                "Authorization": f"Bearer {self.settings.api_key}",
                "Content-Type": "application/json",
            },
        )

    # -------- provider properties --------

    @property
    def model(self) -> str:
        return self.settings.model

    @property
    def dimension(self) -> int:
        if self._dimension is not None:
            return self._dimension
        # Probe a single short text to discover dimensionality.
        try:
            resp = self.client.post(
                self.base_url,
                json={
                    "model": self.settings.model,
                    "input": ["test dimension"],
                    "normalized": True,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            self._dimension = len(data["data"][0]["embedding"])
        except Exception as exc:
            raise EmbeddingError(
                f"Could not determine embedding dimension: {exc}"
            ) from exc
        return self._dimension

    @property
    def normalizes_vectors(self) -> bool:
        return self._normalizes_vectors

    # -------- public API --------

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        batch_size = getattr(self.settings, "batch_size", 32)
        results: List[List[float]] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            payload = {
                "model": self.settings.model,
                "input": batch,
                "normalized": True,
            }

            attempt = 0
            max_attempts = 3
            while attempt < max_attempts:
                try:
                    resp = self.client.post(self.base_url, json=payload)
                    # Rate-limit or transient errors -> retry with back-off.
                    if resp.status_code == 429 or 500 <= resp.status_code < 600:
                        wait = 2 ** attempt  # 1, 2, 4 seconds
                        time.sleep(wait)
                        attempt += 1
                        continue
                    resp.raise_for_status()
                    break  # success, exit retry loop
                except httpx.HTTPStatusError as exc:
                    if exc.response is not None and exc.response.status_code == 401:
                        raise EmbeddingError(
                            "Invalid Jina API key or unauthorized access."
                        ) from exc
                    if attempt < max_attempts - 1:
                        wait = 2 ** attempt
                        time.sleep(wait)
                        attempt += 1
                        continue
                    raise EmbeddingError(
                        f"HTTP error from Jina embedding API: {exc}"
                    ) from exc
                except httpx.RequestError as exc:
                    if attempt < max_attempts - 1:
                        wait = 2 ** attempt
                        time.sleep(wait)
                        attempt += 1
                        continue
                    raise EmbeddingError(
                        f"Network error contacting Jina API: {exc}"
                    ) from exc
            else:
                # Loop exhausted without a successful response: the last
                # status was 429/5xx on every attempt.
                status = getattr(resp, "status_code", None)
                raise EmbeddingError(
                    f"Embedding request failed after {max_attempts} attempts "
                    f"(last HTTP status: {status})."
                )

            # Parse response.
            try:
                data = resp.json()
                if "data" not in data or not isinstance(data["data"], list):
                    raise EmbeddingError("Unexpected response shape from Jina API")
                for entry in data["data"]:
                    if "embedding" not in entry or not isinstance(
                        entry["embedding"], list
                    ):
                        raise EmbeddingError(
                            "Malformed embedding entry in API response"
                        )
                    results.append(entry["embedding"])
                if self._dimension is None and results:
                    self._dimension = len(results[0])
            except Exception as exc:
                raise EmbeddingError(
                    f"Failed to parse embedding API response: {exc}"
                ) from exc

        return results

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query using the same model/dimension as documents."""
        return self.embed_documents([text])[0]