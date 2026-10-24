"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";

/**
 * The "what ChatGPT can't do" component: one window frame, two tabs —
 * a grounded answer with citations, and an honest refusal. The session
 * replays like a recording: question types in, the retrieval trace lands
 * line by line, then the answer and its sources. Values are recorded
 * from a real session shape; visitors can run it live in the playground.
 */

type Tab = "grounded" | "refusal";

interface Source {
  n: number;
  file: string;
  page: number;
  score: number;
}

type Segment = { t: string } | { cite: number };

interface Session {
  q: string;
  query: string;
  statsLine: string;
  decisionLine: string;
  ok: boolean;
  answer: Segment[];
  sources: Source[];
}

const SESSIONS: Record<Tab, Session> = {
  grounded: {
    q: "What algorithm does the vector database use for search?",
    query: "vector database search algorithm",
    statsLine: "6 passages · 3 sources · top score 0.82",
    decisionLine: "0.82 ≥ threshold 0.35 — grounded",
    ok: true,
    answer: [
      { t: "Qdrant performs nearest-neighbour search with the HNSW graph algorithm, trading a small index-time cost for fast approximate queries at scale." },
      { cite: 1 },
      { t: " Recall stays high because layered graphs preserve long-range links." },
      { cite: 2 },
    ],
    sources: [
      { n: 1, file: "qdrant-architecture.pdf", page: 3, score: 0.82 },
      { n: 2, file: "qdrant-architecture.pdf", page: 4, score: 0.74 },
      { n: 3, file: "retrieval-notes.pdf", page: 12, score: 0.68 },
    ],
  },
  refusal: {
    q: "What is the payroll schedule for the engineering team?",
    query: "engineering payroll schedule",
    statsLine: "4 passages · best score 0.21",
    decisionLine: "0.21 < threshold 0.35 — refused",
    ok: false,
    answer: [],
    sources: [],
  },
};

const TYPE_MS = 26;
const TRACE_DELAYS = [420, 980, 1560]; // after typing: retrieve line, stats, decision
const ANSWER_AT = 2120;
const SOURCES_AT = 2520;

// phases: 0 typing · 1 retrieve-line · 2 stats · 3 decision · 4 answer · 5 sources
export default function EvidenceDemo() {
  const [tab, setTab] = useState<Tab>("grounded");
  const [phase, setPhase] = useState(0);
  const [typed, setTyped] = useState("");
  const timers = useRef<number[]>([]);
  const typer = useRef<number | null>(null);

  const clearTimers = useCallback(() => {
    if (typer.current !== null) window.clearInterval(typer.current);
    typer.current = null;
    timers.current.forEach((t) => window.clearTimeout(t));
    timers.current = [];
  }, []);

  const play = useCallback(
    (which: Tab) => {
      clearTimers();
      const s = SESSIONS[which];
      setTyped("");
      setPhase(0);

      if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        setTyped(s.q);
        setPhase(5);
        return;
      }

      let i = 0;
      typer.current = window.setInterval(() => {
        i += 1;
        setTyped(s.q.slice(0, i));
        if (i >= s.q.length) {
          if (typer.current !== null) window.clearInterval(typer.current);
          typer.current = null;
          TRACE_DELAYS.forEach((d, idx) => {
            timers.current.push(
              window.setTimeout(() => setPhase(idx + 1), d)
            );
          });
          timers.current.push(
            window.setTimeout(() => setPhase(4), ANSWER_AT)
          );
          timers.current.push(
            window.setTimeout(() => setPhase(5), SOURCES_AT)
          );
        }
      }, TYPE_MS);
    },
    [clearTimers]
  );

  useEffect(() => {
    play(tab);
    return clearTimers;
  }, [tab, play, clearTimers]);

  const s = SESSIONS[tab];
  const typing = typed.length < s.q.length;

  return (
    <div className="window">
      <div className="window-bar">
        <span className="dots">
          <span />
          <span />
          <span />
        </span>
        <span className="window-title">production-rag — playground</span>
        <button
          type="button"
          className="replay-btn"
          onClick={() => play(tab)}
          aria-label="Replay the recorded session"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden
          >
            <path d="M21 12a9 9 0 1 1-2.64-6.36" />
            <path d="M21 3v6h-6" />
          </svg>
          replay
        </button>
        <div className="demo-tabs">
          <button
            type="button"
            className={`demo-tab${tab === "grounded" ? " active" : ""}`}
            onClick={() => setTab("grounded")}
          >
            Grounded answer
          </button>
          <button
            type="button"
            className={`demo-tab${tab === "refusal" ? " active" : ""}`}
            onClick={() => setTab("refusal")}
          >
            Honest refusal
          </button>
        </div>
      </div>

      <div className="demo-body">
        <div className="demo-main">
          <div className="demo-q">
            {typed}
            {typing && <span className="caret" />}
          </div>

          <div className="trace">
            {phase >= 1 && (
              <div className="trace-line fade-in">
                <span className="prompt">&gt;</span>retrieve("{s.query}")
              </div>
            )}
            {phase >= 2 && (
              <div className="trace-line trace-dim fade-in">{s.statsLine}</div>
            )}
            {phase >= 3 && (
              <div
                className={`trace-line fade-in ${s.ok ? "trace-ok" : "trace-warn"}`}
              >
                {s.decisionLine}
              </div>
            )}
          </div>

          {phase >= 4 &&
            (s.ok ? (
              <div className="result-card fade-in">
                <div className="answer-head">
                  <span className="block-title">Answer</span>
                  <span className="badge ok">cited</span>
                </div>
                <p className="answer-text">
                  {s.answer.map((seg, i) =>
                    "cite" in seg ? (
                      <span key={i} className="cite">
                        {seg.cite}
                      </span>
                    ) : (
                      <span key={i}>{seg.t}</span>
                    )
                  )}
                </p>
              </div>
            ) : (
              <div className="refusal-card fade-in">
                <div className="refusal-title">
                  <span className="refusal-glyph">∅</span>
                  Refused — not enough evidence
                </div>
                <p className="refusal-body">
                  Nothing in the indexed documents clears the confidence
                  threshold for this question. The LLM is never called: zero
                  tokens spent, zero hallucination risk.{" "}
                  <Link href="/console">Add documents in the console →</Link>
                </p>
              </div>
            ))}
        </div>

        <div className="demo-rail">
          <div className="rail-head">
            <span className="rail-title">Sources</span>
            {tab === "grounded" && phase >= 5 && (
              <span className="badge info fade-in">{s.sources.length} retrieved</span>
            )}
          </div>
          {tab === "grounded"
            ? s.sources.map((src, i) =>
                phase >= 5 ? (
                  <div
                    key={src.n}
                    className="source-card fade-in"
                    style={{ animationDelay: `${i * 150}ms` }}
                  >
                    <span className="source-num">[{src.n}]</span>
                    <span className="source-info">
                      <span className="source-file">{src.file}</span>
                      <span className="source-meta">page {src.page}</span>
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
                ) : (
                  <div key={src.n} className="source-card source-ghost" />
                )
              )
            : phase >= 5 && (
                <p className="rail-empty fade-in">
                  no sources — nothing cleared the 0.35 threshold, so no passage
                  was sent to the model.
                </p>
              )}
        </div>
      </div>
    </div>
  );
}
