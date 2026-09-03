"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AskResponse, askQuestion, getStats, StatsResponse } from "@/lib/api";

function AnswerWithCitations({ text }: { text: string }) {
  const parts = text.split(/(\[\d+\])/g);
  return (
    <p className="answer-text">
      {parts.map((part, i) => {
        const match = part.match(/^\[(\d+)\]$/);
        if (match) {
          return (
            <a key={i} href={`#source-${match[1]}`} className="citation">
              {match[1]}
            </a>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </p>
  );
}

export default function AskPage() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AskResponse | null>(null);
  const [stats, setStats] = useState<StatsResponse | null>(null);

  useEffect(() => {
    getStats().then(setStats).catch(() => setStats(null));
  }, [result]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!question.trim() || loading) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await askQuestion({ question: question.trim() }));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container" style={{ paddingBottom: 60 }}>
      <div className="page-head" style={{ textAlign: "center", paddingBottom: 28 }}>
        <h1>Ask your documents</h1>
        <p>
          {stats
            ? `${stats.total_chunks} chunks indexed across your knowledge base.`
            : "Answers grounded in retrieved context — cited or refused."}
        </p>
      </div>

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
            <kbd>Enter</kbd> to ask · <kbd>Shift</kbd>+<kbd>Enter</kbd> new
            line
          </span>
          <button
            type="submit"
            className="btn-primary"
            disabled={loading || !question.trim()}
          >
            {loading && <span className="spinner" />}
            {loading ? "Thinking..." : "Ask"}
          </button>
        </div>
      </form>

      {error && <div className="error-box">{error}</div>}

      {result && !result.refused && (
        <div className="result-card glow" style={{ marginTop: 22 }}>
          <div className="result-title">
            Grounded answer <span className="badge">cited</span>
          </div>
          <AnswerWithCitations text={result.answer} />
        </div>
      )}

      {result && result.refused && (
        <div className="refusal-box" style={{ marginTop: 22 }}>
          {result.answer}
          <div className="refusal-sub">
            Retrieval confidence was below threshold, so the LLM was never
            called.{" "}
            <Link href="/documents" style={{ color: "#93c5fd" }}>
              Upload more relevant documents →
            </Link>
          </div>
        </div>
      )}

      {result && result.sources.length > 0 && (
        <div className="result-card">
          <div className="result-title">
            Sources{" "}
            <span className="badge info">{result.sources.length} retrieved</span>
          </div>
          <ul className="source-list">
            {result.sources.map((src, i) => (
              <li key={i} className="source-item" id={`source-${i + 1}`}>
                <span className="source-num">[{i + 1}]</span>
                <span className="source-name">{src.filename}</span>
                <span className="source-meta">
                  page {src.page_number} · chunk {src.chunk_index}
                </span>
                <span className="source-score">
                  <span className="score-bar-track">
                    <span
                      className="score-bar"
                      style={{
                        width: `${Math.max(6, src.score * 100)}%`,
                        display: "block",
                      }}
                    />
                  </span>
                  <span className="score-num">{src.score.toFixed(3)}</span>
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
