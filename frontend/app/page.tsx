import { Fragment } from "react";
import Link from "next/link";
import Reveal from "@/components/Reveal";
import CopyCommand from "@/components/CopyCommand";
import EvidenceDemo from "@/components/EvidenceDemo";
import { GITHUB_URL } from "@/lib/site";

const PIPELINE_STAGES = [
  {
    num: "01",
    name: "Parse",
    desc: "PyMuPDF per-page extraction with encrypted and corrupt file detection.",
  },
  {
    num: "02",
    name: "Chunk",
    desc: "Recursive splitting with exact character offsets and full lineage kept.",
  },
  {
    num: "03",
    name: "Embed",
    desc: "Jina AI embeddings — batched, with retries and exponential backoff.",
  },
  {
    num: "04",
    name: "Index",
    desc: "Qdrant with hash-derived point IDs. Re-indexing is idempotent.",
  },
  {
    num: "05",
    name: "Retrieve",
    desc: "Query → vector → top-k scored chunks, ranked by cosine similarity.",
  },
  {
    num: "06",
    name: "Generate",
    desc: "Numbered-context prompting with [n] citations — or a refusal.",
  },
];

const FEATURES = [
  {
    glyph: "[n]",
    title: "Page-level citations",
    desc: "Every [n] marker resolves to a file, a page, and a similarity score. Answers are auditable by design.",
  },
  {
    glyph: "∅",
    title: "Honest refusals",
    desc: "Below the confidence threshold the LLM is never called. “I don’t know” is a feature, not a failure.",
  },
  {
    glyph: "#",
    title: "Content-hash dedup",
    desc: "SHA-256 per file and hash-derived point IDs. Re-uploading never duplicates; deleting is clean.",
  },
  {
    glyph: "⇄",
    title: "Providers by config",
    desc: "Jina, Groq, OpenRouter — anything OpenAI-compatible. Switching a provider is an env var, not a rewrite.",
  },
  {
    glyph: "≡",
    title: "Embedded or server Qdrant",
    desc: "Zero-infrastructure embedded mode for local development; server mode via Docker Compose for production.",
  },
  {
    glyph: "✓",
    title: "Tested offline",
    desc: "142 deterministic tests across 9 suites, with mocked HTTP transports. No test ever calls a paid API.",
  },
];

const COMPARE_ROWS: [string, string, string][] = [
  [
    "source of answers",
    "Model memory plus whatever fits in one paste",
    "Your whole indexed corpus, retrieved per query",
  ],
  [
    "citations",
    "Vague links, if the model bothers",
    "Page-level [n] citations with similarity scores",
  ],
  [
    "missing evidence",
    "Confident hallucination",
    "Refusal — the LLM is never called",
  ],
  [
    "quality control",
    "Trust it",
    "142 offline tests · eval harness on the roadmap",
  ],
];

/**
 * The retrieval constellation: a grid of document chunks, a query node, and
 * the three passages it retrieves — wired to a grounded answer. Pure SVG +
 * CSS animations, decorative only.
 */
function HeroConstellation() {
  const cols = 11;
  const rows = 8;
  const s = 14;
  const gap = 10;
  const ox = 100;
  const oy = 44;
  const cx = (c: number) => ox + c * (s + gap) + s / 2;
  const cy = (r: number) => oy + r * (s + gap) + s / 2;
  const hits: Array<[number, number]> = [
    [2, 8],
    [4, 6],
    [6, 9],
  ];
  const answerY = oy + rows * (s + gap) + 34;

  return (
    <svg viewBox="0 0 480 400" role="img" aria-label="A query retrieving three passages from a grid of document chunks, producing a grounded answer">
      {/* chunk grid */}
      <g className="c-grid">
        {Array.from({ length: rows }).map((_, r) =>
          Array.from({ length: cols }).map((_, c) => (
            <rect
              key={`${r}-${c}`}
              x={ox + c * (s + gap)}
              y={oy + r * (s + gap)}
              width={s}
              height={s}
              rx={3}
              fill="rgba(20,23,28,0.07)"
            />
          ))
        )}
      </g>

      {/* query node */}
      <g className="c-query">
        <circle cx={44} cy={cy(3)} r={5} fill="#1d4ed8" />
        <text x={26} y={cy(3) + 26} fill="#8b9099">
          query
        </text>
      </g>

      {/* retrieval paths */}
      {hits.map(([r, c], i) => (
        <path
          key={`p${i}`}
          className={`c-path c-d${i + 1}`}
          d={`M 52 ${cy(3)} Q ${(52 + cx(c)) / 2} ${cy(3) - 46 - i * 20} ${cx(c)} ${cy(r)}`}
          stroke="#1d4ed8"
          strokeOpacity={0.45}
          strokeWidth={1.5}
          fill="none"
        />
      ))}

      {/* retrieved chunks */}
      {hits.map(([r, c], i) => (
        <g key={`h${i}`} className={`c-hit c-d${i + 3}`}>
          <rect
            x={ox + c * (s + gap)}
            y={oy + r * (s + gap)}
            width={s}
            height={s}
            rx={3}
            fill="#1d4ed8"
          />
          <text x={cx(c) + 11} y={cy(r) - 8} fill="#1d4ed8">
            {`[${i + 1}]`}
          </text>
        </g>
      ))}

      {/* evidence drops */}
      {hits.map(([r, c], i) => (
        <line
          key={`d${i}`}
          className={`c-drop c-d${i + 3}`}
          x1={cx(c)}
          y1={cy(r) + 10}
          x2={cx(c)}
          y2={answerY}
          stroke="#1d4ed8"
          strokeOpacity={0.3}
          strokeWidth={1}
          strokeDasharray="3 4"
        />
      ))}

      {/* grounded answer */}
      <g className="c-answer">
        <rect
          x={ox}
          y={answerY}
          width={cols * (s + gap) - gap}
          height={40}
          rx={10}
          fill="#ffffff"
          stroke="rgba(20,23,28,0.16)"
        />
        <text x={ox + 16} y={answerY + 25} fill="#14171c">
          grounded answer
        </text>
        <text
          x={ox + cols * (s + gap) - gap - 16}
          y={answerY + 25}
          textAnchor="end"
          fill="#1d4ed8"
        >
          [1] [2] [3]
        </text>
      </g>
    </svg>
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
              <span className="kicker">open-source rag infrastructure</span>
              <span className="kicker-rule" />
            </div>
            <h1>RAG that shows its work.</h1>
            <p className="hero-sub">
              Upload documents, ask questions, and get answers cited to the
              exact page — or refused when the evidence isn’t there. A
              transparent, testable pipeline from PDF to grounded answer.
            </p>
            <div className="hero-cta">
              <Link href="/playground" className="btn btn-primary">
                Open the playground
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
          </Reveal>
          <Reveal delay={200} className="hero-visual">
            <HeroConstellation />
          </Reveal>
        </div>
        <Reveal delay={140}>
          <div className="hero-terminal">
            <CopyCommand
              title="quickstart"
              lines={[
                {
                  cmd: "git clone https://github.com/1divyanshdev/production-rag",
                },
                {
                  cmd: "cd production-rag && uv pip install -r requirements.txt",
                },
                {
                  cmd: "uvicorn backend.app.main:app --reload",
                  comment: "→ http://127.0.0.1:8000/docs",
                },
              ]}
            />
          </div>
          <div className="hero-stats">
            <span className="stat-chip">
              <b>142</b> offline tests
            </span>
            <span className="stat-chip">
              <b>9</b> test suites
            </span>
            <span className="stat-chip">
              <b>0</b> paid APIs in CI
            </span>
            <span className="stat-chip">
              <b>2</b> free-tier API keys to run
            </span>
          </div>
        </Reveal>
      </section>

      {/* ================= EVIDENCE ================= */}
      <section className="section container" id="evidence">
        <Reveal>
          <div className="section-head">
            <span className="kicker">evidence</span>
            <h2>Every claim comes with a receipt.</h2>
            <p>
              A chatbot answers from memory. production-rag retrieves from your
              documents — and shows you exactly which passages it used, or
              admits when nothing it found was good enough.
            </p>
          </div>
        </Reveal>
        <Reveal delay={120}>
          <EvidenceDemo />
          <p className="demo-caption">
            example session · recorded values ·{" "}
            <Link href="/playground">run it live in the playground →</Link>
          </p>
        </Reveal>
      </section>

      {/* ================= PIPELINE ================= */}
      <section className="section container" id="pipeline">
        <Reveal>
          <div className="section-head">
            <span className="kicker">pipeline</span>
            <h2>A pipeline you can actually see.</h2>
            <p>
              Six typed stages, each an independently tested service. No black
              boxes between your PDF and the answer.
            </p>
          </div>
        </Reveal>
        <Reveal delay={120}>
          <div className="pipeline">
            {PIPELINE_STAGES.map((stage, i) => (
              <Fragment key={stage.num}>
                <div className="pipe-stage">
                  <div className="pipe-num">{stage.num}</div>
                  <div className="pipe-name">{stage.name}</div>
                  <p className="pipe-desc">{stage.desc}</p>
                </div>
                {i < PIPELINE_STAGES.length - 1 && (
                  <span className="pipe-arrow" aria-hidden>
                    →
                  </span>
                )}
              </Fragment>
            ))}
          </div>
          <p className="pipe-foot">
            every stage sits behind an abstract interface — swap embeddings,
            LLM, or vector store with <code>EMBEDDING_API_KEY</code>,{" "}
            <code>LLM_BASE_URL</code>, <code>VECTOR_STORE_URL</code>
          </p>
        </Reveal>
      </section>

      {/* ================= FEATURES ================= */}
      <section className="section container" id="features">
        <Reveal>
          <div className="section-head">
            <span className="kicker">features</span>
            <h2>Built like infrastructure, not a demo.</h2>
            <p>
              The boring parts are done properly — that’s what makes the
              answers trustworthy.
            </p>
          </div>
        </Reveal>
        <div className="feature-grid">
          {FEATURES.map((f, i) => (
            <Reveal key={f.title} delay={i * 70}>
              <div className="feature-card">
                <div className="feature-glyph" aria-hidden>
                  {f.glyph}
                </div>
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
              Because a generic chatbot answers from memory and hopes you don’t
              check. This one answers from your corpus and shows the evidence.
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
      </section>

      {/* ================= DEPLOY + ROADMAP ================= */}
      <section className="section container" id="deploy">
        <Reveal>
          <div className="section-head">
            <span className="kicker">deploy</span>
            <h2>Runs where you run.</h2>
            <p>
              Embedded vector store for zero-friction local work, the same
              codebase against a Qdrant server in production.
            </p>
          </div>
        </Reveal>
        <Reveal delay={120}>
          <div className="deploy-grid">
            <div className="deploy-card">
              <span className="deploy-tag">local development</span>
              <h3>Embedded mode</h3>
              <p>
                Qdrant runs embedded inside the API process. Zero
                infrastructure — data stays on your machine.
              </p>
              <div className="deploy-cmd">
                <span className="prompt">$</span>uvicorn
                backend.app.main:app --reload
              </div>
            </div>
            <div className="deploy-card">
              <span className="deploy-tag">production shape</span>
              <h3>Server mode</h3>
              <p>
                Docker Compose runs Qdrant as a server next to the API — the
                production topology, one command away.
              </p>
              <div className="deploy-cmd">
                <span className="prompt">$</span>docker compose up --build
              </div>
            </div>
          </div>
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
              the eval harness will generate its own questions, answer them,
              and score retrieval quality — a RAG system that grades itself.
            </span>
          </div>
        </Reveal>
      </section>

      {/* ================= FINAL CTA ================= */}
      <section className="cta-band">
        <div className="cta-inner">
          <Reveal>
            <h2>Index your first document in under a minute.</h2>
            <p>Free-tier API keys, no credit card. Ask a question, check the citations.</p>
            <div className="cta-actions">
              <Link href="/playground" className="btn btn-primary">
                Open the playground
              </Link>
              <a
                href={GITHUB_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-dark-ghost"
              >
                Browse the source
              </a>
            </div>
          </Reveal>
        </div>
      </section>
    </>
  );
}
