import type { Metadata, Viewport } from "next";
import Link from "next/link";
import { Inter, JetBrains_Mono } from "next/font/google";
import { API_DOCS_URL, GITHUB_URL } from "@/lib/site";
import GitHubStars from "@/components/GitHubStars";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  display: "swap",
});

export const metadata: Metadata = {
  title: "production-rag — RAG that shows its work",
  description:
    "Open-source retrieval-augmented generation with page-level citations, a transparent pipeline, and honest refusals.",
};

export const viewport: Viewport = {
  themeColor: "#FAFAF7",
};

function LogoMark({ size = 26 }: { size?: number }) {
  return (
    <span className="brand-mark" style={{ width: size, height: size }}>
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="#fafaf7"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
        style={{ width: size * 0.58, height: size * 0.58 }}
      >
        <path d="M12 2 2 7l10 5 10-5-10-5z" />
        <path d="m2 17 10 5 10-5" opacity="0.55" />
        <path d="m2 12 10 5 10-5" opacity="0.8" />
      </svg>
    </span>
  );
}

function GitHubIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <path d="M12 .5C5.65.5.5 5.65.5 12c0 5.08 3.29 9.39 7.86 10.91.58.11.79-.25.79-.55v-2.17c-3.2.7-3.87-1.36-3.87-1.36-.52-1.33-1.28-1.68-1.28-1.68-1.04-.71.08-.7.08-.7 1.15.08 1.76 1.19 1.76 1.19 1.03 1.75 2.69 1.25 3.35.95.1-.74.4-1.25.72-1.53-2.55-.29-5.24-1.28-5.24-5.68 0-1.26.45-2.28 1.19-3.09-.12-.29-.52-1.46.11-3.05 0 0 .97-.31 3.17 1.18a11 11 0 0 1 5.77 0c2.2-1.49 3.17-1.18 3.17-1.18.63 1.59.23 2.76.11 3.05.74.81 1.19 1.83 1.19 3.09 0 4.41-2.7 5.38-5.26 5.67.41.35.77 1.05.77 2.12v3.14c0 .3.21.67.8.55A11.51 11.51 0 0 0 23.5 12C23.5 5.65 18.35.5 12 .5z" />
    </svg>
  );
}

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrains.variable}`}>
      <body>
        <div className="banner">
          <div className="banner-inner">
            <span className="banner-tag">on the roadmap</span>
            a retrieval eval harness that grades itself —{" "}
            <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer">
              follow the build on GitHub →
            </a>
          </div>
        </div>
        <header className="site-header">
          <div className="header-inner">
            <Link href="/" className="brand" aria-label="production-rag home">
              <LogoMark />
              <span className="brand-name">production-rag</span>
            </Link>
            <nav>
              <Link href="/#pipeline">Pipeline</Link>
              <Link href="/playground">Playground</Link>
              <Link href="/console">Console</Link>
              <a
                href={GITHUB_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="nav-github"
              >
                <GitHubIcon />
                GitHub
                <GitHubStars />
              </a>
              <Link href="/playground" className="nav-cta">
                Open playground
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
                <span className="brand-name">production-rag</span>
              </Link>
              <p>
                An open-source RAG pipeline with nothing to hide — every answer
                grounded in retrieved context, cited to real pages, or refused.
              </p>
            </div>
            <div className="footer-col">
              <h4>Product</h4>
              <Link href="/playground">Playground</Link>
              <Link href="/console">Console</Link>
              <a href={API_DOCS_URL} target="_blank" rel="noopener noreferrer">
                API reference
              </a>
            </div>
            <div className="footer-col">
              <h4>Project</h4>
              <a href={GITHUB_URL} target="_blank" rel="noopener noreferrer">
                GitHub
              </a>
              <a
                href={`${GITHUB_URL}/blob/main/scripts/demo_rag.py`}
                target="_blank"
                rel="noopener noreferrer"
              >
                Offline demo
              </a>
              <a
                href={`${GITHUB_URL}/tree/main/tests`}
                target="_blank"
                rel="noopener noreferrer"
              >
                Test suites
              </a>
            </div>
            <div className="footer-col">
              <h4>Stack</h4>
              <span>FastAPI · Pydantic v2</span>
              <span>Qdrant · Jina AI</span>
              <span>Next.js 15 · React 19</span>
            </div>
          </div>
          <div className="footer-bottom">
            <span>
              © {new Date().getFullYear()} production-rag — grounded in
              retrieved context.
            </span>
            <span>cited to real pages · or refused</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
