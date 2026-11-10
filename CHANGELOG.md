# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-27

### Added
- Initial release of production-rag as a standalone Python library
- RAGPipeline for end-to-end document processing and retrieval
- Multi-provider embedding support (Jina AI, OpenAI-compatible)
- Flexible LLM integration via OpenAI-compatible API
- Qdrant vector store integration
- PDF parsing and text chunking
- Semantic and hybrid search capabilities
- Comprehensive test suite (177 tests)
- Full documentation and examples
- MIT License

### Features
- **Document Ingestion**: PDF parsing with metadata extraction
- **Text Processing**: Smart chunking with configurable strategies
- **Embeddings**: Pluggable embedding providers
- **Vector Store**: Qdrant integration with collection management
- **Retrieval**: Semantic search with configurable parameters
- **Generation**: LLM-based answer generation with source citations
- **API**: FastAPI backend with REST endpoints
- **Frontend**: Next.js playground interface

### Technical
- Python 3.11+ support
- Type hints throughout
- Pydantic v2 for data validation
- Async/await support
- Environment-based configuration
- Docker and docker-compose setup

## [Unreleased]

### Planned
- Additional embedding providers (Cohere, Anthropic)
- More vector stores (Pinecone, Weaviate)
- Advanced chunking strategies
- Query optimization
- Caching layer
- Batch processing
- Monitoring and metrics
