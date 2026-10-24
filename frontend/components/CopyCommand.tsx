"use client";

import { useState } from "react";

/**
 * Dark terminal panel with a copy button — the "code-as-hero" chip.
 */
export default function CopyCommand({
  title,
  lines,
}: {
  title: string;
  lines: { cmd: string; comment?: string }[];
}) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(lines.map((l) => l.cmd).join("\n"));
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard unavailable — ignore */
    }
  }

  return (
    <div className="terminal">
      <div className="terminal-bar">
        <span className="dots">
          <span />
          <span />
          <span />
        </span>
        <span className="terminal-title">{title}</span>
        <button
          className={`copy-btn${copied ? " copied" : ""}`}
          onClick={handleCopy}
          type="button"
        >
          {copied ? "copied ✓" : "copy"}
        </button>
      </div>
      <div className="terminal-body">
        {lines.map((line, i) => (
          <div key={i} className="terminal-line">
            <span className="prompt">$</span>
            <span className="cmd">{line.cmd}</span>
            {line.comment && <span className="comment"># {line.comment}</span>}
          </div>
        ))}
      </div>
    </div>
  );
}
