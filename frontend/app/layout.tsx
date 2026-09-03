import type { Metadata } from "next";
import Link from "next/link";
import { GITHUB_URL } from "@/lib/site";
import "./globals.css";

export const metadata: Metadata = {
  title: "production-rag — grounded document QA",
  description:
    "Full-stack RAG platform: upload documents, get answers grounded in retrieved context with page-level citations and honest refusals.",
};

function LogoMark({ size = 30 }: { size?: number }) {
  return (
    <span className="brand-mark" style={{ width: size, height: size }}>
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="#fff"
        strokeWidth="2.4"
        strokeLinecap="round"
        strokeLinejoin="round"
        style={{ width: size * 0.55, height: size * 0.55 }}
      >
        <path d="M12 2 2 7l10 5 10-5-10-5z" />
        <path d="m2 17 10 5 10-5" opacity="0.55" />
        <path d="m2 12 10 5 10-5" opacity="0.8" />
      </svg>
    </span>
  );
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <header className="site-header">
          <div className="header-inner">
            <Link href="/" className="brand">
              <LogoMark />
              production<span className="brand-blue">-rag</span>
            </Link>
            <nav>
              <Link href="/#how-it-works">How it works</Link>
              <Link href="/#features">Features</Link>
              <Link href="/#use-cases">Use cases</Link>
              <a
                href={GITHUB_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="nav-github"
                aria-label="GitHub repository"
              >
                <svg width="17" height="17" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.55v-2.17c-3.2.7-3.87-1.36-3.87-1.36-.52-1.33-1.28-1.68-1.28-1.68-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.19 1.76 1.19 1.03 1.75 2.69 1.25 3.35.95.1-.74.4-1.25.72-1.53-2.55-.29-5.24-1.28-5.24-5.68 0-1.26.45-2.28 1.19-3.09-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.17 1.18a11 11 0 0 1 5.77 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.83 1.19 3.09 0 4.41-2.7 5.38-5.26 5.67.41.35.77 1.05.77 2.12v3.14c0 .3.21.67.8.55A11.51 11.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5z" />
                </svg>
              </a>
              <Link href="/ask" className="nav-cta">
                Ask Now
              </Link>
            </nav>
          </div>
        </header>

        <main>{children}</main>

        <footer className="site-footer">
          <div className="footer-inner">
            <div className="footer-brand">
              <Link href="/" className="brand">
                <LogoMark />
                production<span className="brand-blue">-rag</span>
              </Link>
              <p>
                A production-oriented RAG platform. Every answer is grounded in
                retrieved context, cited to real pages, and refused when the
                evidence isn&apos;t there.
              </p>
            </div>
            <div className="footer-col">
              <h4>Product</h4>
              <Link href="/ask">Ask questions</Link>
              <Link href="/documents">Upload &amp; manage documents</Link>
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
              >
                API reference
              </a>
            </div>
            <div className="footer-col">
              <h4>Stack</h4>
              <span>Next.js 15 · React 19</span>
              <span>FastAPI · Pydantic v2</span>
              <span>Qdrant · Jina AI</span>
              <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer">
                View source on GitHub
              </a>
            </div>
          </div>
          <div className="footer-bottom">
            <span>
              © {new Date().getFullYear()} production-rag — built to understand
              every layer.
            </span>
            <span>Grounded answers · citations · refusals over hallucinations</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
