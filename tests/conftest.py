"""Shared fixtures for the test suite.

All PDFs are generated in-memory with PyMuPDF so the suite is fast,
offline, and deterministic. Fakes for embeddings/LLM keep the RAG
pipeline tests fully offline too.
"""
import io
import math
import zlib
from typing import Dict, List

import pytest
import pymupdf


# ---------------------------------------------------------------- fakes ----


_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "of", "to", "and", "or",
    "for", "in", "on", "with", "that", "this", "it", "its", "what", "which",
    "does", "do", "did", "use", "uses", "using", "how", "why", "when",
}


class FakeEmbeddingProvider:
    """Deterministic offline embedder.

    Bag-of-words hashing into a fixed-dim space (punctuation stripped,
    stopwords dropped), then L2 normalization. Texts sharing content
    words land close together (high cosine), unrelated texts near
    orthogonal (low cosine) - enough to test retrieval logic.
    """

    def __init__(self, dim: int = 256):
        self._dim = dim

    @property
    def model(self) -> str:
        return "fake-embedder"

    @property
    def dimension(self) -> int:
        return self._dim

    @property
    def normalizes_vectors(self) -> bool:
        return True

    def _embed_one(self, text: str) -> List[float]:
        vec = [0.0] * self._dim
        for word in text.lower().split():
            word = word.strip(".,!?;:()[]'\"")
            if not word or word in _STOPWORDS:
                continue
            vec[zlib.crc32(word.encode()) % self._dim] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed_one(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed_one(text)


class FakeLLMProvider:
    """Records calls and returns a canned grounded answer."""

    def __init__(self, canned_answer: str = "Based on the context, the answer is here. [1]"):
        self.canned_answer = canned_answer
        self.calls: List[tuple] = []

    @property
    def model(self) -> str:
        return "fake-llm"

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls.append((system_prompt, user_prompt))
        return self.canned_answer


@pytest.fixture
def fake_embedder():
    return FakeEmbeddingProvider()


@pytest.fixture
def fake_llm():
    return FakeLLMProvider()


@pytest.fixture
def memory_store(fake_embedder):
    from rag_core.config import VectorStoreSettings
    from rag_core.vector_stores.qdrant_store import QdrantVectorStore

    return QdrantVectorStore(
        VectorStoreSettings(path=":memory:"), dimension=fake_embedder.dimension
    )


# ------------------------------------------------------------ pdf fixtures --


@pytest.fixture
def make_pdf_bytes():
    """Factory fixture: build_pdf_bytes(["page one text", "", "page three"]) -> bytes."""

    def _build(page_texts) -> bytes:
        doc = pymupdf.open()
        try:
            for text in page_texts:
                page = doc.new_page()
                if text:
                    page.insert_text((50, 50), text, fontsize=12)
            return doc.tobytes()
        finally:
            doc.close()

    return _build


@pytest.fixture
def make_encrypted_pdf_bytes():
    """Factory fixture: returns (encrypted_pdf_bytes, user_password)."""

    def _build(page_texts, password="test-passphrase") -> tuple:
        doc = pymupdf.open()
        try:
            for text in page_texts:
                page = doc.new_page()
                if text:
                    page.insert_text((50, 50), text, fontsize=12)
            buffer = io.BytesIO()
            doc.save(
                buffer,
                encryption=pymupdf.PDF_ENCRYPT_AES_256,
                user_pw=password,
                owner_pw=password,
            )
            return buffer.getvalue(), password
        finally:
            doc.close()

    return _build
