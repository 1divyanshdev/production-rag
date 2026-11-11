# production-rag

[![PyPI version](https://img.shields.io/pypi/v/prod-rag.svg)](https://pypi.org/project/prod-rag/)
[![Tests](https://github.com/1divyanshdev/production-rag/actions/workflows/test.yml/badge.svg)](https://github.com/1divyanshdev/production-rag/actions/workflows/test.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready Python library for **Retrieval-Augmented Generation** — not a demo. Index documents, ask questions, get answers cited to the exact page, or get an honest refusal when the evidence isn't there.

```bash
pip install prod-rag
```

---

## Quick Start

```python
from rag_core import RAGPipeline, RAGConfig
from rag_core.config import EmbeddingSettings, LLMSettings

config = RAGConfig(
    embedding_settings=EmbeddingSettings(
        api_key="your-jina-key",   # jina.ai — 1M tokens/month free
        provider="jina",
    ),
    llm_settings=LLMSettings(
        api_key="your-groq-key",   # console.groq.com — 30 req/min free
        base_url="https://api.groq.com/openai/v1",
        model="openai/gpt-oss-20b",
    ),
)

pipeline = RAGPipeline(config)

# Index a PDF or .txt file
result = pipeline.index_document("paper.pdf")
print(f"Indexed {result.indexed_chunks} chunks")

# Ask a question
answer = pipeline.query("What are the key findings?")

if answer.refused:
    print("Not enough evidence to answer.")
else:
    print(answer.answer)
    for src in answer.sources:
        print(f"  [{src['index']}] {src['filename']}, page {src['page_number']}")
```

Or load keys from a `.env` file and call `RAGPipeline()` with no arguments — it auto-loads.

---

## Features

- **Page-level citations** — every `[n]` marker resolves to a filename, page number, and similarity score
- **Honest refusals** — below the confidence threshold the LLM is never called; "I don't know" is built in
- **PDF and .txt ingestion** — PyMuPDF page extraction with encrypted/corrupt file detection
- **Content-hash deduplication** — re-indexing the same file is a no-op; deleting is clean
- **Provider flexibility** — Jina embeddings; any OpenAI-compatible LLM (Groq, OpenRouter, OpenAI, Claude, Gemini)
- **Embedded or server Qdrant** — zero-infrastructure local mode; server mode via `VECTOR_STORE_URL`
- **Standalone** — no FastAPI, no web server; use in scripts, notebooks, CLI tools, or any Python app
- **Fully typed** — PEP 561 compliant (`py.typed`), Pydantic validation throughout
- **Testable** — 209 offline tests; fake providers for deterministic unit testing

---

## Installation

```bash
# From PyPI
pip install prod-rag

# From source (editable)
pip install -e .
```

Requires Python 3.11+.

---

## Configuration

All settings load from environment variables. Copy `.env.example` to `.env` and fill in your keys:

```bash
# Embeddings (required for indexing and querying)
EMBEDDING_API_KEY=your-jina-key

# LLM (required for answer generation)
LLM_API_KEY=your-llm-key
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-20b

# Vector store (optional — defaults to local embedded mode)
# VECTOR_STORE_URL=http://localhost:6333   # uncomment for server mode
```

Or pass settings explicitly via `RAGConfig` as shown in the Quick Start.

### Supported LLM providers

The LLM layer works with any OpenAI-compatible endpoint. Provider auto-detection is built in:

| Provider | `base_url` | Example model |
|---|---|---|
| Groq | `https://api.groq.com/openai/v1` | `openai/gpt-oss-20b` |
| OpenRouter | `https://openrouter.ai/api/v1` | `openai/gpt-4o-mini` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o` |
| Anthropic Claude | `https://api.anthropic.com/v1` | `claude-3-5-sonnet-20241022` |
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta` | `gemini-1.5-flash` |

---

## Project Structure

```
production-rag/
├── rag_core/                    # The library
│   ├── pipeline.py              # RAGPipeline — main public entry point
│   ├── config.py                # Settings dataclasses (all env-loadable)
│   ├── exceptions.py            # Typed domain exceptions
│   ├── ingestion/               # PDF + .txt parsing, dedup, page extraction
│   ├── chunking/                # Recursive splitter with char offsets + lineage
│   ├── embeddings/              # EmbeddingProvider ABC + Jina implementation
│   ├── llm/                     # LLMProvider ABC + OpenAI-compat + Claude + Gemini
│   ├── vector_stores/           # Qdrant (embedded and server modes)
│   ├── retrieval/               # Query → top-k ScoredChunks
│   └── generation/              # Numbered-context prompting, citations, refusal
├── frontend/                    # Static documentation site (Next.js → Vercel)
├── tests/
│   ├── library/                 # Public API tests (RAGPipeline, RAGConfig)
│   └── unit/                    # Component tests (chunking, embeddings, LLM, etc.)
├── examples/                    # 5 runnable examples
├── docs/
│   ├── PYTHON_LIBRARY_GUIDE.md  # Deep-dive architecture and usage guide
│   └── PUBLISHING.md            # PyPI release process
└── pyproject.toml
```

---

## Pipeline

```
file (PDF/.txt)
    → ingestion (SHA-256 hash, page extraction)
    → chunking  (recursive split, char offsets, overlap)
    → embedding (Jina AI, batched with retries)
    → Qdrant    (hash-derived point IDs — idempotent)

query
    → embed query
    → top-k vector search
    → score threshold check → refusal if below threshold
    → numbered-context LLM prompt
    → answer with [n] citations
```

---

## Testing

209 offline tests — deterministic PDF fixtures, in-memory Qdrant, mocked HTTP transports. No test calls a paid API.

```bash
# Run all tests
python -m pytest -v

# Library API tests only
python -m pytest tests/library/ -v

# Unit tests only
python -m pytest tests/unit/ -v

# With coverage
python -m pytest --cov=rag_core --cov-report=term-missing
```

---

## Examples

Five runnable examples in [`examples/`](examples/):

| File | What it shows |
|---|---|
| `01_basic_usage.py` | Quickstart — index a PDF, ask questions |
| `02_advanced_configuration.py` | Provider customization and settings |
| `03_citations_and_sources.py` | Working with answer sources |
| `04_error_handling.py` | Robust error handling patterns |
| `05_standalone_application.py` | Building a CLI tool with the library |

---

## Documentation

- **[Python Library Guide](docs/PYTHON_LIBRARY_GUIDE.md)** — full architecture walkthrough, execution flows, design decisions, extension patterns, debugging tips
- **[Examples README](examples/README.md)** — guide to running the examples

---

## Roadmap

- [ ] Hybrid search (dense + BM25) and reranking
- [ ] Retrieval evaluation harness
- [ ] Multi-modal support (images, tables in PDFs)
- [x] Claude and Gemini provider support
- [x] `.txt` file ingestion alongside PDF
- [x] PEP 561 `py.typed` marker
- [x] Lazy embedding dimension probe (offline construction)
- [x] 209 offline tests

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Core principle: all RAG logic lives in `rag_core/` with zero web framework dependencies. Run `pytest -v` before submitting.

## License

MIT — see [LICENSE](LICENSE).
