# OpenCode Testing Protocol v2.1 - Production RAG Complete System Test

**Date:** November 2026  
**Version:** 0.1.1  
**Package:** prod-rag (PyPI)  
**Repository:** https://github.com/1divyanshdev/production-rag  

> **Changelog from v2.0 → v2.1:** Updated all code snippets to match the current API
> (RAGPipeline takes a `RAGConfig`, not keyword args; `ChunkingService.chunk_documents`
> replaces `chunk_text`; EmbeddingSettings `dimension` param avoids the eager network
> probe; test count updated to 184; `max_tokens` guidance added for reasoning models).

---

## 🎯 Testing Objectives

This protocol validates the entire production-rag ecosystem:
1. ✅ PyPI package installation and functionality
2. ✅ Core library (rag_core) with all features
3. ✅ New LLM providers (Claude, Gemini)
4. ✅ Static frontend build
5. ✅ All 184 tests passing
6. ✅ Documentation accuracy

---

## 📋 Test Environment Setup

### Prerequisites:
- Python 3.11 or 3.12
- Node.js 18+ (for frontend)
- Fresh virtual environment (no prior installations)
- API keys (free tiers):
  - Jina AI: https://jina.ai (embeddings)
  - Groq: https://console.groq.com (LLM)
  - Optional: Claude, Gemini keys for provider testing

### Setup Steps:
```bash
# 1. Create fresh test directory
mkdir test-prod-rag
cd test-prod-rag

# 2. Create virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# 3. Verify clean slate
pip list  # Should show only pip, setuptools
```

---

## 🧪 TEST SUITE 1: PyPI Package Installation

### Test 1.1: Package Availability
**Objective:** Verify package is published and downloadable from PyPI

```bash
pip index versions prod-rag
```

**Expected Output:**
```
prod-rag (0.1.1)
Available versions: 0.1.1, 0.1.0
```

**Pass Criteria:** ✅ Version 0.1.1 listed

---

### Test 1.2: Clean Installation
**Objective:** Install package without errors

```bash
pip install prod-rag
```

**Pass Criteria:**
- ✅ No errors during installation
- ✅ All dependencies installed
- ✅ Package appears in `pip list`

---

### Test 1.3: Import Test
**Objective:** Verify package imports correctly

```bash
python -c "from rag_core import RAGPipeline; print('✅ Import successful')"
```

**Pass Criteria:** ✅ No import errors

---

### Test 1.4: Module Structure
**Objective:** Verify all expected modules are available

```python
python -c "
from rag_core import RAGPipeline, RAGConfig
from rag_core.config import EmbeddingSettings, LLMSettings
from rag_core.llm import get_llm_provider, AnthropicClaudeProvider, GoogleGeminiProvider
from rag_core.models import Chunk, Document
print('✅ All modules available')
"
```

**Pass Criteria:** ✅ All imports succeed

---

## 🧪 TEST SUITE 2: Core Library Functionality

### Test 2.1: Basic Configuration
**Objective:** Test library initialization — constructor must not make network calls

Create `test_basic.py`:
```python
from rag_core import RAGPipeline, RAGConfig
from rag_core.config import EmbeddingSettings, LLMSettings

# Pass dimension=256 so the Jina dimension probe is skipped entirely.
# (Without dimension= the provider would probe Jina's API on first use,
#  which fails with a fake key.)
config = RAGConfig(
    embedding_settings=EmbeddingSettings(
        api_key="test-key",
        provider="jina",
        dimension=256,       # <-- avoids the network probe
    ),
    llm_settings=LLMSettings(
        api_key="test-key",
        base_url="https://api.groq.com/openai/v1",
        model="openai/gpt-oss-20b",
    ),
)
pipeline = RAGPipeline(config=config)

print(f"✅ Pipeline initialized")
print(f"Embedding provider: {pipeline.config.embedding_settings.provider}")
print(f"LLM model: {pipeline.config.llm_settings.model}")
```

**Run:**
```bash
python test_basic.py
```

**Expected Output:**
```
✅ Pipeline initialized
Embedding provider: jina
LLM model: openai/gpt-oss-20b
```

**Pass Criteria:** ✅ Pipeline initializes without any network calls

---

### Test 2.2: Environment Variable Loading
**Objective:** Verify .env file loading works

Create `.env`:
```
EMBEDDING_API_KEY=jina_test_key_12345
EMBEDDING_PROVIDER=jina

LLM_API_KEY=gsk_test_key_12345
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=openai/gpt-oss-20b
```

Create `test_env.py`:
```python
from rag_core.config import EmbeddingSettings, LLMSettings, load_embedding_settings, load_llm_settings

settings = load_embedding_settings()
print(f"✅ Loaded embedding key: {settings.api_key[:20]}...")
print(f"✅ Loaded provider: {settings.provider}")

llm = load_llm_settings()
print(f"✅ Loaded LLM key: {llm.api_key[:20]}...")
print(f"✅ Loaded LLM model: {llm.model}")
```

**Pass Criteria:** ✅ Environment variables loaded correctly

---

### Test 2.3: Chunking (Offline)
**Objective:** Test chunking without any API calls

Create `test_chunking.py`:
```python
from rag_core.chunking import ChunkingService
from rag_core.models.document import Document, DocumentMetadata

chunker = ChunkingService()

# Build a minimal Document object
metadata = DocumentMetadata(
    document_id="test-doc",
    filename="test.txt",
    file_type="txt",
    file_hash="a" * 64,
    file_size_bytes=200,
    page_number=1,
    total_pages=1,
)
doc = Document(
    page_content="This is a test document. It has multiple sentences. We are testing the chunking system.",
    metadata=metadata,
)

# chunk_documents takes a list of Document objects
chunks = chunker.chunk_documents([doc])

print(f"✅ Created {len(chunks)} chunk(s)")
for i, chunk in enumerate(chunks, 1):
    print(f"  Chunk {i}: {chunk.content[:60]}...")

assert len(chunks) > 0, "Should create at least one chunk"
print("✅ Chunking works correctly")
```

**Pass Criteria:**
- ✅ Chunks created
- ✅ Each chunk has content
- ✅ No errors

---

## 🧪 TEST SUITE 3: LLM Provider Testing

### Test 3.1: Provider Auto-Detection
**Objective:** Verify smart provider detection works

Create `test_providers.py`:
```python
from rag_core.llm import get_llm_provider, OpenAICompatibleLLMProvider, AnthropicClaudeProvider, GoogleGeminiProvider
from rag_core.config import LLMSettings

# Test 1: Groq (OpenAI-compatible)
groq_settings = LLMSettings(api_key="gsk_test", base_url="https://api.groq.com/openai/v1", model="openai/gpt-oss-20b")
assert isinstance(get_llm_provider(groq_settings), OpenAICompatibleLLMProvider)
print("✅ Groq detected as OpenAI-compatible")

# Test 2: Claude by model name
claude_settings = LLMSettings(api_key="sk-ant-test", base_url="https://example.com", model="claude-3-5-sonnet-20241022")
assert isinstance(get_llm_provider(claude_settings), AnthropicClaudeProvider)
print("✅ Claude detected by model name")

# Test 3: Claude by URL
claude_url = LLMSettings(api_key="sk-ant-test", base_url="https://api.anthropic.com/v1", model="any-model")
assert isinstance(get_llm_provider(claude_url), AnthropicClaudeProvider)
print("✅ Claude detected by URL")

# Test 4: Gemini by model name
gemini_settings = LLMSettings(api_key="AIza-test", base_url="https://example.com", model="gemini-1.5-flash")
assert isinstance(get_llm_provider(gemini_settings), GoogleGeminiProvider)
print("✅ Gemini detected by model name")

# Test 5: Gemini by URL
gemini_url = LLMSettings(api_key="AIza-test", base_url="https://generativelanguage.googleapis.com/v1", model="any-model")
assert isinstance(get_llm_provider(gemini_url), GoogleGeminiProvider)
print("✅ Gemini detected by URL")

print("\n🎉 All 5 provider detection tests passed!")
```

**Pass Criteria:** ✅ All 5 provider detection tests pass

---

### Test 3.2: Live LLM Test (Optional - Requires Real API Key)
**Objective:** Test actual LLM generation with Groq

> ⚠️ Only run if you have real API keys.
> Do NOT set `max_tokens` too low (< 200) — reasoning models return empty
> responses when the token budget is exhausted mid-thought.

Create `test_live_llm.py`:
```python
import os
from rag_core.llm import get_llm_provider
from rag_core.config import LLMSettings

api_key = os.getenv("LLM_API_KEY", "")
if not api_key or api_key.startswith("test"):
    print("⏭️  Skipping live LLM test (no real API key)")
    exit(0)

settings = LLMSettings(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1",
    model="openai/gpt-oss-20b",
    max_tokens=512,          # keep well above 200 for reasoning models
)
provider = get_llm_provider(settings)
response = provider.generate(
    system_prompt="You are a helpful assistant. Be concise.",
    user_prompt="Say exactly: Hello from Groq!",
)
print(f"Response: {response}")
assert response.strip(), "Response must not be empty"
print("✅ Live LLM test passed!")
```

**Pass Criteria:**
- ✅ Skips gracefully if no key
- ✅ OR generates non-empty response if key provided

---

## 🧪 TEST SUITE 4: Full Integration Test

### Test 4.1: End-to-End RAG (With Real APIs)
**Objective:** Complete RAG pipeline test — requires real Jina AI and Groq API keys

Create `test_e2e.py`:
```python
import os, tempfile, pathlib
from rag_core import RAGPipeline

jina_key = os.getenv("EMBEDDING_API_KEY", "")
llm_key  = os.getenv("LLM_API_KEY", "")

if not jina_key or not llm_key or jina_key.startswith("test"):
    print("⏭️  Skipping E2E test (requires real API keys)")
    exit(0)

print("Running End-to-End RAG test...")
pipeline = RAGPipeline()   # loads keys from .env

# Create a minimal PDF via PyMuPDF for indexing
import pymupdf
doc = pymupdf.open()
page = doc.new_page()
page.insert_text((50, 50), "Python was created by Guido van Rossum in 1991.", fontsize=12)
pdf_bytes = doc.tobytes()
doc.close()

result = pipeline.index_document(pdf_bytes, filename="python_history.pdf")
print(f"✅ Indexed {result.indexed_chunks} chunk(s)")

answer = pipeline.query("Who created Python?")
print(f"✅ Answer: {answer.answer}")
assert "Guido" in answer.answer or not answer.refused
print("✅ E2E test passed!")
```

**Pass Criteria:**
- ✅ Skips gracefully if no keys
- ✅ OR returns a cited answer if keys provided

---

## 🧪 TEST SUITE 5: Repository Tests

### Test 5.1: Clone and Run Test Suite
**Objective:** Verify all 184 tests pass

```bash
git clone https://github.com/1divyanshdev/production-rag.git
cd production-rag
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -e ".[dev]"
pytest -v --tb=short
```

**Expected Output:**
```
184 passed in XX.XXs
```

**Pass Criteria:** ✅ 184 tests pass (183 acceptable if 1 fails due to local .env)

---

### Test 5.2: Test Coverage Check

```bash
pytest --cov=rag_core --cov-report=term-missing
```

**Expected:**
- ✅ Coverage > 80%
- ✅ All major modules covered

---

## 🧪 TEST SUITE 6: Frontend Build Test

### Test 6.1: Frontend Dependencies
```bash
cd frontend
npm install
```

**Pass Criteria:** ✅ No fatal errors (audit warnings are acceptable)

---

### Test 6.2: Frontend Build
```bash
npm run build
```

**Pass Criteria:**
- ✅ Build completes without errors
- ✅ All pages generated
- ✅ No TypeScript errors

---

### Test 6.3: Frontend Pages Check

**Expected Pages:**
- ✅ `page.html` (landing page)
- ✅ `get-started/page.html`

---

## 🧪 TEST SUITE 7: Documentation Validation

### Test 7.1: README Quick Start Accuracy
Verify the README Quick Start example runs without errors (using `dimension=256` to bypass the network probe).

### Test 7.2: .env.example Completeness
**Check `.env.example` contains:**
- ✅ EMBEDDING_API_KEY
- ✅ Groq, Claude, Gemini, OpenRouter, OpenAI examples
- ✅ VECTOR_STORE settings
- ✅ RETRIEVAL settings

---

## 🧪 TEST SUITE 8: Installation from Source

### Test 8.1: Build from Source
```bash
pip install build
python -m build
```

**Expected:**
- ✅ `dist/prod_rag-0.1.1.tar.gz` created
- ✅ `dist/prod_rag-0.1.1-py3-none-any.whl` created

---

### Test 8.2: Install Built Package
```bash
pip install dist/prod_rag-0.1.1-py3-none-any.whl
python -c "from rag_core import RAGPipeline; from rag_core.llm import get_llm_provider, AnthropicClaudeProvider, GoogleGeminiProvider; print('✅ Local install works')"
```

**Pass Criteria:** ✅ Installs and all imports succeed

---

## 📊 TEST RESULTS SUMMARY TEMPLATE

```markdown
# Production RAG v0.1.1 - OpenCode Test Results

**Tester:** [Your Name/OpenCode]
**Date:** [Date]
**Environment:** Python 3.X, Node.js X.X
**Duration:** XX minutes

## Summary
- ✅ Passed: XX tests
- ❌ Failed: XX tests
- ⏭️ Skipped: XX tests
- **Overall Status:** PASS / FAIL

[Suite results...]
```

---

## 🎯 Critical Pass Criteria

1. ✅ Package installs from PyPI without errors
2. ✅ `from rag_core.llm import get_llm_provider, AnthropicClaudeProvider, GoogleGeminiProvider` works
3. ✅ All 184 tests pass (183 acceptable if 1 fails due to local .env)
4. ✅ Provider auto-detection works for all 5 cases
5. ✅ Frontend builds without errors
6. ✅ RAGPipeline constructor does **not** make network calls

---

## 📝 Notes for Tester

- **Free-tier API keys:** Jina AI (1 M tokens/month), Groq (30 req/min)
- **max_tokens:** Always use ≥ 512 for reasoning models; small values produce empty responses
- **Offline construction:** Pass `EmbeddingSettings(dimension=N)` to skip the Jina dimension probe
- **Text files:** `.txt` files are now supported alongside PDFs — test with both
- **Time estimate:** With API keys: 20–30 min; without: 10–15 min

---

## 🚀 Quick Start Command Sequence

```bash
# 1. Test PyPI install
python -m venv test_venv
test_venv\Scripts\activate    # Windows
pip install prod-rag
python -c "from rag_core import RAGPipeline; from rag_core.llm import AnthropicClaudeProvider, GoogleGeminiProvider; print('✅ Install works')"

# 2. Test repository
git clone https://github.com/1divyanshdev/production-rag.git
cd production-rag
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pytest -v --tb=short

# 3. Test frontend
cd frontend
npm install
npm run build
```
