"use client";

import Reveal from "@/components/Reveal";
import CopyCommand from "@/components/CopyCommand";

export default function GetStartedPage() {
  return (
    <div className="container">
      <div className="page-head">
        <span className="kicker">get started</span>
        <h1>From pip to first answer in five minutes</h1>
        <p className="page-sub">
          A Python library: install it, bring two free API keys, index a PDF,
          ask a question.
        </p>
      </div>

      {/* Installation */}
      <section className="section">
        <Reveal>
          <div className="section-head">
            <span className="kicker">installation</span>
            <h2>Install via pip</h2>
            <p>One command. Python 3.11+, any OS.</p>
          </div>
        </Reveal>
        <Reveal delay={100}>
          <CopyCommand
            title="install"
            lines={[{ cmd: "pip install prod-rag" }]}
          />
          <p className="gs-note">
            Requires Python 3.11+. Compatible with Windows, macOS, and Linux.
          </p>
        </Reveal>
      </section>

      {/* API Keys */}
      <section className="section">
        <Reveal>
          <div className="section-head">
            <span className="kicker">api keys</span>
            <h2>Bring two free-tier keys</h2>
            <p>
              Embeddings and generation both run on generous free tiers — no
              credit card required.
            </p>
          </div>
        </Reveal>
        <Reveal delay={100}>
          <div className="gs-grid-2">
            <div className="key-card">
              <h3>1. Jina AI — embeddings</h3>
              <p>
                Converts text into vector representations for semantic search.
              </p>
              <div className="key-perks">
                <span className="key-perk">
                  <b>1M tokens/month</b> free
                </span>
                <span className="key-perk">
                  <b>Fast</b> inference
                </span>
              </div>
              <a
                href="https://jina.ai"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-ghost"
              >
                Get a Jina AI key →
              </a>
              <div className="key-steps">
                Sign up → Dashboard → API Keys → Create
              </div>
            </div>

            <div className="key-card">
              <h3>2. Groq — generation</h3>
              <p>
                Generates answers from retrieved context, with citations.
              </p>
              <div className="key-perks">
                <span className="key-perk">
                  <b>30 req/min</b> free
                </span>
                <span className="key-perk">
                  <b>Fastest</b> LLM API
                </span>
              </div>
              <a
                href="https://console.groq.com"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-ghost"
              >
                Get a Groq key →
              </a>
              <div className="key-steps">
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
            <h2>Your first pipeline in 30 seconds</h2>
            <p>Index a document, ask a question. That’s the whole loop.</p>
          </div>
        </Reveal>
        <Reveal delay={100}>
          <div className="gs-codeblock">
            <pre>
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
          <div className="gs-center">
            <a
              href="https://github.com/1divyanshdev/production-rag/tree/main/examples"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary"
            >
              View more examples →
            </a>
          </div>
        </Reveal>
      </section>

      {/* Common Use Cases */}
      <section className="section">
        <Reveal>
          <div className="section-head">
            <span className="kicker">use cases</span>
            <h2>What you can build</h2>
          </div>
        </Reveal>
        <Reveal delay={100}>
          <div className="uc-grid">
            {[
              {
                title: "Research assistant",
                desc: "Index academic papers, ask questions, get cited answers with page references.",
                code: "pipeline.query('What methodology did they use?')",
              },
              {
                title: "Legal document search",
                desc: "Search contracts and legal docs with semantic understanding, not just keywords.",
                code: "pipeline.query('What are the termination clauses?')",
              },
              {
                title: "Internal knowledge base",
                desc: "Company docs, wikis, and manuals — searchable and question-answerable.",
                code: "pipeline.query('How do I deploy to production?')",
              },
              {
                title: "Customer support bot",
                desc: "Answer customer questions from product documentation with real citations.",
                code: "pipeline.query('How do I reset my password?')",
              },
            ].map((useCase) => (
              <div key={useCase.title} className="uc-card">
                <h3>{useCase.title}</h3>
                <p>{useCase.desc}</p>
                <code className="uc-code">{useCase.code}</code>
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
            <h2>Dive deeper</h2>
          </div>
        </Reveal>
        <Reveal delay={100}>
          <div className="next-list">
            <a
              href="https://github.com/1divyanshdev/production-rag/blob/main/docs/PYTHON_LIBRARY_GUIDE.md"
              target="_blank"
              rel="noopener noreferrer"
              className="next-link"
            >
              <div>
                <h3>Python library guide</h3>
                <p>
                  Comprehensive guide covering architecture, configuration, and
                  usage patterns.
                </p>
              </div>
              <span className="next-arrow" aria-hidden>→</span>
            </a>

            <a
              href="https://github.com/1divyanshdev/production-rag/tree/main/examples"
              target="_blank"
              rel="noopener noreferrer"
              className="next-link"
            >
              <div>
                <h3>Code examples</h3>
                <p>
                  Five runnable examples, from basic usage to advanced
                  patterns.
                </p>
              </div>
              <span className="next-arrow" aria-hidden>→</span>
            </a>

            <a
              href="https://github.com/1divyanshdev/production-rag"
              target="_blank"
              rel="noopener noreferrer"
              className="next-link"
            >
              <div>
                <h3>Source code</h3>
                <p>
                  Explore the codebase, run the test suites, and contribute on
                  GitHub.
                </p>
              </div>
              <span className="next-arrow" aria-hidden>→</span>
            </a>
          </div>
        </Reveal>
      </section>

      <div style={{ height: "48px" }} />
    </div>
  );
}
