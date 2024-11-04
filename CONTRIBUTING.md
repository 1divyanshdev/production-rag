# Contributing to Production RAG

Thank you for your interest in contributing to Production RAG! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Issues

- Use GitHub Issues to report bugs or request features
- Search existing issues before creating a new one
- Provide clear descriptions with steps to reproduce bugs
- Include your environment details (OS, Python version, etc.)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/production-rag.git
   cd production-rag
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -e ".[dev]"  # Installs library + dev tools
   ```

4. **Run tests**
   ```bash
   pytest -v
   ```

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the existing code style
   - Add tests for new features
   - Update documentation as needed

3. **Run tests and linting**
   ```bash
   pytest -v
   black .
   ruff check .
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Convention

We follow conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

Examples:
- `feat: add support for DOCX files`
- `fix: handle empty PDF pages correctly`
- `docs: update installation instructions`

### Code Style

- **Python**: Follow PEP 8, use Black for formatting
- **Line length**: 100 characters (configured in pyproject.toml)
- **Type hints**: Use type hints for all public functions
- **Docstrings**: Use Google-style docstrings

### Testing Guidelines

- Write tests for all new features
- Maintain or improve test coverage
- Use offline fakes (no real API calls in tests)
- Tests should be deterministic and fast

### Project Structure

```
production-rag/
├── rag_core/          # Reusable library (no FastAPI)
│   ├── models/        # Data models
│   ├── ingestion/     # PDF parsing, chunking
│   ├── embeddings/    # Embedding providers
│   ├── vector_stores/ # Vector storage
│   ├── retrieval/     # Semantic search
│   └── generation/    # Answer generation
├── backend/           # FastAPI web application
├── frontend/          # Next.js UI
├── tests/             # Test suite
│   ├── library/       # Library API tests
│   └── unit/          # Component tests
└── examples/          # Usage examples
```

### Adding New Features

#### Adding a New Embedding Provider

1. Create a new file in `rag_core/embeddings/`
2. Implement the `EmbeddingProvider` interface
3. Register in `factory.py`
4. Add tests in `tests/unit/`
5. Update documentation

#### Adding a New Document Format

1. Create a parser in `rag_core/ingestion/`
2. Update `ingestion_service.py` to handle the format
3. Add test fixtures and tests
4. Update README with supported formats

### Documentation

- Update README.md for user-facing changes
- Update PYTHON_LIBRARY_GUIDE.md for library changes
- Add docstrings to all public functions
- Create examples for new features

### Pull Request Process

1. Ensure all tests pass
2. Update documentation
3. Keep PRs focused (one feature/fix per PR)
4. Reference related issues
5. Wait for review and address feedback

### Getting Help

- Open an issue for questions
- Check existing documentation
- Review closed issues and PRs

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Production RAG! 🚀
