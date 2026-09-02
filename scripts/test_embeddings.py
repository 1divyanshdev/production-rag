"""Manual live-suite for the embedding component.

Run this script once you have set EMBEDDING_API_KEY in your environment
(see .env.example).  It performs a quick similarity sanity check and prints
the model name + dimensionality.

If the key is not set the script exits early with a helpful message.
"""
import os
import sys

from backend.app.core.config import load_embedding_settings
from backend.app.services.embeddings.factory import get_embedding_provider


def main() -> None:
    key = os.getenv("EMBEDDING_API_KEY")
    if not key:
        print(
            "EMBEDDING_API_KEY not set – skipping live embedding test. "
            "Add it to your environment or .env file (see .env.example)."
        )
        return

    settings = load_embedding_settings()
    settings.api_key = key  # override the placeholder
    provider = get_embedding_provider(settings)

    # --- similarity sanity check ---
    related = "Retrieval-Augmented Generation combines search with LLMs"
    unrelated = "The quick brown fox jumps over the lazy dog"

    vec_a = provider.embed_query(related)
    vec_b = provider.embed_query(unrelated)

    # simple cosine similarity
    def cosine_sim(u, v):
        if len(u) != len(v):
            raise ValueError("vectors must be same length")
        dot = sum(a * b for a, b in zip(u, v))
        norm_u = sum(a ** 2 for a in u) ** 0.5
        norm_v = sum(b ** 2 for b in v) ** 0.5
        if norm_u == 0 or norm_v == 0:
            return 0.0
        return dot / (norm_u * norm_v)

    sim = cosine_sim(vec_a, vec_b)
    print(f"Model: {provider.model}")
    print(f"Dimension: {len(vec_a)}")
    print(f"Cosine similarity (related vs unrelated): {sim:.4f}")
    print(
        f"  – related sentences should score higher (>{sim:.2f}) "
        "than unrelated inputs."
    )

    # --- basic shape checks ---
    docs = provider.embed_documents(["hello world", "goodbye world"])
    assert len(docs) == 2, "expected two document embeddings"
    assert len(docs[0]) == len(vec_a), "document and query dims must match"
    print(f"Document embeddings OK: {len(docs)} vectors of dim {len(docs[0])}")


if __name__ == "__main__":
    main()