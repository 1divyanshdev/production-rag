/**
 * Static app-window mockups rendered in pure CSS/JSX — the product
 * "screenshots" of the landing page (hero, cards, final CTA).
 */

function BrandMark({ size = 20 }: { size?: number }) {
  return (
    <span className="brand-mark" style={{ width: size, height: size, borderRadius: 6 }}>
      <svg viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" style={{ width: size * 0.55, height: size * 0.55 }}>
        <path d="M12 2 2 7l10 5 10-5-10-5z" />
        <path d="m2 17 10 5 10-5" opacity="0.55" />
        <path d="m2 12 10 5 10-5" opacity="0.8" />
      </svg>
    </span>
  );
}

export function AppMockup() {
  return (
    <div className="app-mockup">
      <div className="mock-sidebar">
        <div className="mock-side-brand">
          <BrandMark />
          production-rag
        </div>
        <div className="mock-side-label">Menu</div>
        {["Dashboard", "Documents", "Ask", "Settings"].map((item, i) => (
          <div key={item} className={`mock-nav-item${i === 2 ? " active" : ""}`}>
            {item}
          </div>
        ))}
      </div>
      <div className="mock-main">
        <div className="mock-title">Ask</div>
        <div className="mock-question">
          What algorithm does the vector database use for search?
        </div>
        <div className="mock-answer">
          Qdrant performs nearest-neighbour search with the HNSW graph
          algorithm, trading a small index-time cost for fast approximate
          queries at scale.
          <span className="cite">[1]</span> Recall stays high because layered
          graphs preserve long-range links.
          <span className="cite">[2]</span>
        </div>
        <div className="mock-sources">
          <div className="mock-source">
            <span className="num">[1]</span> kb.pdf — page 3
            <span className="score" />
            <span className="mock-badge">0.82</span>
          </div>
          <div className="mock-source">
            <span className="num">[2]</span> kb.pdf — page 4
            <span className="score" />
            <span className="mock-badge">0.74</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export function SourcesMockup() {
  return (
    <div className="sources-mock">
      {[
        ["[1]", "report.pdf", "page 12", "0.86"],
        ["[2]", "report.pdf", "page 13", "0.79"],
        ["[3]", "handbook.pdf", "page 2", "0.71"],
      ].map(([num, file, page, score]) => (
        <div key={num} className="mock-source">
          <span className="num">{num}</span> {file} · {page}
          <span className="score" />
          <span className="mock-badge">{score}</span>
        </div>
      ))}
    </div>
  );
}

export function RefusalMockup() {
  return (
    <div>
      <div className="confidence-track">
        <div className="confidence-fill" />
      </div>
      <div className="confidence-labels">
        <span>retrieval confidence</span>
        <span>threshold 0.35</span>
      </div>
      <div className="mini-answer">✓ Confident → answer with citations [1][2]</div>
      <div style={{ height: 10 }} />
      <div className="mini-refusal">
        ⚠ Below threshold → &ldquo;I could not find relevant information…&rdquo; — LLM never called
      </div>
    </div>
  );
}

export function MatchFlowMockup() {
  return (
    <div className="match-flow">
      <div className="match-tags">
        <span className="match-tag">Your PDFs 📄</span>
        <span className="match-tag">Chunks 🧩</span>
        <span className="match-tag">Embeddings 🧠</span>
        <span className="match-tag">Qdrant ⚡</span>
      </div>
      <div className="match-arrow">→</div>
      <div className="match-result">
        <div className="dim">Grounded</div>
        <div className="big">Answer</div>
        <div className="dim">with [n] citations</div>
      </div>
    </div>
  );
}

export function DedupMockup() {
  return (
    <div>
      <div className="hash-row">
        sha256(a3f9c2…) <span className="same">✓ already indexed — skipped</span>
      </div>
      <div className="hash-row">
        sha256(7b1e88…) <span className="skip">new — chunk → embed → upsert</span>
      </div>
      <div className="hash-row">
        id = uuid5(hash:chunk) <span className="same">overwrite, never duplicate</span>
      </div>
    </div>
  );
}
