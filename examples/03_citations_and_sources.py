"""
Citations and Source Inspection Example
========================================

This example demonstrates how to:
- Inspect query results and source citations
- Track which sources the LLM actually cited
- Use citation metadata for your application

Run:
    python examples/03_citations_and_sources.py
"""
import sys
from pathlib import Path

from rag_core import RAGPipeline, RAGConfig


def demonstrate_citation_inspection():
    """Show how to inspect and use citations from query results."""
    print("=" * 70)
    print("Citations and Source Inspection Example")
    print("=" * 70)
    
    # For this example, we'll use fake/demo mode
    print("\n⚠️  This example requires indexed documents to work.")
    print("Run example 01_basic_usage.py first to index documents.\n")
    
    # Initialize pipeline
    config = RAGConfig()
    rag = RAGPipeline(config=config)
    
    # Check if we have content
    stats = rag.get_stats()
    if stats['total_chunks'] == 0:
        print("❌ No documents indexed. Please index documents first.")
        print("Run: python examples/01_basic_usage.py")
        return 1
    
    print(f"✓ Found {stats['total_chunks']} indexed chunks\n")
    
    # Example query
    question = input("Enter a question (or press Enter for demo): ").strip()
    if not question:
        print("\n📝 Using demo question...")
        print("⚠️  This will only work if you have relevant content indexed!\n")
        question = "What is the main topic of the document?"
    
    print(f"\n💬 Question: {question}")
    print("\n🔍 Retrieving and generating answer...\n")
    
    try:
        result = rag.query(question)
        
        # 1. Check if the system refused to answer
        print("-" * 70)
        if result.refused:
            print("⚠️  System REFUSED to answer (confidence too low)")
            print(f"\nRefusal message:\n{result.answer}\n")
            print("💡 This means the retrieved chunks weren't similar enough")
            print("   to the question (score < threshold).")
        else:
            print("✓ System PROVIDED an answer\n")
            
            # 2. Display the answer
            print(f"📝 Answer:\n{result.answer}\n")
            
            # 3. Inspect retrieved sources
            print(f"📚 Retrieved Sources ({len(result.sources)}):")
            print("-" * 70)
            for i, source in enumerate(result.sources, 1):
                print(f"\n[{i}] {source['filename']}")
                print(f"    Page: {source['page_number']}")
                print(f"    Chunk: {source['chunk_index']}")
                print(f"    Document ID: {source['document_id']}")
                print(f"    Similarity Score: {source['score']:.4f}")
            
            # 4. Check which sources were actually cited
            print("\n" + "=" * 70)
            print(f"🔗 Citations Used: {result.cited_indices}")
            print("=" * 70)
            
            if result.cited_indices:
                print("\nThe LLM cited these sources in its answer:")
                for idx in result.cited_indices:
                    if idx <= len(result.sources):
                        source = result.sources[idx - 1]
                        print(f"  [{idx}] {source['filename']}, page {source['page_number']}")
            else:
                print("\n⚠️  No citations found in answer")
                print("   (LLM didn't use [n] citation format)")
            
            # 5. Show unreferenced sources
            all_indices = set(range(1, len(result.sources) + 1))
            cited = set(result.cited_indices)
            uncited = all_indices - cited
            
            if uncited:
                print(f"\n📋 Unreferenced sources: {sorted(uncited)}")
                print("   (Retrieved but not explicitly cited by LLM)")
        
        # 6. Demonstrate programmatic use
        print("\n" + "=" * 70)
        print("💻 Programmatic Usage Example")
        print("=" * 70)
        
        print("""
# Access result fields:
question = result.question
answer = result.answer
sources = result.sources
refused = result.refused
cited_indices = result.cited_indices

# Iterate sources:
for source in result.sources:
    filename = source['filename']
    page = source['page_number']
    score = source['score']
    # ... use in your application

# Check if specific source was cited:
if 1 in result.cited_indices:
    print("Source [1] was cited!")

# Filter high-confidence sources:
high_conf_sources = [s for s in result.sources if s['score'] > 0.7]

# Group by document:
from collections import defaultdict
by_doc = defaultdict(list)
for s in result.sources:
    by_doc[s['document_id']].append(s)
        """)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


def main():
    return demonstrate_citation_inspection()


if __name__ == "__main__":
    sys.exit(main())
