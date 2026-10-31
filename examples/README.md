# Production RAG - Usage Examples

This directory contains practical examples demonstrating how to use the Production RAG library.

## Prerequisites

Before running these examples, make sure you have:

1. **Installed the library:**
   ```bash
   pip install -e .
   ```

2. **Set up API keys:**
   - **Embedding API**: Get a free key from [jina.ai](https://jina.ai)
   - **LLM API**: Get a free key from [Groq](https://console.groq.com), [OpenRouter](https://openrouter.ai), or similar

3. **Configure environment variables:**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Add your keys:
   EMBEDDING_API_KEY=your-jina-api-key
   LLM_API_KEY=your-llm-api-key
   LLM_BASE_URL=https://api.groq.com/openai/v1
   LLM_MODEL=llama-3.1-8b-instant
   ```

## Examples Overview

### 01_basic_usage.py
**Quick Start with the Library**

The simplest way to use Production RAG: initialize, index, and query.

```bash
python examples/01_basic_usage.py
```

**What you'll learn:**
- Initializing RAGPipeline with environment configuration
- Indexing PDF documents
- Asking questions and getting grounded answers
- Inspecting query results and citations

**Requirements:** API keys must be set in environment

---

### 02_advanced_configuration.py
**Customizing the Pipeline**

Learn how to customize every aspect of the RAG pipeline configuration.

```bash
python examples/02_advanced_configuration.py
```

**What you'll learn:**
- Custom embedding settings (model, batch size, timeout)
- Local vs. server vector store modes
- Different LLM providers (Groq, OpenRouter, Together AI)
- Fine-tuning retrieval parameters (top_k, score_threshold)
- Mixing environment and explicit configuration

**Requirements:** None (demo code, no actual API calls)

---

### 03_citations_and_sources.py
**Working with Citations**

Understand how to inspect and use source citations from query results.

```bash
python examples/03_citations_and_sources.py
```

**What you'll learn:**
- Inspecting retrieved sources and similarity scores
- Tracking which sources the LLM actually cited
- Identifying unreferenced sources
- Programmatic access to citation metadata
- Using citations in your application

**Requirements:** Indexed documents (run 01_basic_usage.py first)

---

### 04_error_handling.py
**Robust Error Handling**

Learn proper error handling patterns for production use.

```bash
python examples/04_error_handling.py
```

**What you'll learn:**
- Catching and handling specific exceptions
- Configuration validation errors
- Document processing errors (invalid PDF, no text, etc.)
- Provider failures (embedding, LLM, vector store)
- Query validation
- Building robust applications with complete error handling

**Requirements:** None (demo code showing patterns)

---

### 05_standalone_application.py
**Library Independence Demo**

See how to use the library in a standalone Python application without FastAPI.

```bash
python examples/05_standalone_application.py
```

**What you'll learn:**
- Using rag_core without any web framework
- Building CLI tools with the library
- Batch processing documents and queries
- Generating reports
- Integration patterns for workers, scripts, notebooks

**Requirements:** None (demo application structure)

---

## Example Use Cases

The examples demonstrate patterns for:

- **Web APIs**: FastAPI, Flask, Django (see backend/ for FastAPI integration)
- **CLI tools**: Document search, batch processing
- **Background workers**: Celery tasks, async job processors
- **Data pipelines**: ETL with RAG capabilities
- **Research tools**: Jupyter notebooks, analysis scripts
- **Bots**: Discord, Slack, Telegram backends
- **Desktop apps**: PyQt, Tkinter with RAG features

## Quick Reference

### Basic Pattern

```python
from rag_core import RAGPipeline, RAGConfig

# Initialize
config = RAGConfig()  # Uses environment variables
rag = RAGPipeline(config=config)

# Index a document
result = rag.index_document("document.pdf")
print(f"Indexed {result.indexed_chunks} chunks")

# Ask a question
answer = rag.query("What is the main topic?")
if not answer.refused:
    print(answer.answer)
    for source in answer.sources:
        print(f"[{source['page_number']}] {source['filename']}")
```

### With Custom Configuration

```python
from rag_core import (
    RAGPipeline, RAGConfig,
    EmbeddingSettings, VectorStoreSettings,
    LLMSettings, RetrievalSettings
)

config = RAGConfig(
    embedding_settings=EmbeddingSettings(
        api_key="your-key",
        model="jina-embeddings-v5-text-nano",
    ),
    vector_store_settings=VectorStoreSettings(
        path="./my_rag_storage",
        collection="my_docs",
    ),
    llm_settings=LLMSettings(
        api_key="your-key",
        base_url="https://api.groq.com/openai/v1",
        model="llama-3.1-8b-instant",
    ),
    retrieval_settings=RetrievalSettings(
        top_k=7,
        score_threshold=0.4,
    ),
)

rag = RAGPipeline(config=config)
```

### Error Handling

```python
from rag_core import (
    RAGPipeline,
    PDFParseError,
    EmbeddingError,
    LLMError,
)

try:
    result = rag.index_document("document.pdf")
except PDFParseError as e:
    print(f"Invalid PDF: {e}")
except EmbeddingError as e:
    print(f"Embedding failed: {e}")

try:
    answer = rag.query("What is this about?")
    if answer.refused:
        print("No relevant information found")
except LLMError as e:
    print(f"LLM failed: {e}")
```

## Troubleshooting

### "ImportError: cannot import name 'RAGPipeline'"
Install the library in editable mode:
```bash
pip install -e .
```

### "EMBEDDING_API_KEY is not set"
Set the environment variable or pass it explicitly in config:
```python
config = RAGConfig(
    embedding_settings=EmbeddingSettings(api_key="your-key")
)
```

### "LLM_API_KEY is not set"
The LLM provider is lazy-initialized, so you only need LLM keys when calling `query()`.

### "Qdrant server not running"
If using server mode, start Qdrant:
```bash
docker run -p 6333:6333 qdrant/qdrant
```
Or use local mode (default):
```python
VectorStoreSettings(path="./local_storage")  # No server needed
```

## Next Steps

1. **Start with example 01** to get basic usage working
2. **Explore example 02** to customize configuration
3. **Review example 04** to understand error handling
4. **Read the study guide**: `docs/PYTHON_LIBRARY_GUIDE.md` for deep architectural understanding

## Need Help?

- Check the main README: `../README.md`
- Read the study guide: `../docs/PYTHON_LIBRARY_GUIDE.md`
- Review tests: `../tests/library/` for more usage patterns
- Check existing issues: GitHub issues
