import Link from "next/link";
import Reveal from "@/components/Reveal";
import {
  AppMockup,
  DedupMockup,
  MatchFlowMockup,
  RefusalMockup,
  SourcesMockup,
} from "@/components/mockups";
import { GITHUB_URL } from "@/lib/site";

const icon = (path: React.ReactNode) =>
  function Icon() {
    return (
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {path}
      </svg>
    );
  };

const IconCheck = icon(<path d="M20 6 9 17l-5-5" />);
const IconSpark = icon(<path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1" />);
const IconPuzzle = icon(<path d="M14 7V5a2 2 0 1 1 4 0v2h2a1 1 0 0 1 1 1v3h-2a2 2 0 1 0 0 4h2v3a1 1 0 0 1-1 1h-3v-2a2 2 0 1 0-4 0v2H7a1 1 0 0 1-1-1v-3H4a2 2 0 1 1 0-4h2V8a1 1 0 0 1 1-1h3V5" />);
const IconCompass = icon(<><circle cx="12" cy="12" r="9" /><path d="m15.5 8.5-2 5-5 2 2-5 5-2z" /></>);
const IconLock = icon(<><rect x="5" y="11" width="14" height="9" rx="2" /><path d="M8 11V7a4 4 0 1 1 8 0v4" /></>);
const IconRocket = icon(<><path d="M5 13c-1.5 1.5-2 5-2 5s3.5-.5 5-2" /><path d="M12 15l-3-3a12 12 0 0 1 8-9c1 0 2 1 2 2a12 12 0 0 1-9 8z" /><path d="M9 12H6s.3-2 1.5-3.5C9 7 11 7 11 7" /><path d="M12 15v3s2-.3 3.5-1.5C17 15 17 13 17 13" /></>);

export default function LandingPage() {
  return (
    <>
      {/* ================= HERO ================= */}
      <section className="hero container">
        <Reveal>
          <h1>
            Stop searching. <em>Start asking.</em>
            <br />
            Answers <span className="accent">with receipts.</span>
          </h1>
        </Reveal>
        <Reveal delay={120}>
          <p className="hero-sub">
            A full-stack RAG platform that reads your PDFs and answers
            questions grounded in the retrieved context — cited to exact
            pages, or honestly refused when the evidence isn&apos;t there.
          </p>
        </Reveal>
        <Reveal delay={220}>
          <div className="hero-cta">
            <Link href="/ask" className="btn-primary">
              Get Started — it&apos;s free
            </Link>
            <a href="#how-it-works" className="btn-white">
              Learn More
            </a>
          </div>
        </Reveal>
        <Reveal delay={320}>
          <div className="mockup-wrap">
            <AppMockup />
          </div>
        </Reveal>
      </section>

      {/* ================= WHY ================= */}
      <section className="block container" id="why">
        <Reveal>
          <div className="section-head">
            <h2>Why production-rag?</h2>
            <p>Upload a PDF. Ask anything. Get receipts.</p>
          </div>
        </Reveal>

        <div className="why-grid">
          <Reveal>
            <div className="why-card">
              <h3>Not links. Citations.</h3>
              <p>
                Chatbots give you confident paragraphs. Every claim here maps
                to a numbered passage with filename, page, and similarity
                score.
              </p>
              <div className="why-visual">
                <MatchFlowMockup />
              </div>
            </div>
          </Reveal>

          <Reveal delay={120}>
            <div className="why-card">
              <h3>From PDF to answer in seconds.</h3>
              <p>
                Upload, and the pipeline takes over: parse → chunk → embed →
                index. No manual prep, no cleanup scripts.
              </p>
              <div className="why-visual">
                <div className="icon-trio">
                  <span className="sq">
                    <IconSpark />
                  </span>
                  <span className="sq">
                    <IconPuzzle />
                  </span>
                  <span className="sq">
                    <IconCompass />
                  </span>
                </div>
              </div>
            </div>
          </Reveal>

          <Reveal delay={80}>
            <div className="why-card">
              <h3>Everything in one place.</h3>
              <p>
                Manage documents, track what&apos;s indexed, delete cleanly —
                the whole knowledge-base lifecycle without juggling tools.
              </p>
              <div className="why-visual">
                <DedupMockup />
              </div>
            </div>
          </Reveal>

          <Reveal delay={160}>
            <div className="why-card">
              <h3>Honest by default.</h3>
              <p>
                Below a confidence threshold the LLM is never called. A refusal
                is a feature: &ldquo;I don&apos;t know&rdquo; beats a
                hallucination every time.
              </p>
              <div className="why-visual">
                <RefusalMockup />
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ================= HOW IT WORKS ================= */}
      <section className="block container" id="how-it-works">
        <Reveal>
          <div className="section-head">
            <h2>How it works?</h2>
            <p>From raw PDF to cited answer in three steps.</p>
          </div>
        </Reveal>
        <div className="hiw-grid">
          <Reveal>
            <div className="hiw-card c-gray">
              <div className="hiw-num">01</div>
              <h3>Upload your PDFs</h3>
              <p>
                Drag and drop. Files are hashed, parsed page by page, and
                duplicates are skipped automatically.
              </p>
            </div>
          </Reveal>
          <Reveal delay={120}>
            <div className="hiw-card c-blue">
              <div className="hiw-num">02</div>
              <h3>We chunk &amp; embed</h3>
              <p>
                Recursive splitting keeps paragraphs whole. Embeddings land in
                Qdrant with full lineage — file, page, offsets.
              </p>
            </div>
          </Reveal>
          <Reveal delay={240}>
            <div className="hiw-card c-purple">
              <div className="hiw-num">03</div>
              <h3>Ask &amp; get citations</h3>
              <p>
                Your question retrieves the top passages; the answer cites them
                inline as [n] — or refuses if the evidence is too weak.
              </p>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ================= FEATURES ================= */}
      <section className="block container" id="features">
        <Reveal>
          <div className="section-head">
            <h2>Features</h2>
            <p>What makes the answers trustworthy.</p>
          </div>
        </Reveal>

        <div className="feature-grid">
          <Reveal>
            <div className="feature-card">
              <h3>Sources you can verify</h3>
              <p>
                Every answer ships with its evidence: ranked sources, page
                numbers, and cosine similarity scores you can eyeball at a
                glance.
              </p>
              <SourcesMockup />
            </div>
          </Reveal>
          <Reveal delay={120}>
            <div className="feature-card">
              <h3>Providers, swappable by config</h3>
              <p>
                Jina for embeddings, any OpenAI-compatible endpoint for the
                LLM — free tiers supported. Changing providers is an env var,
                not a rewrite.
              </p>
              <div className="why-visual">
                <div className="providers-row">
                  <span>jina-embeddings</span>
                  <span>groq/llama</span>
                  <span>openrouter</span>
                  <span>qdrant</span>
                  <span>fastapi</span>
                  <span>next.js</span>
                </div>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ================= USE CASES ================= */}
      <section className="block container" id="use-cases">
        <Reveal>
          <div className="section-head">
            <h2>Use Cases</h2>
            <p>Where grounded answers actually matter.</p>
          </div>
        </Reveal>
        <div className="usecase-grid">
          <Reveal>
            <div className="usecase-card">
              <span className="blob blob-green" />
              <span className="emoji">📚</span>
              <div>
                <h3>Researchers</h3>
                <p>Interrogate papers and reports — with page-level proof.</p>
              </div>
            </div>
          </Reveal>
          <Reveal delay={100}>
            <div className="usecase-card">
              <span className="blob blob-yellow" />
              <span className="emoji">👩‍💻</span>
              <div>
                <h3>Developers</h3>
                <p>Query API docs and internal wikis without the tab hunt.</p>
              </div>
            </div>
          </Reveal>
          <Reveal delay={160}>
            <div className="usecase-card">
              <span className="blob blob-purple" />
              <span className="emoji">🏢</span>
              <div>
                <h3>Teams</h3>
                <p>One knowledge base every teammate can trust and verify.</p>
              </div>
            </div>
          </Reveal>
          <Reveal delay={220}>
            <div className="usecase-card">
              <span className="blob blob-blue" />
              <span className="emoji">🎓</span>
              <div>
                <h3>Students</h3>
                <p>Turn lecture slides and textbooks into a cited study buddy.</p>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ================= DIFFERENT ================= */}
      <section className="block container" id="different">
        <Reveal>
          <div className="section-head">
            <h2>
              What Makes
              <br />
              production-rag Different
            </h2>
            <p>RAG shouldn&apos;t feel like a slot machine.</p>
          </div>
        </Reveal>
        <Reveal delay={100}>
          <div className="diff-cta">
            <Link href="/ask" className="btn-primary">
              Try for Free
            </Link>
          </div>
        </Reveal>
        <div className="diff-grid">
          <Reveal>
            <div className="diff-card">
              <div className="diff-icon"><IconCompass /></div>
              <h3>Built to understand</h3>
              <p>
                The splitter, retries, dedup, and grounding are written from
                scratch — no black boxes.
              </p>
            </div>
          </Reveal>
          <Reveal delay={100}>
            <div className="diff-card">
              <div className="diff-icon"><IconRocket /></div>
              <h3>Focused on real grounding</h3>
              <p>
                No vibes-based answers — just retrieval, citations, and honest
                refusals.
              </p>
            </div>
          </Reveal>
          <Reveal delay={160}>
            <div className="diff-card">
              <div className="diff-icon"><IconLock /></div>
              <h3>Your data, your control</h3>
              <p>
                Local Qdrant, your own API keys, delete anytime. Nothing leaves
                your stack but embeddings.
              </p>
            </div>
          </Reveal>
          <Reveal delay={220}>
            <div className="diff-card">
              <div className="diff-icon"><IconSpark /></div>
              <h3>Tested like production</h3>
              <p>
                142 offline tests across every stage — deterministic, no paid
                APIs required.
              </p>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ================= ROADMAP ================= */}
      <section className="block container" id="roadmap">
        <Reveal>
          <div className="section-head">
            <h2>What&apos;s coming next</h2>
          </div>
        </Reveal>
        <div className="roadmap-grid">
          <Reveal>
            <div className="roadmap-card">
              <div className="diff-icon"><IconPuzzle /></div>
              <h3>Hybrid search (BM25 + vectors)</h3>
            </div>
          </Reveal>
          <Reveal delay={120}>
            <div className="roadmap-card">
              <div className="diff-icon"><IconSpark /></div>
              <h3>Neural reranking</h3>
            </div>
          </Reveal>
          <Reveal delay={240}>
            <div className="roadmap-card">
              <div className="diff-icon"><IconCompass /></div>
              <h3>Retrieval evaluation harness</h3>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ================= FINAL CTA ================= */}
      <section className="container final-cta" id="start">
        <Reveal>
          <h2>Your knowledge base is already waiting. Start asking.</h2>
          <p className="sub">
            Free tiers, no credit card, grounded answers in under a minute.
          </p>
          <Link href="/ask" className="btn-primary">
            Ask your first question
          </Link>
        </Reveal>
        <Reveal delay={200}>
          <div className="final-mockup">
            <AppMockup />
          </div>
        </Reveal>
      </section>
    </>
  );
}
