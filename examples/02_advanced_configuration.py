"""
Advanced Configuration Example
==============================

This example shows how to customize the RAG pipeline configuration:
- Custom embedding settings
- Custom vector store settings (local or server mode)
- Custom LLM settings
- Custom retrieval parameters

Run:
    python examples/02_advanced_configuration.py
"""
import sys
from pathlib import Path

from rag_core import (
    RAGPipeline,
    RAGConfig,
    EmbeddingSettings,
    VectorStoreSettings,
    LLMSettings,
    RetrievalSettings,
)


def example_local_vector_store():
    """Example 1: Using a custom local vector store path."""
    print("\n" + "=" * 70)
    print("Example 1: Custom Local Vector Store")
    print("=" * 70)
    
    config = RAGConfig(
        embedding_settings=EmbeddingSettings(
            api_key="your-embedding-key",
            model="jina-embeddings-v5-text-nano",
            batch_size=32,
        ),
        vector_store_settings=VectorStoreSettings(
            path="./my_custom_rag_storage",  # Custom local path
            collection="my_documents",       # Custom collection name
        ),
        llm_settings=LLMSettings(
            api_key="your-llm-key",
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.1-8b-instant",
            temperature=0.1,
            max_tokens=1024,
        ),
        retrieval_settings=RetrievalSettings(
            top_k=10,                    # Retrieve more chunks
            score_threshold=0.3,         # Lower threshold for more lenient matching
        ),
    )
    
    rag = RAGPipeline(config=config)
    print(f"✓ Pipeline created with local storage at: ./my_custom_rag_storage")
    print(f"  Collection: my_documents")
    print(f"  Top-K: 10, Threshold: 0.3")
    
    return rag


def example_server_vector_store():
    """Example 2: Using a Qdrant server (Docker or cloud)."""
    print("\n" + "=" * 70)
    print("Example 2: Qdrant Server Mode")
    print("=" * 70)
    
    config = RAGConfig(
        embedding_settings=EmbeddingSettings(
            api_key="your-embedding-key",
        ),
        vector_store_settings=VectorStoreSettings(
            url="http://localhost:6333",     # Qdrant server URL
            api_key="",                       # Optional API key for Qdrant Cloud
            collection="production_rag",
        ),
        llm_settings=LLMSettings(
            api_key="your-llm-key",
            base_url="https://api.groq.com/openai/v1",
            model="llama-3.1-70b-versatile",  # Larger model
            temperature=0.0,                   # More deterministic
        ),
    )
    
    # Note: This requires a running Qdrant server
    # Start one with: docker run -p 6333:6333 qdrant/qdrant
    print("⚠️  This requires a running Qdrant server at http://localhost:6333")
    print("   Start with: docker run -p 6333:6333 qdrant/qdrant")
    
    # Uncomment to actually create the pipeline:
    # rag = RAGPipeline(config=config)
    # print(f"✓ Pipeline created with Qdrant server mode")
    
    return None


def example_custom_retrieval():
    """Example 3: Fine-tuning retrieval behavior."""
    print("\n" + "=" * 70)
    print("Example 3: Custom Retrieval Settings")
    print("=" * 70)
    
    # High precision: retrieve fewer, more relevant chunks
    high_precision_config = RAGConfig(
        retrieval_settings=RetrievalSettings(
            top_k=3,                 # Fewer chunks
            score_threshold=0.5,     # Higher threshold
        ),
    )
    
    # High recall: retrieve more chunks, accept lower similarity
    high_recall_config = RAGConfig(
        retrieval_settings=RetrievalSettings(
            top_k=20,                # More chunks
            score_threshold=0.2,     # Lower threshold
        ),
    )
    
    print("High Precision Setup:")
    print("  - top_k=3, score_threshold=0.5")
    print("  - Good for: When you need very accurate answers")
    
    print("\nHigh Recall Setup:")
    print("  - top_k=20, score_threshold=0.2")
    print("  - Good for: Exploratory queries, research")
    
    return high_precision_config, high_recall_config


def example_different_llm_providers():
    """Example 4: Using different LLM providers."""
    print("\n" + "=" * 70)
    print("Example 4: Different LLM Providers")
    print("=" * 70)
    
    providers = {
        "Groq (Free)": {
            "base_url": "https://api.groq.com/openai/v1",
            "models": ["llama-3.1-8b-instant", "llama-3.1-70b-versatile"],
            "signup": "https://console.groq.com",
        },
        "OpenRouter": {
            "base_url": "https://openrouter.ai/api/v1",
            "models": ["meta-llama/llama-3.1-8b-instruct:free", "google/gemma-2-9b-it:free"],
            "signup": "https://openrouter.ai",
        },
        "Together AI": {
            "base_url": "https://api.together.xyz/v1",
            "models": ["meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"],
            "signup": "https://together.ai",
        },
    }
    
    for provider, info in providers.items():
        print(f"\n{provider}:")
        print(f"  Base URL: {info['base_url']}")
        print(f"  Example models: {', '.join(info['models'][:2])}")
        print(f"  Sign up: {info['signup']}")
    
    # Example configuration for OpenRouter
    openrouter_config = RAGConfig(
        llm_settings=LLMSettings(
            api_key="your-openrouter-key",
            base_url="https://openrouter.ai/api/v1",
            model="meta-llama/llama-3.1-8b-instruct:free",
        ),
    )
    
    print("\n✓ Any OpenAI-compatible endpoint works!")


def example_environment_override():
    """Example 5: Mixing environment and explicit configuration."""
    print("\n" + "=" * 70)
    print("Example 5: Environment + Explicit Config")
    print("=" * 70)
    
    # Use environment for some settings, explicit for others
    config = RAGConfig(
        # Load embedding settings from environment
        embedding_settings=None,  # Will use EMBEDDING_API_KEY, etc.
        
        # Override vector store settings explicitly
        vector_store_settings=VectorStoreSettings(
            path="./custom_path",
            collection="special_collection",
        ),
        
        # Load LLM settings from environment
        llm_settings=None,  # Will use LLM_API_KEY, LLM_BASE_URL, etc.
        
        # Override retrieval settings
        retrieval_settings=RetrievalSettings(top_k=7),
    )
    
    print("✓ Flexible configuration:")
    print("  - Embedding: from environment")
    print("  - Vector store: custom local path")
    print("  - LLM: from environment")
    print("  - Retrieval: custom top_k=7")


def main():
    print("=" * 70)
    print("Production RAG - Advanced Configuration Examples")
    print("=" * 70)
    print("\nThis script demonstrates various configuration options.")
    print("No actual API calls are made - these are configuration examples.")
    
    # Run examples
    example_local_vector_store()
    example_server_vector_store()
    example_custom_retrieval()
    example_different_llm_providers()
    example_environment_override()
    
    print("\n" + "=" * 70)
    print("💡 Tips:")
    print("=" * 70)
    print("1. Start with defaults, then customize what you need")
    print("2. Use environment variables for secrets (API keys)")
    print("3. Use explicit config for application-specific settings")
    print("4. Local vector store is zero-infrastructure for development")
    print("5. Server mode (Docker/Cloud) is better for production")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
