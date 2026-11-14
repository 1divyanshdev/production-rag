"use client";

import Link from "next/link";
import Reveal from "@/components/Reveal";
import CopyCommand from "@/components/CopyCommand";

export default function GetStartedPage() {
  return (
    <div className="container">
      <div className="page-head">
        <span className="kicker">get started</span>
        <h1>Install & Use in 5 Minutes</h1>
        <p className="page-sub">
          Production RAG is a Python library. Install it, bring your API keys,
          and start building.
        </p>
      </div>

      {/* Installation */}
      <section className="section">
        <Reveal>
          <div className="section-head">
            <span className="kicker">installation</span>
            <h2>Install via pip</h2>
            <p>Production RAG is published on PyPI. One command and you're ready.</p>
          </div>
        </Reveal>
        <Reveal delay={100}>
          <CopyCommand
            title="install"
            lines={[
              { cmd: "pip install prod-rag" },
            ]}
          />
          <p style={{ marginTop: "16px", color: "#6B7280", fontSize: "15px" }}>
            Requires Python 3.11+. Compatible with Windows, macOS, and Linux.
          </p>
        </Reveal>
      </section>

      {/* API Keys */}
      <section className="section">
        <Reveal>
          <div className="section-head">
            <span className="kicker">api keys</span>
            <h2>Get Your Free API Keys</h2>
            <p>
              Production RAG uses external services for embeddings and LLM. Both
              offer generous free tiers — no credit card required.
            </p>
          </div>
        </Reveal>
        <Reveal delay={100}>
          <div style={{ display: "grid", gap: "24px", marginTop: "32px" }}>
            <div
              style={{
                padding: "24px",
                border: "1px solid rgba(20,23,28,0.12)",
                borderRadius: "12px",
              }}
            >
              <h3 style={{ marginBottom: "8px" }}>
                1. Jina AI (Embeddings)
              </h3>
              <p style={{ color: "#6B7280", marginBottom: "16px" }}>
                Converts text into vector representations for semantic search.
              </p>
              <div style={{ display: "flex", gap: "12px", marginBottom: "12px" }}>
                <span style={{ fontSize: "14px" }}>
                  ✅ <strong>1M tokens/month</strong> free
                </span>
                <span style={{ fontSize: "14px" }}>
                  ⚡ <strong>Fast</strong> inference
                </span>
              </div>
              <a
                href="https://jina.ai"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-ghost"
                style={{ marginTop: "8px" }}
              >
                Get Jina AI Key →
              </a>
              <div
                style={{
                  marginTop: "16px",
                  padding: "12px",
                  background: "rgba(20,23,28,0.03)",
                  borderRadius: "6px",
                  fontSize: "13px",
                  fontFamily: "var(--font-jetbrains)",
                }}
              >
                Sign up → Dashboard → API Keys → Create
              </div>
            </div>

            <div
              style={{
                padding: "24px",
                border: "1px solid rgba(20,23,28,0.12)",
                borderRadius: "12px",
              }}
            >
              <h3 style={{ marginBottom: "8px" }}>
                2. Groq (LLM)
              </h3>
              <p style={{ color: "#6B7280", marginBottom: "16px" }}>
                Generates answers from retrieved context with citations.
              </p>
              <div style={{ display: "flex", gap: "12px", marginBottom: "12px" }}>
                <span style={{ fontSize: "14px" }}>
                  ✅ <strong>30 req/min</strong> free
                </span>
                <span style={{ fontSize: "14px" }}>
                  ⚡ <strong>Fastest</strong> LLM API
                </span>
              </div>
              <a
                href="https://console.groq.com"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-ghost"
                style={{ marginTop: "8px" }}
              >
                Get Groq Key →
              </a>
              <div
                style={{
                  marginTop: "16px",
                  padding: "12px",
                  background: "rgba(20,23,28,0.03)",
                  borderRadius: "6px",
                  fontSize: "13px",
                  fontFamily: "var(--font-jetbrains)",
                }}
              >
                Sign up → API Keys → Create new key
              </div>
            </div>
          </div>
        </Reveal>
      </section>

      {/* Quick Start Code */}
      <section className="section">
        <Reveal>
          <div className="section-head">
            <span className="kicker">quick start</span>
            <h2>Your First RAG Pipeline in 30 Seconds</h2>
            <p>Index a document and ask questions. That's it.</p>
          </div>
        </Reveal>
        <Reveal delay={100}>
          <div
            style={{
              background: "#14171c",
              color: "#fafaf7",
              padding: "24px",
              borderRadius: "12px",
              fontFamily: "var(--font-jetbrains)",
              fontSize: "14px",
              lineHeight: "1.6",
              overflow: "auto",
            }}
          >
            <pre style={{ margin: 0 }}>
              <code>{`from rag_core import RAGPipeline
from rag_core.config import EmbeddingSettings, LLMSettings

# Configure with your API keys
pipeline = RAGPipeline(
    embedding_settings=EmbeddingSettings(
        api_key="your-jina-key",
        provider="jina"
    ),
    llm_settings=LLMSettings(
        api_key="your-groq-key",
        base_url="https://api.groq.com/openai/v1",
        model="openai/gpt-oss-20b"
    )
)

# Index a document
result = pipeline.index_document("research-paper.pdf")
print(f"Indexed {result.indexed_chunks} chunks")

# Ask a question
answer = pipeline.query("What are the main findings?")

if answer.refused:
    print(f"No answer: {answer.answer}")
else:
    print(f"Answer: {answer.answer}")
    for src in answer.sources:
        print(f"  [{src.filename}] page {src.page_number}")`}</code>
            </pre>
          </div>
          <div style={{ marginTop: "16px", textAlign: "center" }}>
            <a
              href="https://github.com/1divyanshdev/production-rag/tree/main/examples"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary"
            >
              View More Examples →
            </a>
          </div>
        </Reveal>
      </section>

      {/* Common Use Cases */}
      <section className="section">
        <Reveal>
          <div className="section-head">
            <span className="kicker">use cases</span>
            <h2>What You Can Build</h2>
          </div>
        </Reveal>
        <Reveal delay={100}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: "24px", marginTop: "32px" }}>
            {[
              {
                title: "Research Assistant",
                desc: "Index academic papers, ask questions, get cited answers with page references.",
                code: "pipeline.query('What methodology did they use?')",
              },
              {
                title: "Legal Document Search",
                desc: "Search contracts and legal docs with semantic understanding, not just keywords.",
                code: "pipeline.query('What are the termination clauses?')",
              },
              {
                title: "Internal Knowledge Base",
                desc: "Company docs, wikis, and manuals — searchable and question-answerable.",
                code: "pipeline.query('How do I deploy to production?')",
              },
              {
                title: "Customer Support Bot",
                desc: "Answer customer questions from product documentation with real citations.",
                code: "pipeline.query('How do I reset my password?')",
              },
            ].map((useCase) => (
              <div
                key={useCase.title}
                style={{
                  padding: "20px",
                  border: "1px solid rgba(20,23,28,0.12)",
                  borderRadius: "10px",
                }}
              >
                <h3 style={{ fontSize: "18px", marginBottom: "8px" }}>
                  {useCase.title}
                </h3>
                <p style={{ color: "#6B7280", fontSize: "14px", marginBottom: "12px" }}>
                  {useCase.desc}
                </p>
                <code
                  style={{
                    display: "block",
                    padding: "8px 12px",
                    background: "rgba(20,23,28,0.05)",
                    borderRadius: "6px",
                    fontSize: "12px",
                    fontFamily: "var(--font-jetbrains)",
                  }}
                >
                  {useCase.code}
                </code>
              </div>
            ))}
          </div>
        </Reveal>
      </section>

      {/* Next Steps */}
      <section className="section">
        <Reveal>
          <div className="section-head">
            <span className="kicker">next steps</span>
            <h2>Dive Deeper</h2>
          </div>
        </Reveal>
        <Reveal delay={100}>
          <div style={{ display: "grid", gap: "16px", marginTop: "32px" }}>
            <a
              href="https://github.com/1divyanshdev/production-rag/blob/main/docs/PYTHON_LIBRARY_GUIDE.md"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                padding: "20px 24px",
                border: "1px solid rgba(20,23,28,0.12)",
                borderRadius: "10px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                textDecoration: "none",
                color: "inherit",
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "#1d4ed8";
                e.currentTarget.style.background = "rgba(29,78,216,0.03)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "rgba(20,23,28,0.12)";
                e.currentTarget.style.background = "transparent";
              }}
            >
              <div>
                <h3 style={{ fontSize: "18px", marginBottom: "4px" }}>
                  📖 Python Library Guide
                </h3>
                <p style={{ color: "#6B7280", fontSize: "14px", margin: 0 }}>
                  Comprehensive 600+ line guide covering architecture, configuration, and patterns
                </p>
              </div>
              <span style={{ fontSize: "24px", color: "#1d4ed8" }}>→</span>
            </a>

            <a
              href="https://github.com/1divyanshdev/production-rag/tree/main/examples"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                padding: "20px 24px",
                border: "1px solid rgba(20,23,28,0.12)",
                borderRadius: "10px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                textDecoration: "none",
                color: "inherit",
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "#1d4ed8";
                e.currentTarget.style.background = "rgba(29,78,216,0.03)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "rgba(20,23,28,0.12)";
                e.currentTarget.style.background = "transparent";
              }}
            >
              <div>
                <h3 style={{ fontSize: "18px", marginBottom: "4px" }}>
                  💻 Code Examples
                </h3>
                <p style={{ color: "#6B7280", fontSize: "14px", margin: 0 }}>
                  5 runnable examples from basic usage to advanced patterns
                </p>
              </div>
              <span style={{ fontSize: "24px", color: "#1d4ed8" }}>→</span>
            </a>

            <a
              href="https://github.com/1divyanshdev/production-rag"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                padding: "20px 24px",
                border: "1px solid rgba(20,23,28,0.12)",
                borderRadius: "10px",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                textDecoration: "none",
                color: "inherit",
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = "#1d4ed8";
                e.currentTarget.style.background = "rgba(29,78,216,0.03)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = "rgba(20,23,28,0.12)";
                e.currentTarget.style.background = "transparent";
              }}
            >
              <div>
                <h3 style={{ fontSize: "18px", marginBottom: "4px" }}>
                  🔬 View Source Code
                </h3>
                <p style={{ color: "#6B7280", fontSize: "14px", margin: 0 }}>
                  Explore the codebase, run tests, and contribute on GitHub
                </p>
              </div>
              <span style={{ fontSize: "24px", color: "#1d4ed8" }}>→</span>
            </a>
          </div>
        </Reveal>
      </section>

      {/* Trust Indicators */}
      <section className="section">
        <Reveal>
          <div
            style={{
              background: "rgba(29,78,216,0.05)",
              border: "1px solid rgba(29,78,216,0.2)",
              borderRadius: "12px",
              padding: "32px",
              textAlign: "center",
            }}
          >
            <h2 style={{ marginBottom: "16px" }}>Battle-Tested & Production-Ready</h2>
            <div
              style={{
                display: "flex",
                justifyContent: "center",
                gap: "48px",
                flexWrap: "wrap",
                marginTop: "24px",
              }}
            >
              <div>
                <div style={{ fontSize: "32px", fontWeight: "bold", color: "#1d4ed8" }}>
                  177
                </div>
                <div style={{ color: "#6B7280", fontSize: "14px" }}>
                  Tests Passing
                </div>
              </div>
              <div>
                <div style={{ fontSize: "32px", fontWeight: "bold", color: "#1d4ed8" }}>
                  0
                </div>
                <div style={{ color: "#6B7280", fontSize: "14px" }}>
                  Known Bugs
                </div>
              </div>
              <div>
                <div style={{ fontSize: "32px", fontWeight: "bold", color: "#1d4ed8" }}>
                  MIT
                </div>
                <div style={{ color: "#6B7280", fontSize: "14px" }}>
                  Open Source
                </div>
              </div>
              <div>
                <div style={{ fontSize: "32px", fontWeight: "bold", color: "#1d4ed8" }}>
                  100%
                </div>
                <div style={{ color: "#6B7280", fontSize: "14px" }}>
                  Type Safe
                </div>
              </div>
            </div>
          </div>
        </Reveal>
      </section>
    </div>
  );
}
