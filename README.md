# production-rag

A production-oriented, full-stack **RAG (Retrieval-Augmented Generation) platform** — not a "chat with PDF" demo. Upload documents, index them through a transparent pipeline, ask questions, and get grounded answers with page-level citations and honest refusals when the corpus can't support an answer.

**Two ways to use this project:**

1. **As a reusable Python library** (`rag_core`) — install in your own application, no FastAPI required
2. **As a full-stack application** — Next.js frontend + FastAPI backend + Qdrant vector store

## Table of Contents

- [Using rag_core as a Library](#using-rag_core-as-a-library)
- [Using the Full-Stack Application](#using-the-full-stack-application)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Pipeline](#pipeline)
- [API](#api)
- [Testing](#testing)
- [Documentation](#documentation)

---

## Using rag_core as a Library

The `rag_core` package is a standalone, reusable Python library for building RAG systems. Install it in any Python project — no FastAPI, no web server required.

### Installation

```powershell
# Install from source (editable mode)
uv pip install -e .

# Or in your own project
uv pip install -e path/to/production-rag
```

### Quick Start

```python
from rag_core import RAGPipeline, RAGConfig

# Configure the pipeline
config = RAGConfig(
    embedding_provider="jina",
    embedding_api_key="your-jina-key",
    llm_provider="openai-compat",
    llm_api_key="your-llm-key",
    llm_base_url="https://api.groq.com/openai/v1",
    llm_model="llama-3.1-8b-instant"
)

# Initialize (providers are lazy-loaded)
pipeline = RAGPipeline(config)

# Index a document
doc = pipeline.index_document(
    file_path="./paper.pdf",
    title="Research Paper"
)
print(f"Indexed {doc.num_chunks} chunks from {doc.title}")

# Ask questions
result = pipeline.query(
    question="What are the key findings?",
    top_k=5
)

if result.refused:
    print(f"Cannot answer: {result.answer}")
else:
    print(f"Answer: {result.answer}")
    for source in result.sources:
        print(f"  [{source.citation_index}] {source.document_title} (page {source.page_number})")
```

### Features

- **Standalone** — No FastAPI dependencies; use in CLI tools, notebooks, batch jobs
- **Provider flexibility** — Swap embedding and LLM providers via configuration
- **Typed API** — Full type hints and Pydantic validation
- **Production-ready** — Deterministic IDs, idempotent indexing, error handling
- **Testable** — 177 offline tests; fake providers for unit testing

### Documentation

- **[Python Library Guide](docs/PYTHON_LIBRARY_GUIDE.md)** — Comprehensive 600+ line guide covering architecture, execution flows, configuration, design decisions, and extension patterns
- **[Examples](examples/)** — 5 runnable examples from basic usage to standalone applications
- **[Test Suite](tests/library/)** — Library-specific test suite demonstrating usage patterns

### When to Use the Library

Use `rag_core` directly when:

- Building a CLI tool or batch processor
- Integrating RAG into an existing application
- Running in Jupyter notebooks or research scripts
- You don't need a REST API or web interface
- You want full control over the RAG pipeline

---

## Using the Full-Stack Application

The full-stack application combines `rag_core` with a FastAPI backend and Next.js frontend for a complete web-based RAG platform.

### Architecture

```
PDF upload → ingestion → parsing/cleaning → chunking → embeddings → Qdrant
                                                                          ↓
Next.js frontend  ←  FastAPI  /api/ask ← retrieval ← grounded generation ←┘
  (landing, upload,       /api/documents        (citations, refusal on
   chat, sources UI)                             low confidence)
```

The backend (`backend/app/`) is a thin adapter layer that wraps `rag_core` with FastAPI routes and dependency injection. All RAG logic lives in the reusable library.

## Project Structure

```
production-rag/
├── rag_core/                        # 🆕 Reusable Python library (NO FastAPI)
│   ├── __init__.py                  # Public API: RAGPipeline, RAGConfig
│   ├── pipeline.py                  # Main RAGPipeline orchestration
│   ├── config.py                    # Settings classes for all components
│   ├── exceptions.py                # Typed domain exceptions
│   ├── models/
│   │   ├── document.py              # Document + chunk data models
│   │   └── retrieval.py             # Retrieval result models
│   ├── ingestion/
│   │   ├── ingestion_service.py     # SHA-256 dedup, per-page extraction
│   │   ├── ingestion_pipeline.py    # Orchestrates full index pipeline
│   │   └── pdf_parser.py            # PyMuPDF parsing
│   ├── chunking/
│   │   ├── text_splitter.py         # Recursive-separator splitter
│   │   └── chunking_service.py      # Char offsets, overlap, lineage
│   ├── embeddings/
│   │   ├── base.py                  # EmbeddingProvider ABC
│   │   ├── factory.py               # Provider selection by config
│   │   └── jina_provider.py         # Jina AI implementation
│   ├── llm/
│   │   ├── base.py                  # LLMProvider ABC
│   │   └── openai_compat.py         # OpenAI-compatible chat
│   ├── vector_stores/
│   │   └── vector_store.py          # Qdrant (embedded/server modes)
│   ├── retrieval/
│   │   └── retrieval_service.py     # Query → top-k chunks
│   └── generation/
│       └── generation_service.py    # Prompting, citations, refusal
├── backend/                         # FastAPI adapter (thin wrapper over rag_core)
│   └── app/
│       ├── main.py                  # FastAPI app factory, CORS, exception mapping
│       ├── api/
│       │   ├── routes.py            # All API endpoints
│       │   ├── schemas.py           # Pydantic request/response models
│       │   └── deps.py              # Dependency injection (services)
│       └── core/
│           └── config.py            # FastAPI-specific settings
├── frontend/                        # Next.js 15 + React 19 App Router
│   ├── app/
│   │   ├── page.tsx                 # Landing page
│   │   ├── console/page.tsx         # Q&A interface with citations
│   │   └── playground/page.tsx      # Document manager
│   ├── components/
│   │   ├── EvidenceDemo.tsx         # Citation UI components
│   │   └── Reveal.tsx               # Scroll-reveal animation
│   └── lib/
│       ├── api.ts                   # Typed API client (mirrors backend schemas)
│       └── site.ts                  # Site-wide constants
├── tests/
│   ├── library/                     # 🆕 Library-specific tests (35 tests)
│   │   ├── test_public_api.py       # RAGPipeline API testing
│   │   └── test_configuration.py    # Config validation
│   └── unit/                        # Component unit tests (142 tests)
├── examples/                        # 🆕 Runnable library examples
│   ├── 01_basic_usage.py            # Quickstart
│   ├── 02_advanced_configuration.py # Customization
│   ├── 03_citations_and_sources.py  # Working with results
│   ├── 04_error_handling.py         # Robust patterns
│   ├── 05_standalone_application.py # Library independence
│   └── README.md                    # Example usage guide
├── docs/
│   └── PYTHON_LIBRARY_GUIDE.md      # 🆕 Comprehensive library documentation
├── scripts/
│   └── demo_rag.py                  # Full offline pipeline demo (no keys needed)
├── pyproject.toml                   # 🆕 Package metadata for rag_core
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

**Key architectural decision:** The library (`rag_core/`) contains ALL RAG logic and has zero web framework dependencies. The backend (`backend/app/`) is a thin adapter that exposes `rag_core` via REST endpoints. This means:

- You can use `rag_core` standalone without running the FastAPI server
- The backend delegates all RAG operations to the library
- Tests for core RAG logic don't require FastAPI or HTTP mocking

## Pipeline

Every stage is a typed, modular component in `rag_core/`, each with its own offline test suite. External providers (embeddings, LLM) sit behind abstract interfaces and are switched by configuration.

| Stage | Module | What it does |
|---|---|---|
| Ingestion | `rag_core/ingestion/ingestion_service.py` | SHA-256 hashing, per-page extraction, empty-page policy |
| PDF parsing | `rag_core/ingestion/pdf_parser.py` | PyMuPDF, encrypted/corrupt detection |
| Chunking | `rag_core/chunking/text_splitter.py`, `chunking_service.py` | Recursive-separator splitter with exact char offsets and overlap; full document lineage kept |
| Embeddings | `rag_core/embeddings/` | `EmbeddingProvider` ABC + Jina AI implementation (batching, retries, backoff) |
| Vector store | `rag_core/vector_stores/vector_store.py` | Qdrant — embedded local mode **or** server mode; hash-derived point IDs (idempotent re-index), metadata filtering |
| Retrieval | `rag_core/retrieval/retrieval_service.py` | query → vector → top-k `ScoredChunk`s |
| Generation | `rag_core/generation/generation_service.py` | numbered-context prompting, `[n]` citations, refusal below confidence threshold |
| LLM | `rag_core/llm/` | OpenAI-compatible chat (Groq / OpenRouter / Cohere-compat — all have free tiers) |

## Quickstart (Full-Stack Application)

Requires Python 3.11+.

```powershell
# 1. Install dependencies
uv venv --python 3.11 .venv
uv pip install -r requirements.txt -r requirements-dev.txt

# Or install the library in editable mode
uv pip install -e .

# 2. Configuration
Copy-Item .env.example .env    # then fill in your keys (see below)

# 3. Run tests (fully offline - no keys needed)
.venv\Scripts\python.exe -m pytest -v

# 4. Start the API
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
# Interactive docs: http://127.0.0.1:8000/docs
```

### API keys (free tiers, no credit card)

| Key | Where | Used by |
|---|---|---|
| `EMBEDDING_API_KEY` | [jina.ai](https://jina.ai) → API Key | `/api/documents` (indexing) |
| `LLM_API_KEY` + `LLM_BASE_URL` + `LLM_MODEL` | e.g. [console.groq.com](https://console.groq.com) (`https://api.groq.com/openai/v1`, `llama-3.1-8b-instant`) | `/api/ask` |

Keys live in `.env` (gitignored) — never in code, tests, or logs. **The API works partially configured:** uploading needs only the embedding key; the LLM stack is built lazily on first question.

### Offline demo (no keys at all)

```powershell
# Demo the full RAG pipeline with deterministic fakes
.venv\Scripts\python.exe scripts\demo_rag.py

# Or try library examples
.venv\Scripts\python.exe examples\01_basic_usage.py
```

The script runs the full pipeline — index, retrieve, answer, refuse — with deterministic fakes. See [examples/README.md](examples/README.md) for all available examples.

## Docker

```powershell
Copy-Item .env.example .env   # add keys first
docker compose up --build
# API:    http://localhost:8000/docs
# Qdrant: http://localhost:6333
```

Compose runs Qdrant in **server mode** (`VECTOR_STORE_URL=http://qdrant:6333`) — the production shape — while local development defaults to embedded mode with zero infrastructure.

## Frontend (Next.js)

React 19 + Next.js 15 App Router in `frontend/`. Three views:

- **Landing** (`/`) — hero, feature overview, how-it-works, use cases, roadmap
- **Console** (`/console`) — question box, grounded answer with clickable `[n]` citation markers, source list with page numbers and similarity scores, refusal banner when confidence is low
- **Playground** (`/playground`) — drag-and-drop PDF upload (duplicate-hash skips shown), document table with chunk counts, per-document delete

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local   # points at http://127.0.0.1:8000
npm run dev                         # http://localhost:3000
```

Requires the backend API running. The typed API client in `frontend/lib/api.ts` mirrors the backend schemas one-to-one.

## API

| Method | Route | Description |
|---|---|---|
| GET | `/api/health` | liveness — returns `{ status, version }` |
| POST | `/api/documents` | multipart PDF upload → parse → chunk → embed → index (50 MB limit, dedup by file hash) |
| GET | `/api/documents` | list indexed documents with chunk counts |
| DELETE | `/api/documents/{id}` | remove all chunks for a document |
| POST | `/api/ask` | grounded answer + sources + `refused` flag |
| GET | `/api/stats` | collection name and total chunk count |

### Error handling

Domain exceptions are mapped to precise HTTP status codes at the app boundary — nothing below the API layer touches HTTP:

| Exception | HTTP status |
|---|---|
| `PDFParseError` | 400 |
| `NoTextExtractedError` | 422 |
| `EmbeddingError` | 502 |
| `LLMError` | 502 / 503 |
| `VectorStoreError` | 500 |

All exceptions are defined in `rag_core/exceptions.py` and mapped to HTTP status codes at the FastAPI boundary in `backend/app/main.py`.

## LLM Provider

The LLM layer (`rag_core/llm/openai_compat.py`) works with any OpenAI-compatible endpoint — the same `POST /chat/completions` shape covers Groq, OpenRouter, and Cohere's compatibility endpoint. Features:

- Exponential backoff with 3 retries on 429 / 5xx
- Lazy initialization — the client is only built when the first question arrives
- Config-only provider switching via `LLM_BASE_URL` + `LLM_MODEL`

Use the same provider in standalone library mode or through the FastAPI backend.

## Testing

177 offline tests across library and unit test suites — deterministic PDF fixtures, in-memory Qdrant, mocked HTTP transports. No test depends on a paid API.

```powershell
# Run all tests
.venv\Scripts\python.exe -m pytest -v

# Run only library tests (RAGPipeline API, configuration)
.venv\Scripts\python.exe -m pytest tests/library/ -v

# Run only unit tests (individual components)
.venv\Scripts\python.exe -m pytest tests/unit/ -v

# Run with coverage
.venv\Scripts\python.exe -m pytest --cov=rag_core --cov=backend tests/
```

**Test breakdown:**
- `tests/library/` — 35 tests for `rag_core` public API (RAGPipeline, RAGConfig, library independence)
- `tests/unit/` — 142 tests for individual components (chunking, embeddings, retrieval, generation, etc.)

All tests use deterministic fakes (`FakeEmbeddingProvider`, `FakeLLMProvider`) defined in `tests/conftest.py` for reproducible, offline testing.

## Documentation

- **[Python Library Guide](docs/PYTHON_LIBRARY_GUIDE.md)** — Comprehensive 600+ line guide covering:
  - Complete architecture and execution flows (with mermaid diagrams)
  - Public API reference and configuration options
  - Design decisions and rationale
  - Extension patterns for custom providers
  - Testing strategies and debugging tips
  - Complete build walkthrough

- **[Examples](examples/)** — 5 runnable examples with explanations:
  - Basic usage (quickstart pattern)
  - Advanced configuration (provider customization)
  - Citations and sources (working with results)
  - Error handling (robust patterns)
  - Standalone application (library independence demo)

- **[API Documentation](http://127.0.0.1:8000/docs)** — Interactive OpenAPI docs (when backend is running)

## Roadmap

- [ ] Hybrid search (dense + BM25) and reranking (Jina reranker)
- [ ] Retrieval evaluation harness (precision, recall metrics)
- [ ] CI/CD (GitHub Actions)
- [ ] Multi-user / auth layer
- [x] **Reusable Python library** (`rag_core`) with comprehensive documentation
- [x] Next.js frontend (landing page, upload UI, chat with clickable citations)
- [x] Docker Compose stack with Qdrant server mode
- [x] OpenAI-compatible LLM provider (Groq, OpenRouter)

## Project principles

**Library-first architecture** · typed data structures · modular replaceable providers · meaningful error translation at boundaries · config via env vars only · offline-deterministic tests · no technology without a reason.

---

## Contributing

This project maintains a clean separation between:
- **`rag_core/`** — Reusable library (no web framework dependencies)
- **`backend/`** — FastAPI adapter (thin wrapper exposing REST endpoints)
- **`frontend/`** — Next.js UI (consumes REST API)

When adding features:
1. Implement core logic in `rag_core/` with unit tests
2. Expose via `RAGPipeline` public API if needed
3. Add FastAPI routes in `backend/` only for web access
4. Update documentation and examples as appropriate

Run `pytest -v` before submitting changes to ensure no regressions.
