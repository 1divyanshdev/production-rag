"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  AskResponse,
  askQuestion,
  getStats,
  StatsResponse,
} from "@/lib/api";

interface HistoryEntry {
  question: string;
  result: AskResponse;
}

const EXAMPLES = [
  "What algorithm does the vector database use for search?",
  "How does chunking decide where to split text?",
  "What happens to an encrypted PDF on upload?",
];

function AnswerWithCitations({ text }: { text: string }) {
  const parts = text.split(/(\[\d+\])/g);
  return (
    <p className="answer-text">
      {parts.map((part, i) => {
        const match = part.match(/^\[(\d+)\]$/);
        if (match) {
          return (
            <a key={i} href={`#source-${match[1]}`} className="cite">
              {match[1]}
            </a>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </p>
  );
}

export default function PlaygroundPage() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AskResponse | null>(null);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);

  useEffect(() => {
    getStats().then(setStats).catch(() => setStats(null));
  }, [result]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const q = question.trim();
    if (!q || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await askQuestion({ question: q });
      setResult(res);
      setHistory((h) => [{ question: q, result: res }, ...h].slice(0, 8));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  function restore(entry: HistoryEntry) {
    setQuestion(entry.question);
    setResult(entry.result);
    setError(null);
  }

  const topScore = result?.sources?.[0]?.score;

  return (
    <div className="container">
      <div className="page-head">
        <span className="kicker">playground</span>
        <h1>Ask your knowledge base</h1>
        <p className="page-sub">
          {stats
            ? `${stats.total_chunks} chunks indexed in “${stats.collection}” — answers cited, or refused.`
            : "Answers grounded in retrieved context — cited to real pages, or refused."}
        </p>
      </div>

      <div className="pg-grid">
        {/* ---------- main column ---------- */}
        <div>
          <form className="ask-panel" onSubmit={handleSubmit}>
            <textarea
              rows={2}
              placeholder="e.g. What algorithm does the vector database use for search?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) handleSubmit(e);
              }}
              aria-label="Your question"
              autoFocus
            />
            <div className="ask-actions">
              <span className="ask-hint">
                <kbd>Enter</kbd> ask · <kbd>Shift</kbd>+<kbd>Enter</kbd> new
                line
              </span>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={loading || !question.trim()}
              >
                {loading && <span className="spinner on-accent" />}
                {loading ? "Asking…" : "Ask"}
              </button>
            </div>
          </form>

          {error && <div className="error-box">{error}</div>}

          {!result && !error && !loading && (
            <div className="empty-card">
              <span className="block-title">no query yet</span>
              <p>
                Ask something answerable from your indexed documents — or start
                with one of these:
              </p>
              <div className="example-chips">
                {EXAMPLES.map((ex) => (
                  <button
                    key={ex}
                    type="button"
                    className="example-chip"
                    onClick={() => setQuestion(ex)}
                  >
                    {ex}
                  </button>
                ))}
              </div>
            </div>
          )}

          {result && !result.refused && (
            <div className="pg-block">
              <div className="trace">
                <div className="trace-line">
                  <span className="prompt">&gt;</span>
                  retrieve("{result.question.slice(0, 72)}
                  {result.question.length > 72 ? "…" : ""}")
                </div>
                <div className="trace-line trace-dim">
                  {result.sources.length} passages · top score{" "}
                  {topScore?.toFixed(2)} · {result.cited_indices.length} cited
                </div>
                <div className="trace-line trace-ok">
                  grounded — every claim traces to a numbered source
                </div>
              </div>
              <div className="result-card">
                <div className="answer-head">
                  <span className="block-title">Answer</span>
                  <span className="badge ok">cited</span>
                </div>
                <AnswerWithCitations text={result.answer} />
              </div>
            </div>
          )}

          {result && result.refused && (
            <div className="pg-block">
              <div className="trace">
                <div className="trace-line">
                  <span className="prompt">&gt;</span>
                  retrieve("{result.question.slice(0, 72)}
                  {result.question.length > 72 ? "…" : ""}")
                </div>
                <div className="trace-line trace-dim">
                  no passage cleared the confidence threshold
                </div>
                <div className="trace-line trace-warn">
                  refused — the llm was never called
                </div>
              </div>
              <div className="refusal-card">
                <div className="refusal-title">
                  <span className="refusal-glyph">∅</span>
                  Refused — not enough evidence
                </div>
                <p className="refusal-body">
                  {result.answer}{" "}
                  <Link href="/console">Add documents in the console →</Link>
                </p>
              </div>
            </div>
          )}
        </div>

        {/* ---------- sources rail ---------- */}
        <aside className="pg-rail">
          {result && result.sources.length > 0 && (
            <div>
              <div className="rail-head">
                <span className="rail-title">Sources</span>
                <span className="badge info">
                  {result.sources.length} retrieved
                </span>
              </div>
              {result.sources.map((src, i) => (
                <div key={i} className="source-card" id={`source-${i + 1}`}>
                  <span className="source-num">[{i + 1}]</span>
                  <span className="source-info">
                    <span className="source-file">{src.filename}</span>
                    <span className="source-meta">
                      page {src.page_number} · chunk {src.chunk_index}
                    </span>
                  </span>
                  <span className="source-score">
                    <span className="score-track">
                      <span
                        className="score-bar"
                        style={{ width: `${Math.max(6, src.score * 100)}%` }}
                      />
                    </span>
                    <span className="score-num">{src.score.toFixed(2)}</span>
                  </span>
                </div>
              ))}
            </div>
          )}

          {history.length > 0 && (
            <div className="history-card">
              <span className="block-title">this session</span>
              {history.map((h, i) => (
                <button
                  key={i}
                  type="button"
                  className="history-item"
                  onClick={() => restore(h)}
                  title={h.question}
                >
                  <span
                    className={`history-dot${h.result.refused ? " refused" : ""}`}
                  />
                  <span className="history-q">{h.question}</span>
                </button>
              ))}
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
