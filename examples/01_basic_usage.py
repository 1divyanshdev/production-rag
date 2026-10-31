"""
Basic Usage Example for Production RAG Library
===============================================

This example demonstrates the simplest way to use the Production RAG library:
1. Initialize the pipeline with environment-based configuration
2. Index a PDF document
3. Ask questions and get grounded answers

Prerequisites:
- Set EMBEDDING_API_KEY environment variable (get free key from jina.ai)
- Set LLM_API_KEY, LLM_BASE_URL, LLM_MODEL (e.g., Groq free tier)
- Have a PDF file to index

Run:
    python examples/01_basic_usage.py
"""
import os
import sys
from pathlib import Path

# Optional: Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from rag_core import RAGPipeline, RAGConfig


def main():
    print("=" * 70)
    print("Production RAG - Basic Usage Example")
    print("=" * 70)
    
    # Check for required environment variables
    if not os.getenv("EMBEDDING_API_KEY"):
        print("\n❌ ERROR: EMBEDDING_API_KEY environment variable not set")
        print("Get a free API key from: https://jina.ai")
        return 1
    
    if not os.getenv("LLM_API_KEY"):
        print("\n❌ ERROR: LLM_API_KEY environment variable not set")
        print("Get a free API key from: https://console.groq.com")
        return 1
    
    # Initialize RAG pipeline with default configuration (from environment)
    print("\n📦 Initializing RAG pipeline...")
    config = RAGConfig()
    rag = RAGPipeline(config=config)
    print("✓ Pipeline initialized")
    
    # Get stats about the current index
    stats = rag.get_stats()
    print(f"\n📊 Current index: {stats['total_chunks']} chunks in '{stats['collection']}'")
    
    # Check if there are any documents already indexed
    docs = rag.list_documents()
    if docs:
        print(f"\n📄 Already indexed documents:")
        for doc in docs:
            print(f"  - {doc['filename']}: {doc['chunk_count']} chunks")
    
    # Example: Index a document (you'll need to provide a real PDF path)
    pdf_path = input("\n📄 Enter path to a PDF file to index (or press Enter to skip): ").strip()
    
    if pdf_path and Path(pdf_path).exists():
        print(f"\n🔄 Indexing {pdf_path}...")
        try:
            result = rag.index_document(pdf_path)
            
            if result.skipped_duplicate:
                print(f"⏭️  Document already indexed (skipped)")
            else:
                print(f"✓ Indexed successfully!")
                print(f"  - Filename: {result.filename}")
                print(f"  - Chunks: {result.indexed_chunks}")
                print(f"  - Document ID: {result.document_id}")
        except Exception as e:
            print(f"❌ Error indexing document: {e}")
            return 1
    else:
        if pdf_path:
            print(f"❌ File not found: {pdf_path}")
        print("⏭️  Skipping indexing")
    
    # Check if we have any content to query
    stats = rag.get_stats()
    if stats['total_chunks'] == 0:
        print("\n⚠️  No documents indexed. Please index a document first.")
        return 0
    
    # Ask questions
    print("\n" + "=" * 70)
    print("💬 Question Answering")
    print("=" * 70)
    print("Enter questions to ask about the indexed documents.")
    print("Type 'quit' or 'exit' to stop.\n")
    
    while True:
        question = input("❓ Question: ").strip()
        
        if not question:
            continue
        
        if question.lower() in ('quit', 'exit', 'q'):
            break
        
        try:
            print("\n🤔 Thinking...")
            result = rag.query(question)
            
            print("\n" + "-" * 70)
            if result.refused:
                print("⚠️  REFUSED (low confidence)")
                print(f"\n📝 Answer:\n{result.answer}")
            else:
                print("✓ ANSWERED")
                print(f"\n📝 Answer:\n{result.answer}")
                
                if result.sources:
                    print(f"\n📚 Sources ({len(result.sources)}):")
                    for i, source in enumerate(result.sources, 1):
                        print(f"  [{i}] {source['filename']}, page {source['page_number']} "
                              f"(score: {source['score']:.3f})")
                
                if result.cited_indices:
                    print(f"\n🔗 Citations used: {result.cited_indices}")
            
            print("-" * 70 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
    
    print("\n👋 Goodbye!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
