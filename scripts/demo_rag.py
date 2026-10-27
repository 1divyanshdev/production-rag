"""
End-to-end RAG demo: ingest -> chunk -> embed -> index -> retrieve -> answer.

Runs fully OFFLINE using deterministic fakes (no keys needed) to demonstrate
the pipeline mechanics. With EMBEDDING_API_KEY + LLM_* env vars set, set
use_live=True to run against the real providers.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import pymupdf

from backend.app.services.chunking_service import ChunkingService
from backend.app.services.embeddings.factory import get_embedding_provider
from backend.app.services.generation_service import GenerationService
from backend.app.services.ingestion_pipeline import IngestionPipeline
from backend.app.services.ingestion_service import DocumentIngestionService
from backend.app.services.llm.openai_compat import OpenAICompatibleLLMProvider
from backend.app.services.retrieval_service import RetrievalService
from backend.app.services.vector_store import QdrantVectorStore
from backend.app.core.config import (
    load_embedding_settings,
    load_llm_settings,
    load_vector_store_settings,
)

SAMPLE_PAGES = [
    "Qdrant is a vector database that stores embeddings and performs "
    "nearest neighbour search using the HNSW algorithm.",
    "Chunking splits long documents into small coherent passages so each "
    "embedding represents one focused topic.",
    "Chocolate chip cookies need butter, sugar, flour and chocolate chips.",
]


def build_sample_pdf() -> bytes:
    doc = pymupdf.open()
    for text in SAMPLE_PAGES:
        page = doc.new_page()
        # wrap at word boundaries: insert_text does not wrap lines, and
        # mid-word splits would corrupt the extracted text downstream
        y = 60
        words = text.split()
        line = ""
        for word in words:
            if len(line) + len(word) + 1 > 70:
                page.insert_text((50, y), line, fontsize=11)
                y += 18
                line = word
            else:
                line = f"{line} {word}".strip()
        if line:
            page.insert_text((50, y), line, fontsize=11)
    data = doc.tobytes()
    doc.close()
    return data


def main(use_live: bool = False):
    embedder = (
        get_embedding_provider(load_embedding_settings())
        if use_live else _OfflineEmbedder()
    )
    llm = (
        OpenAICompatibleLLMProvider(load_llm_settings())
        if use_live else _OfflineLLM()
    )

    # Fresh throwaway storage per demo run unless --persist is given.
    import tempfile

    import os

    if "--persist" in sys.argv:
        store_settings = load_vector_store_settings()
    else:
        store_settings = load_vector_store_settings()
        store_settings.path = tempfile.mkdtemp(prefix="rag-demo-store-")

    store = QdrantVectorStore(store_settings, dimension=embedder.dimension)

    pipeline = IngestionPipeline(
        ingestion=DocumentIngestionService(),
        chunker=ChunkingService(),
        embedder=embedder,
        store=store,
    )
    result = pipeline.index_pdf(build_sample_pdf(), filename="demo.pdf")
    print(f"[index] {result}")

    retrieval = RetrievalService(embedder, store)
    generation = GenerationService(retrieval, llm)

    for question in [
        "What algorithm does Qdrant use for nearest neighbour search?",
        "How do you make chocolate chip cookies?",
        "What is the airspeed velocity of an unladen swallow?",
    ]:
        answer = generation.ask(question)
        print(f"\nQ: {question}")
        print(f"A: {answer.answer}")
        if answer.sources:
            for src in answer.sources[:3]:
                print(f"   - {src['filename']} p.{src['page_number']} (score {src['score']})")
        if answer.refused:
            print("   (refused: retrieval confidence below threshold)")


class _OfflineEmbedder:
    """Minimal offline embedder (bag of content words, L2-normalized)."""

    dimension = 256
    model = "offline-fake"
    normalizes_vectors = True

    _STOPWORDS = {
        "the", "a", "an", "is", "are", "was", "were", "of", "to", "and",
        "or", "for", "in", "on", "with", "that", "this", "it", "its",
        "what", "which", "does", "do", "did", "use", "uses", "using",
        "how", "why", "when",
    }

    def _embed(self, text):
        import math, zlib

        vec = [0.0] * self.dimension
        for word in text.lower().split():
            word = word.strip(".,!?;:()[]'\"")
            if not word or word in self._STOPWORDS:
                continue
            vec[zlib.crc32(word.encode()) % self.dimension] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def embed_documents(self, texts):
        return [self._embed(t) for t in texts]

    def embed_query(self, text):
        return self._embed(text)


class _OfflineLLM:
    model = "offline-fake"

    def generate(self, system_prompt, user_prompt):
        first_block = user_prompt.split("]")[1].split("\n") if "]" in user_prompt else [""]
        return f"Based on the provided context, here is the relevant excerpt: [1]"


if __name__ == "__main__":
    main(use_live="--live" in sys.argv)
