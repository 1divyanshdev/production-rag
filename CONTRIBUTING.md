# Contributing to Production RAG

Thank you for your interest in contributing to Production RAG! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

Before creating a bug report:
1. Check the [existing issues](https://github.com/1divyanshdev/production-rag/issues)
2. Verify the bug exists in the latest version

When reporting, include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, package version)
- Relevant code snippets or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:
1. Check if it's already been suggested
2. Provide a clear use case
3. Explain why this would be useful to most users

### Pull Requests

#### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/1divyanshdev/production-rag.git
cd production-rag

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (if available)
pre-commit install
```

#### Development Workflow

1. **Fork and Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clear, documented code
   - Follow existing code style
   - Add tests for new features
   - Update documentation

3. **Test Your Changes**
   ```bash
   # Run tests
   pytest
   
   # Run specific test file
   pytest tests/unit/test_your_feature.py
   
   # Check coverage
   pytest --cov=rag_core
   ```

4. **Commit**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```
   
   Use conventional commit messages:
   - `feat:` new feature
   - `fix:` bug fix
   - `docs:` documentation changes
   - `test:` adding tests
   - `refactor:` code refactoring
   - `chore:` maintenance tasks

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   Then create a Pull Request on GitHub with:
   - Clear title and description
   - Reference related issues
   - Screenshots (if UI changes)
   - Test results

#### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for public APIs
- Keep functions focused and small
- Use meaningful variable names

Example:
```python
from typing import List, Optional

def process_documents(
    documents: List[str],
    chunk_size: int = 512,
    overlap: Optional[int] = None
) -> List[dict]:
    """
    Process documents into chunks.
    
    Args:
        documents: List of document texts to process
        chunk_size: Maximum size of each chunk in characters
        overlap: Optional overlap between chunks
        
    Returns:
        List of processed document chunks with metadata
        
    Raises:
        ValueError: If chunk_size is less than 1
    """
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    
    # Implementation
    pass
```

#### Testing Guidelines

- Write tests for new features
- Maintain existing test coverage
- Use pytest fixtures for setup
- Mock external dependencies
- Test edge cases and error conditions

Example test:
```python
import pytest
from rag_core import RAGPipeline

def test_pipeline_initialization():
    """Test that pipeline initializes with valid config."""
    pipeline = RAGPipeline(
        embedding_model="test-model",
        vector_store_url="http://localhost:6333"
    )
    assert pipeline is not None
    assert pipeline.embedding_model == "test-model"

def test_pipeline_invalid_config():
    """Test that pipeline raises error with invalid config."""
    with pytest.raises(ValueError):
        RAGPipeline(embedding_model="")
```

#### Documentation

Update documentation when:
- Adding new features
- Changing APIs
- Fixing bugs that affect usage
- Adding examples

Documentation files:
- `README.md` - Overview and quick start
- `docs/PYTHON_LIBRARY_GUIDE.md` - Comprehensive library guide
- `docs/PUBLISHING.md` - Publishing guidelines
- Docstrings in code

### Areas for Contribution

We especially welcome contributions in:

1. **Embedding Providers**
   - Add support for Cohere, Anthropic, Hugging Face
   - Location: `rag_core/services/embeddings/`

2. **Vector Stores**
   - Add Pinecone, Weaviate, ChromaDB support
   - Location: `rag_core/services/vector_store.py`

3. **Document Parsers**
   - Support for DOCX, HTML, Markdown
   - Location: `rag_core/services/parsers/`

4. **Chunking Strategies**
   - Advanced semantic chunking
   - Context-aware splitting
   - Location: `rag_core/services/chunking_service.py`

5. **Testing**
   - Integration tests
   - Performance benchmarks
   - Location: `tests/`

6. **Documentation**
   - Usage examples
   - Tutorials
   - API reference
   - Location: `docs/`

## Questions?

- Open a [GitHub Discussion](https://github.com/1divyanshdev/production-rag/discussions)
- Join our community (if applicable)
- Email: divyansh.freelances@gmail.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
