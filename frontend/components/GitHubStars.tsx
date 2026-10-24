"use client";

import { useEffect, useState } from "react";
import { GITHUB_URL } from "@/lib/site";

const CACHE_KEY = "prag-gh-stars";
const TTL_MS = 60 * 60 * 1000; // 1 hour — well inside GitHub's rate limits

/**
 * Live star count chip for the nav. Fetches once per hour (localStorage
 * cache), renders nothing when GitHub is unreachable — the link still works.
 */
export default function GitHubStars() {
  const [count, setCount] = useState<number | null>(null);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(CACHE_KEY);
      if (raw) {
        const { n, t } = JSON.parse(raw);
        if (typeof n === "number" && Date.now() - t < TTL_MS) {
          setCount(n);
          return;
        }
      }
    } catch {
      /* corrupt cache — refetch */
    }

    const repo = GITHUB_URL.replace("https://github.com/", "");
    fetch(`https://api.github.com/repos/${repo}`)
      .then((r) => (r.ok ? r.json() : Promise.reject(new Error(String(r.status)))))
      .then((d) => {
        const n: number = d.stargazers_count;
        setCount(n);
        try {
          localStorage.setItem(CACHE_KEY, JSON.stringify({ n, t: Date.now() }));
        } catch {
          /* storage unavailable — fine */
        }
      })
      .catch(() => {
        /* rate-limited or offline — badge simply stays hidden */
      });
  }, []);

  if (count === null) return null;

  return (
    <span className="star-count" aria-label={`${count} GitHub stars`}>
      <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
        <path d="M12 2l2.9 6.26 6.6.57-5 4.36 1.5 6.45L12 16.9 5.99 19.64l1.5-6.45-5-4.36 6.6-.57L12 2z" />
      </svg>
      {count}
    </span>
  );
}
