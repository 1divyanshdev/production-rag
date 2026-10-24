"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import {
  DocumentSummary,
  IndexResponse,
  StatsResponse,
  deleteDocument,
  getStats,
  listDocuments,
  uploadDocument,
} from "@/lib/api";

export default function ConsolePage() {
  const [docs, setDocs] = useState<DocumentSummary[]>([]);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragover, setDragover] = useState(false);
  const [confirmId, setConfirmId] = useState<string | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  const refresh = useCallback(async () => {
    setError(null);
    try {
      const [docsResp, statsResp] = await Promise.all([
        listDocuments(),
        getStats(),
      ]);
      setDocs(docsResp);
      setStats(statsResp);
    } catch (err) {
      setError(
        `Cannot reach the backend. Is the API running? (${err instanceof Error ? err.message : err})`
      );
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  // safety net: confirm state expires if untouched
  useEffect(() => {
    if (!confirmId) return;
    const t = setTimeout(() => setConfirmId(null), 3000);
    return () => clearTimeout(t);
  }, [confirmId]);

  async function handleUpload(file: File) {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Only PDF files are supported.");
      return;
    }
    setUploading(true);
    setError(null);
    setMessage(null);
    try {
      const result: IndexResponse = await uploadDocument(file);
      if (result.skipped_duplicate) {
        setMessage(
          `${result.filename} was already indexed (identical content hash) — nothing to do.`
        );
      } else {
        setMessage(
          `Indexed ${result.filename}: ${result.indexed_chunks} chunk(s) are now searchable.`
        );
      }
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setUploading(false);
      if (fileInput.current) fileInput.current.value = "";
    }
  }

  async function handleDelete(doc: DocumentSummary) {
    if (confirmId !== doc.document_id) {
      setConfirmId(doc.document_id);
      return;
    }
    setConfirmId(null);
    setError(null);
    setMessage(null);
    try {
      const resp = await deleteDocument(doc.document_id);
      setMessage(
        `Deleted ${resp.deleted_chunks} chunk(s) from ${doc.filename}.`
      );
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <div className="container">
      <div className="page-head">
        <span className="kicker">console</span>
        <h1>Knowledge base</h1>
        <p className="page-sub">
          Upload PDFs to build the corpus the playground answers from.
        </p>
      </div>

      <div className="stats-strip">
        <div className="stat-card">
          <div className="stat-num">{docs.length}</div>
          <div className="stat-label">documents</div>
        </div>
        <div className="stat-card">
          <div className="stat-num">{stats ? stats.total_chunks : "—"}</div>
          <div className="stat-label">chunks indexed</div>
        </div>
        <div className="stat-card">
          <div className="stat-num mono">
            {stats ? stats.collection : "—"}
          </div>
          <div className="stat-label">qdrant collection</div>
        </div>
      </div>

      <div>
        <div
          className={`dropzone${dragover ? " dragover" : ""}`}
          onClick={() => !uploading && fileInput.current?.click()}
          onDragOver={(e) => {
            e.preventDefault();
            setDragover(true);
          }}
          onDragLeave={() => setDragover(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragover(false);
            const file = e.dataTransfer.files?.[0];
            if (file && !uploading) handleUpload(file);
          }}
        >
          {uploading ? (
            <div className="dz-stage">
              <span className="dz-dots">
                <span />
                <span />
                <span />
              </span>
              indexing — parse → chunk → embed → index
            </div>
          ) : (
            <>
              <div className="dz-title">Drop a PDF here, or click to browse</div>
              <div className="dz-sub">
                duplicates detected by sha-256 · 50 MB limit
              </div>
            </>
          )}
        </div>
        <input
          ref={fileInput}
          type="file"
          accept=".pdf,application/pdf"
          hidden
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) handleUpload(file);
          }}
        />
      </div>

      {message && <div className="ok-box">{message}</div>}
      {error && <div className="error-box">{error}</div>}

      <div className="doc-table-card">
        <div className="doc-table-head">
          <span className="block-title">indexed documents</span>
          {stats && (
            <span className="badge info">{stats.total_chunks} chunks</span>
          )}
        </div>
        {docs.length === 0 ? (
          <div className="empty-card" style={{ border: "none", margin: 0 }}>
            <span className="block-title">empty knowledge base</span>
            <p>
              Nothing indexed yet. Upload a PDF above, then ask questions in
              the <Link href="/playground">playground</Link>.
            </p>
          </div>
        ) : (
          <div className="table-scroll">
            <table className="doc-table">
              <thead>
                <tr>
                  <th>file</th>
                  <th>pages</th>
                  <th>chunks</th>
                  <th>content hash</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {docs.map((doc) => (
                  <tr key={doc.document_id}>
                    <td className="doc-file">{doc.filename}</td>
                    <td>{doc.total_pages}</td>
                    <td>
                      <span className="badge info">{doc.chunk_count}</span>
                    </td>
                    <td className="mono">{doc.file_hash.slice(0, 12)}…</td>
                    <td style={{ textAlign: "right" }}>
                      <button
                        type="button"
                        className={`btn-del${confirmId === doc.document_id ? " confirm" : ""}`}
                        onClick={() => handleDelete(doc)}
                      >
                        {confirmId === doc.document_id ? "Confirm" : "Delete"}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      <div style={{ height: 56 }} />
    </div>
  );
}
