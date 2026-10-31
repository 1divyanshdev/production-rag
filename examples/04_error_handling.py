"""
Error Handling Example
======================

This example demonstrates proper error handling when using the library:
- Configuration errors
- Document processing errors
- Provider failures
- Query validation

Run:
    python examples/04_error_handling.py
"""
import sys
import tempfile
from pathlib import Path

from rag_core import (
    RAGPipeline,
    RAGConfig,
    EmbeddingSettings,
    LLMSettings,
    VectorStoreSettings,
    # Import exception types
    PDFParseError,
    NoTextExtractedError,
    EmbeddingError,
    VectorStoreError,
    LLMError,
)


def example_configuration_errors():
    """Demonstrate configuration validation."""
    print("\n" + "=" * 70)
    print("Example 1: Configuration Errors")
    print("=" * 70)
    
    print("\n1. Missing API keys (caught at provider initialization):")
    try:
        config = RAGConfig(
            embedding_settings=EmbeddingSettings(api_key=""),
        )
        rag = RAGPipeline(config=config)
        # Error will occur when trying to use embeddings
        print("  ⚠️  Configuration accepted (error will occur at first use)")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n2. Invalid LLM configuration (caught at provider initialization):")
    try:
        config = RAGConfig(
            llm_settings=LLMSettings(
                api_key="",
                base_url="",
                model="",
            ),
        )
        rag = RAGPipeline(config=config)
        # LLM is initialized lazily, so error happens on first query
        llm = rag.llm_provider  # Force initialization
    except LLMError as e:
        print(f"  ✓ Caught LLMError: {e}")


def example_document_errors():
    """Demonstrate document processing error handling."""
    print("\n" + "=" * 70)
    print("Example 2: Document Processing Errors")
    print("=" * 70)
    
    # Initialize with minimal config for testing
    config = RAGConfig(
        embedding_settings=EmbeddingSettings(
            api_key="test-key-for-demo",
            dimension=128,  # Pre-known dimension to skip API call
        ),
        vector_store_settings=VectorStoreSettings(
            path=":memory:",  # In-memory for testing
        ),
    )
    
    # We can't actually create the pipeline without a real embedder,
    # so we'll show the error handling patterns:
    
    print("\n1. Invalid PDF file:")
    print("""
try:
    result = rag.index_document(b"not a pdf", filename="bad.pdf")
except PDFParseError as e:
    print(f"Invalid PDF: {e}")
    # Handle: log error, notify user, skip file
""")
    
    print("\n2. Encrypted or corrupt PDF:")
    print("""
try:
    result = rag.index_document("encrypted.pdf")
except PDFParseError as e:
    print(f"Cannot process PDF: {e}")
    # Handle: notify user that PDF needs to be decrypted
""")
    
    print("\n3. PDF with no extractable text (scanned images):")
    print("""
try:
    result = rag.index_document("scanned.pdf")
except NoTextExtractedError as e:
    print(f"No text found: {e}")
    # Handle: notify user that OCR is needed
""")
    
    print("\n4. File not found:")
    print("""
try:
    result = rag.index_document("nonexistent.pdf")
except FileNotFoundError as e:
    print(f"File not found: {e}")
    # Handle: validate path before calling
""")
    
    print("\n5. Missing filename for bytes input:")
    print("""
try:
    pdf_bytes = load_from_api()
    result = rag.index_document(pdf_bytes)  # Missing filename!
except ValueError as e:
    print(f"Configuration error: {e}")
    # Handle: always provide filename with bytes
""")


def example_provider_errors():
    """Demonstrate provider error handling."""
    print("\n" + "=" * 70)
    print("Example 3: Provider Errors")
    print("=" * 70)
    
    print("\n1. Embedding provider failures:")
    print("""
try:
    result = rag.index_document("document.pdf")
except EmbeddingError as e:
    print(f"Embedding failed: {e}")
    # Possible causes:
    # - Invalid API key
    # - Rate limit exceeded (429)
    # - Network timeout
    # - Malformed response
    # Handle: retry with exponential backoff, notify user
""")
    
    print("\n2. LLM provider failures:")
    print("""
try:
    result = rag.query("What is this about?")
except LLMError as e:
    print(f"LLM generation failed: {e}")
    # Possible causes:
    # - Invalid API key
    # - Model not available
    # - Rate limit exceeded
    # - Request timeout
    # Handle: retry, use fallback model, notify user
""")
    
    print("\n3. Vector store failures:")
    print("""
try:
    result = rag.index_document("document.pdf")
except VectorStoreError as e:
    print(f"Vector store error: {e}")
    # Possible causes:
    # - Qdrant server not running (server mode)
    # - Permission issues (local mode)
    # - Dimension mismatch
    # - Collection configuration error
    # Handle: check server status, verify configuration
""")


def example_query_errors():
    """Demonstrate query validation and error handling."""
    print("\n" + "=" * 70)
    print("Example 4: Query Errors")
    print("=" * 70)
    
    print("\n1. Empty question:")
    print("""
try:
    result = rag.query("")
except ValueError as e:
    print(f"Invalid query: {e}")
    # Handle: validate input before calling
""")
    
    print("\n2. Query with no indexed documents:")
    print("""
result = rag.query("What is this about?")
if result.refused:
    print("No relevant content found")
    print(result.answer)  # Contains refusal message
    # Handle: prompt user to index documents first
""")
    
    print("\n3. Query below confidence threshold:")
    print("""
result = rag.query("Unrelated question")
if result.refused:
    print(f"Confidence too low: {result.answer}")
    # The system refused to answer rather than hallucinate
    # Handle: suggest rephrasing, show that no relevant docs exist
""")


def example_robust_application():
    """Show complete error handling in a real application."""
    print("\n" + "=" * 70)
    print("Example 5: Robust Application Pattern")
    print("=" * 70)
    
    print("""
import logging
from rag_core import (
    RAGPipeline, RAGConfig,
    PDFParseError, NoTextExtractedError,
    EmbeddingError, LLMError, VectorStoreError
)

logger = logging.getLogger(__name__)


def index_document_safely(rag: RAGPipeline, filepath: str) -> dict:
    \"\"\"Index a document with comprehensive error handling.\"\"\"
    try:
        result = rag.index_document(filepath)
        
        if result.skipped_duplicate:
            return {
                "status": "skipped",
                "message": f"{result.filename} already indexed"
            }
        
        return {
            "status": "success",
            "filename": result.filename,
            "chunks": result.indexed_chunks,
            "document_id": result.document_id
        }
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {filepath}")
        return {"status": "error", "error": "file_not_found", "message": str(e)}
    
    except PDFParseError as e:
        logger.error(f"Invalid PDF: {filepath}: {e}")
        return {"status": "error", "error": "invalid_pdf", "message": str(e)}
    
    except NoTextExtractedError as e:
        logger.warning(f"No text in PDF: {filepath}")
        return {"status": "error", "error": "no_text", "message": str(e)}
    
    except EmbeddingError as e:
        logger.error(f"Embedding failed: {e}")
        return {"status": "error", "error": "embedding_failed", "message": str(e)}
    
    except VectorStoreError as e:
        logger.error(f"Vector store error: {e}")
        return {"status": "error", "error": "storage_failed", "message": str(e)}
    
    except Exception as e:
        logger.exception(f"Unexpected error indexing {filepath}")
        return {"status": "error", "error": "unexpected", "message": str(e)}


def query_safely(rag: RAGPipeline, question: str) -> dict:
    \"\"\"Query with comprehensive error handling.\"\"\"
    # Input validation
    if not question or not question.strip():
        return {"status": "error", "error": "invalid_input", 
                "message": "Question cannot be empty"}
    
    try:
        result = rag.query(question)
        
        return {
            "status": "success",
            "question": result.question,
            "answer": result.answer,
            "refused": result.refused,
            "sources": result.sources,
            "citations": result.cited_indices
        }
        
    except ValueError as e:
        logger.error(f"Invalid query: {e}")
        return {"status": "error", "error": "invalid_query", "message": str(e)}
    
    except EmbeddingError as e:
        logger.error(f"Query embedding failed: {e}")
        return {"status": "error", "error": "embedding_failed", "message": str(e)}
    
    except LLMError as e:
        logger.error(f"Answer generation failed: {e}")
        return {"status": "error", "error": "generation_failed", "message": str(e)}
    
    except Exception as e:
        logger.exception(f"Unexpected error during query")
        return {"status": "error", "error": "unexpected", "message": str(e)}


# Usage:
rag = RAGPipeline(config=RAGConfig())

# Index with error handling
result = index_document_safely(rag, "document.pdf")
if result["status"] == "success":
    print(f"Indexed {result['chunks']} chunks")
elif result["error"] == "no_text":
    print("PDF needs OCR processing")
else:
    print(f"Failed to index: {result['message']}")

# Query with error handling
result = query_safely(rag, "What is the main topic?")
if result["status"] == "success":
    if result["refused"]:
        print("No relevant information found")
    else:
        print(result["answer"])
else:
    print(f"Query failed: {result['message']}")
    """)


def main():
    print("=" * 70)
    print("Production RAG - Error Handling Examples")
    print("=" * 70)
    
    example_configuration_errors()
    example_document_errors()
    example_provider_errors()
    example_query_errors()
    example_robust_application()
    
    print("\n" + "=" * 70)
    print("💡 Key Takeaways:")
    print("=" * 70)
    print("1. Always validate configuration before creating pipeline")
    print("2. Catch specific exceptions for better error messages")
    print("3. Use try-except blocks around index_document and query")
    print("4. Check result.refused to handle low-confidence gracefully")
    print("5. Log errors for debugging and monitoring")
    print("6. Return structured error responses in applications")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
