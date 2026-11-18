import Link from "next/link";
import Reveal from "@/components/Reveal";
import CopyCommand from "@/components/CopyCommand";
import EvidenceDemo from "@/components/EvidenceDemo";
import { GITHUB_URL } from "@/lib/site";

const FEATURES = [
  {
    kicker: "grounding & citations",
    title: "Page-level citations",
    desc: "Every [n] marker resolves to a file, a page, and a cosine score. Click a marker, read the exact passage the answer used.",
  },
  {
    kicker: "abstention",
    title: "Refuses when evidence is thin",
    desc: "If the top score doesn't clear the threshold, the LLM is never called. \u201cI don't know\u201d is designed behavior, not a failure mode.",
  },
  {
    kicker: "idempotency",
    title: "Re-index without duplicates",
    desc: "SHA-256 content hashes drive deterministic point IDs. Re-uploading is a no-op; deletes leave no orphans.",
  },
  {
    kicker: "portability",
    title: "Providers are configuration",
    desc: "Jina, Groq, OpenRouter — any OpenAI-compatible endpoint. Switching is an env var, not a rewrite.",
  },
  {
    kicker: "engineering",
    title: "209 offline tests",
    desc: "Deterministic suites with mocked HTTP transports. Nothing in CI ever touches a paid API.",
  },
  {
    kicker: "deployment",
    title: "Embedded or server Qdrant",
    desc: "Zero infrastructure for local work — the same codebase against a Qdrant server in production.",
  },
];

const COMPARE_ROWS: [string, string, string][] = [
  [
    "grounding",
    "Model memory, plus whatever fits in one paste",
    "Your entire corpus, retrieved per query",
  ],
  [
    "citations",
    "Vague links, if any",
    "Page-level [n] markers with similarity scores",
  ],
  [
    "no evidence",
    "Confident hallucination",
    "Abstention — the LLM is never called",
  ],
  [
    "quality control",
    "Trust it",
    "209 offline tests · eval harness on the roadmap",
  ],
];

function QuickstartCard() {
  return (
    <div className="terminal">
      <div className="terminal-bar">
        <span className="dots">
          <span />
          <span />
          <span />
        </span>
        <span className="terminal-title">quickstart.py</span>
      </div>
      <div className="terminal-body">
        <pre className="code-pre">
          <code>
            <span className="kw">from</span> rag_core <span className="kw">import</span> RAGPipeline{"\n"}
            {"\n"}
            <span className="cmt"># index a document</span>{"\n"}
            pipeline = RAGPipeline(){"\n"}
            pipeline.index_document(<span className="str">"report.pdf"</span>){"\n"}
            {"\n"}
            <span className="cmt"># ask — the answer arrives with citations</span>{"\n"}
            answer = pipeline.query(<span className="str">"What changed in v2?"</span>){"\n"}
            {"\n"}
            <span className="kw">print</span>(answer.answer){"\n"}
            <span className="cmt"># "Rate limits doubled. [1]"</span>{"\n"}
            <span className="kw">print</span>(answer.sources){"\n"}
            <span className="cmt"># [report.pdf · page 4 · 0.82]</span>
          </code>
        </pre>
      </div>
    </div>
  );
}

export default function LandingPage() {
  return (
    <>
      {/* ================= HERO ================= */}
      <section className="hero container">
        <div className="hero-grid">
          <Reveal>
            <div className="kicker-line">
              <span className="kicker">open-source retrieval pipeline</span>
              <span className="kicker-rule" />
            </div>
            <h1>RAG that shows its work.</h1>
            <p className="hero-sub">
              Upload documents, ask questions, and get answers grounded in
              retrieved passages — cited to the exact page, or refused when the
              evidence doesn’t clear the threshold. A typed, testable pipeline
              from PDF to answer.
            </p>
            <div className="hero-cta">
              <Link href="/get-started" className="btn btn-primary">
                Get started
              </Link>
              <a
                href={GITHUB_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-ghost"
              >
                View on GitHub
              </a>
            </div>
            <div className="hero-install">
              <CopyCommand
                title="shell"
                lines={[{ cmd: "pip install prod-rag" }]}
              />
            </div>
            <div className="hero-stats">
              <span className="stat-chip">
                <b>209</b> deterministic tests
              </span>
              <span className="stat-chip">
                <b>0</b> paid APIs in CI
              </span>
              <span className="stat-chip">
                <b>MIT</b> · PyPI: <b>prod-rag</b>
              </span>
            </div>
          </Reveal>
          <Reveal delay={160}>
            <QuickstartCard />
          </Reveal>
        </div>
      </section>

      {/* ================= EVIDENCE ================= */}
      <section className="section container" id="evidence">
        <Reveal>
          <div className="section-head">
            <span className="kicker">evidence</span>
            <h2>Every claim comes with a receipt.</h2>
            <p>
              A chatbot answers from memory and hopes you don’t check.
              production-rag retrieves from your corpus, cites the exact
              passages it used, and refuses when nothing retrieved is good
              enough.
            </p>
          </div>
        </Reveal>
        <Reveal delay={120}>
          <EvidenceDemo />
          <p className="demo-caption">
            example session · recorded values ·{" "}
            <a
              href="https://github.com/1divyanshdev/production-rag/tree/main/examples"
              target="_blank"
              rel="noopener noreferrer"
            >
              try it yourself on GitHub →
            </a>
          </p>
        </Reveal>
      </section>

      {/* ================= FEATURES ================= */}
      <section className="section container" id="features">
        <Reveal>
          <div className="section-head">
            <span className="kicker">design decisions</span>
            <h2>Built like infrastructure, not a demo.</h2>
            <p>
              The unglamorous parts — chunking, dedup, retries, thresholds —
              are done properly. That’s what makes the answers trustworthy.
            </p>
          </div>
        </Reveal>
        <div className="feature-grid">
          {FEATURES.map((f, i) => (
            <Reveal key={f.title} delay={i * 60}>
              <div className="feature-card">
                <span className="feature-kicker">{f.kicker}</span>
                <h3>{f.title}</h3>
                <p>{f.desc}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </section>

      {/* ================= DIFFERENCE ================= */}
      <section className="section container" id="difference">
        <Reveal>
          <div className="section-head">
            <span className="kicker">the difference</span>
            <h2>Why not just paste it into a chatbot?</h2>
            <p>
              Because a chatbot answers from memory and hopes you don’t check.
              This one answers from your corpus and shows the evidence — or
              abstains.
            </p>
          </div>
        </Reveal>
        <Reveal delay={120}>
          <div className="compare-wrap">
            <div className="table-scroll">
              <table className="compare-table">
                <thead>
                  <tr>
                    <th></th>
                    <th>Generic chatbot</th>
                    <th className="col-us">production-rag</th>
                  </tr>
                </thead>
                <tbody>
                  {COMPARE_ROWS.map(([what, them, us]) => (
                    <tr key={what}>
                      <td className="compare-what">{what}</td>
                      <td>{them}</td>
                      <td className="col-us">{us}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </Reveal>

        {/* ---- deploy + roadmap ---- */}
        <div className="deploy-block" id="deploy">
          <Reveal>
            <div className="section-head">
              <span className="kicker">deploy</span>
              <h2>Runs where you run.</h2>
              <p>
                One codebase, two topologies: an embedded vector store for
                local work, Qdrant as a server for production.
              </p>
            </div>
          </Reveal>
          <Reveal delay={120}>
            <div className="deploy-grid">
              <div className="deploy-card">
                <span className="deploy-tag">local development</span>
                <h3>Embedded mode</h3>
                <p>
                  Qdrant runs in-process with the API. No containers, no
                  services — your data never leaves the machine.
                </p>
                <div className="deploy-cmd">
                  <span className="prompt">$</span>uvicorn
                  backend.app.main:app --reload
                </div>
              </div>
              <div className="deploy-card">
                <span className="deploy-tag">production</span>
                <h3>Server mode</h3>
                <p>
                  Docker Compose runs Qdrant next to the API — the production
                  topology, one command away.
                </p>
                <div className="deploy-cmd">
                  <span className="prompt">$</span>docker compose up --build
                </div>
              </div>
            </div>
            <p className="config-note">
              every stage sits behind an abstract interface — swap embeddings,
              LLM, or vector store with <code>EMBEDDING_API_KEY</code>,{" "}
              <code>LLM_BASE_URL</code>, <code>VECTOR_STORE_URL</code>
            </p>
            <div className="roadmap">
              <span className="roadmap-kicker">on the roadmap</span>
              <div className="roadmap-items">
                <span>
                  hybrid search<em>bm25 + dense</em>
                </span>
                <span>neural reranking</span>
                <span>retrieval eval harness</span>
              </div>
              <span className="roadmap-note">
                the eval harness generates its own questions, answers them
                against the index, and scores retrieval quality — a RAG system
                that grades itself.
              </span>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ================= FINAL CTA ================= */}
      <section className="cta-final">
        <div className="cta-inner">
          <Reveal>
            <h2>Start building in five minutes.</h2>
            <p>
              Two free-tier API keys, one document indexed, and you have a
              grounded question-answering pipeline.
            </p>
            <div className="cta-install">
              <CopyCommand
                title="shell"
                lines={[{ cmd: "pip install prod-rag" }]}
              />
            </div>
            <div className="cta-actions">
              <Link href="/get-started" className="btn btn-primary">
                Get Started
              </Link>
              <a
                href="https://pypi.org/project/prod-rag/"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-ghost"
              >
                View on PyPI
              </a>
            </div>
          </Reveal>
        </div>
      </section>
    </>
  );
}
