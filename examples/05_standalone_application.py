"""
Standalone Application Example
===============================

This example demonstrates using the RAG library in a standalone Python
application WITHOUT FastAPI, showing that the library is truly independent.

This could be:
- A CLI tool
- A background worker
- A data processing script
- A Jupyter notebook
- Any Python application

Run:
    python examples/05_standalone_application.py
"""
import sys
import json
from pathlib import Path
from datetime import datetime

# Import ONLY from rag_core - no FastAPI, no backend imports
from rag_core import (
    RAGPipeline,
    RAGConfig,
    EmbeddingSettings,
    VectorStoreSettings,
    LLMSettings,
    RetrievalSettings,
)


class SimpleRAGApplication:
    """
    A simple standalone application using the RAG library.
    
    This demonstrates that you can build a complete application
    using only the rag_core library, without any web framework.
    """
    
    def __init__(self, storage_path: str = "./rag_data"):
        """Initialize the application."""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        print(f"📦 Initializing RAG application...")
        print(f"   Storage: {self.storage_path}")
        
        # Configure the RAG pipeline
        config = RAGConfig(
            embedding_settings=EmbeddingSettings(
                api_key="demo-key",  # Would come from environment
                dimension=128,        # For demo
            ),
            vector_store_settings=VectorStoreSettings(
                path=str(self.storage_path / "vector_store"),
                collection="documents",
            ),
            llm_settings=LLMSettings(
                api_key="demo-key",
                base_url="http://demo",
                model="demo",
            ),
            retrieval_settings=RetrievalSettings(
                top_k=5,
                score_threshold=0.35,
            ),
        )
        
        # Note: In a real application with valid API keys, this would work
        try:
            self.rag = RAGPipeline(config=config)
            print("✓ RAG pipeline initialized")
        except Exception as e:
            print(f"⚠️  Pipeline initialization skipped (demo mode): {e}")
            self.rag = None
    
    def index_directory(self, directory_path: str):
        """Index all PDF files in a directory."""
        if not self.rag:
            print("⚠️  RAG pipeline not initialized")
            return
        
        dir_path = Path(directory_path)
        if not dir_path.exists():
            print(f"❌ Directory not found: {directory_path}")
            return
        
        pdf_files = list(dir_path.glob("**/*.pdf"))
        
        if not pdf_files:
            print(f"⚠️  No PDF files found in {directory_path}")
            return
        
        print(f"\n📄 Found {len(pdf_files)} PDF files")
        print("-" * 70)
        
        results = []
        for pdf_file in pdf_files:
            print(f"\nIndexing: {pdf_file.name}...")
            try:
                result = self.rag.index_document(str(pdf_file))
                
                if result.skipped_duplicate:
                    print(f"  ⏭️  Already indexed")
                    status = "skipped"
                else:
                    print(f"  ✓ Indexed {result.indexed_chunks} chunks")
                    status = "success"
                
                results.append({
                    "file": str(pdf_file),
                    "status": status,
                    "chunks": result.indexed_chunks,
                })
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                results.append({
                    "file": str(pdf_file),
                    "status": "error",
                    "error": str(e),
                })
        
        # Save results
        results_file = self.storage_path / "indexing_results.json"
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": results,
            }, f, indent=2)
        
        print(f"\n✓ Results saved to: {results_file}")
        return results
    
    def batch_query(self, questions: list[str], output_file: str = None):
        """Process multiple questions in batch."""
        if not self.rag:
            print("⚠️  RAG pipeline not initialized")
            return
        
        print(f"\n💬 Processing {len(questions)} questions...")
        print("-" * 70)
        
        results = []
        for i, question in enumerate(questions, 1):
            print(f"\n[{i}/{len(questions)}] {question}")
            
            try:
                result = self.rag.query(question)
                
                if result.refused:
                    print("  ⚠️  Refused (low confidence)")
                else:
                    print(f"  ✓ Answered (cited {len(result.cited_indices)} sources)")
                
                results.append({
                    "question": question,
                    "answer": result.answer,
                    "refused": result.refused,
                    "sources": result.sources,
                    "citations": result.cited_indices,
                })
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
                results.append({
                    "question": question,
                    "error": str(e),
                })
        
        # Save results
        if output_file:
            output_path = Path(output_file)
        else:
            output_path = self.storage_path / "query_results.json"
        
        with open(output_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": results,
            }, f, indent=2)
        
        print(f"\n✓ Results saved to: {output_path}")
        return results
    
    def generate_report(self):
        """Generate a summary report of the indexed content."""
        if not self.rag:
            print("⚠️  RAG pipeline not initialized")
            return
        
        stats = self.rag.get_stats()
        documents = self.rag.list_documents()
        
        report = []
        report.append("=" * 70)
        report.append("RAG System Report")
        report.append("=" * 70)
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\nCollection: {stats['collection']}")
        report.append(f"Total Chunks: {stats['total_chunks']}")
        report.append(f"Total Documents: {len(documents)}")
        
        if documents:
            report.append("\n" + "-" * 70)
            report.append("Indexed Documents:")
            report.append("-" * 70)
            
            for doc in documents:
                report.append(f"\n📄 {doc['filename']}")
                report.append(f"   Document ID: {doc['document_id']}")
                report.append(f"   Pages: {doc.get('total_pages', 'N/A')}")
                report.append(f"   Chunks: {doc['chunk_count']}")
        
        report_text = "\n".join(report)
        print(report_text)
        
        # Save report
        report_file = self.storage_path / "report.txt"
        with open(report_file, 'w') as f:
            f.write(report_text)
        
        print(f"\n✓ Report saved to: {report_file}")
        return report_text


def demo_cli_application():
    """Demonstrate using the library in a CLI application."""
    print("=" * 70)
    print("Standalone RAG Application Demo")
    print("=" * 70)
    print("\nThis demonstrates using rag_core library WITHOUT FastAPI\n")
    
    # Create the application
    app = SimpleRAGApplication(storage_path="./demo_rag_storage")
    
    # Note: This is a demo, so most operations won't work without real API keys
    print("\n" + "=" * 70)
    print("What This Demonstrates:")
    print("=" * 70)
    print("✓ Import only from rag_core (no FastAPI)")
    print("✓ Initialize RAGPipeline with custom configuration")
    print("✓ Build a complete application using the library")
    print("✓ Process documents and queries programmatically")
    print("✓ Generate reports and save results")
    print("✓ Use in CLI tools, scripts, workers, notebooks, etc.")
    
    print("\n" + "=" * 70)
    print("Example Use Cases:")
    print("=" * 70)
    
    use_cases = [
        "CLI tool for document search",
        "Background worker for batch processing",
        "Data pipeline component",
        "Jupyter notebook for research",
        "Discord/Slack bot backend",
        "ETL pipeline with RAG capabilities",
        "Automated report generation",
        "Content recommendation engine",
    ]
    
    for i, use_case in enumerate(use_cases, 1):
        print(f"  {i}. {use_case}")
    
    print("\n" + "=" * 70)
    print("Library Usage Pattern:")
    print("=" * 70)
    print("""
# 1. Import from rag_core only
from rag_core import RAGPipeline, RAGConfig

# 2. Configure the pipeline
config = RAGConfig(...)
rag = RAGPipeline(config=config)

# 3. Use in your application
result = rag.index_document("doc.pdf")
answer = rag.query("What is this about?")

# 4. Integrate with your workflow
# - Save results to database
# - Send notifications
# - Generate reports
# - Trigger other processes
# - Whatever your application needs!

# No web server, no HTTP, just pure Python!
    """)
    
    print("=" * 70)
    print("\n✓ The library is truly independent and reusable!")
    print("  Use it in any Python application, not just web APIs.\n")


def main():
    demo_cli_application()
    return 0


if __name__ == "__main__":
    sys.exit(main())
