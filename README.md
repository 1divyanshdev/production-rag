# production-rag

A production-oriented, full-stack **RAG (Retrieval-Augmented Generation) platform** — not a "chat with PDF" demo. Upload documents, index them through a transparent pipeline, ask questions, and get grounded answers with page-level citations and honest refusals when the corpus can't support an answer.

## Architecture

```
PDF upload → ingestion → parsing/cleaning → chunking → embeddings → Qdrant
                                                                          ↓
Next.js frontend  ←  FastAPI  /api/ask ← retrieval ← grounded generation ←┘
  (landing, upload,       /api/documents        (citations, refusal on
   chat, sources UI)                             low confidence)
```

Every stage is a typed, modular service under `backend/app/services/`, each with its own offline test suite. External providers (embeddings, LLM) sit behind abstract interfaces and are switched by environment config.

## Project Structure

```
production-rag/
├── backend/
│   └── app/
│       ├── main.py                  # FastAPI app factory, CORS, exception mapping
│       ├── api/
│       │   ├── routes.py            # All API endpoints
│       │   ├── schemas.py           # Pydantic request/response models
│       │   └── deps.py              # Dependency injection (services)
│       ├── core/
│       │   ├── config.py            # Settings via env vars
│       │   └── exceptions.py        # Typed domain exceptions
│       ├── models/
│       │   ├── document.py          # Document + chunk data models
│       │   └── retrieval.py         # Retrieval result models
│       └── services/
│           ├── ingestion_service.py # SHA-256 dedup, per-page extraction
│           ├── ingestion_pipeline.py# Orchestrates the full index pipeline
│           ├── pdf_parser.py        # PyMuPDF, encrypted/corrupt detection
│           ├── text_splitter.py     # Recursive-separator splitter
│           ├── chunking_service.py  # Char offsets, overlap, lineage
│           ├── retrieval_service.py # query → vector → top-k ScoredChunks
│           ├── generation_service.py# Prompting, [n] citations, refusal logic
│           ├── vector_store.py      # Qdrant embedded/server, idempotent indexing
│           ├── embeddings/
│           │   ├── base.py          # EmbeddingProvider ABC
│           │   ├── factory.py       # Provider selection by config
│           │   └── jina_provider.py # Jina AI (batching, retries, backoff)
│           └── llm/
│               ├── base.py          # LLMProvider ABC
│               └── openai_compat.py # OpenAI-compatible chat (Groq, OpenRouter…)
├── frontend/                        # Next.js 15 + React 19 App Router
│   ├── app/
│   │   ├── page.tsx                 # Landing page
│   │   ├── ask/page.tsx             # Q&A interface with citations
│   │   └── documents/page.tsx       # Document manager
│   ├── components/
│   │   ├── mockups.tsx              # UI mockup components
│   │   └── Reveal.tsx               # Scroll-reveal animation
│   └── lib/
│       ├── api.ts                   # Typed API client (mirrors backend schemas)
│       └── site.ts                  # Site-wide constants
├── tests/
│   └── unit/                        # 142 offline tests across 9 suites
├── scripts/
│   └── demo_rag.py                  # Full offline pipeline demo (no keys needed)
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Pipeline

| Stage | Module | What it does |
|---|---|---|
| Ingestion | `services/ingestion_service.py` | SHA-256 hashing, per-page extraction, empty-page policy |
| PDF parsing | `services/pdf_parser.py` | PyMuPDF, encrypted/corrupt detection |
| Chunking | `services/text_splitter.py`, `services/chunking_service.py` | Recursive-separator splitter with exact char offsets and overlap; full document lineage kept |
| Embeddings | `services/embeddings/` | `EmbeddingProvider` ABC + Jina AI implementation (batching, retries, backoff) |
| Vector store | `services/vector_store.py` | Qdrant — embedded local mode **or** server mode; hash-derived point IDs (idempotent re-index), metadata filtering |
| Retrieval | `services/retrieval_service.py` | query → vector → top-k `ScoredChunk`s |
| Generation | `services/generation_service.py` | numbered-context prompting, `[n]` citations, refusal below confidence threshold |
| LLM | `services/llm/` | OpenAI-compatible chat (Groq / OpenRouter / Cohere-compat — all have free tiers) |

## Quickstart

Requires Python 3.11.

```powershell
# 1. Environment
uv venv --python 3.11 .venv
uv pip install -r requirements.txt -r requirements-dev.txt

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
.venv\Scripts\python.exe scripts\demo_rag.py
```

Runs the full pipeline — index, retrieve, answer, refuse — with deterministic fakes.

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
- **Ask** (`/ask`) — question box, grounded answer with clickable `[n]` citation markers, source list with page numbers and similarity scores, refusal banner when confidence is low
- **Documents** (`/documents`) — drag-and-drop PDF upload (duplicate-hash skips shown), document table with chunk counts, per-document delete

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

## LLM Provider

The LLM layer (`services/llm/openai_compat.py`) works with any OpenAI-compatible endpoint — the same `POST /chat/completions` shape covers Groq, OpenRouter, and Cohere's compatibility endpoint. Features:

- Exponential backoff with 3 retries on 429 / 5xx
- Lazy initialization — the client is only built when the first question arrives
- Config-only provider switching via `LLM_BASE_URL` + `LLM_MODEL`

## Testing

142 offline tests across 9 suites — deterministic PDF fixtures, in-memory Qdrant, mocked HTTP transports. No test depends on a paid API.

```powershell
.venv\Scripts\python.exe -m pytest -v
```

## Roadmap

- [ ] Hybrid search (dense + BM25) and reranking (Jina reranker)
- [ ] Retrieval evaluation harness (precision, recall metrics)
- [ ] CI/CD (GitHub Actions)
- [ ] Multi-user / auth layer
- [x] Next.js frontend (landing page, upload UI, chat with clickable citations)
- [x] Docker Compose stack with Qdrant server mode
- [x] OpenAI-compatible LLM provider (Groq, OpenRouter)

## Project principles

Typed data structures · modular replaceable providers · meaningful error translation at boundaries · config via env vars only · offline-deterministic tests · no technology without a reason.
