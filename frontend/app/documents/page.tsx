"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import {
  DocumentSummary,
  IndexResponse,
  StatsResponse,
  deleteDocument,
  getStats,
  listDocuments,
  uploadDocument,
} from "@/lib/api";

export default function DocumentsPage() {
  const [docs, setDocs] = useState<DocumentSummary[]>([]);
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragover, setDragover] = useState(false);
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
    if (!confirm(`Delete all ${doc.chunk_count} chunks of "${doc.filename}"?`))
      return;
    setError(null);
    try {
      const resp = await deleteDocument(doc.document_id);
      setMessage(`Deleted ${resp.deleted_chunks} chunk(s) from ${doc.filename}.`);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <div className="container">
      <div className="page-head">
        <h1>Documents</h1>
        <p>
          {stats
            ? `${stats.total_chunks} chunks across ${docs.length} document(s), live in the ${stats.collection} collection.`
            : "Upload PDFs to build your knowledge base."}
        </p>
      </div>

      <div className="card" style={{ padding: 0, border: "none", background: "transparent" }}>
        <div
          className={`dropzone${dragover ? " dragover" : ""}`}
          onClick={() => fileInput.current?.click()}
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
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
              <span className="spinner" style={{ borderTopColor: "#818cf8", borderColor: "rgba(129,140,248,0.3)" }} />
              <span className="dz-title">
                Indexing — parse → chunk → embed → store...
              </span>
            </div>
          ) : (
            <>
              <div className="dz-title">Drop a PDF here, or click to browse</div>
              <div className="dz-sub">
                Duplicate files are detected by content hash and skipped automatically.
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

        {message && <div className="ok-box" style={{ marginTop: 14 }}>{message}</div>}
        {error && <div className="error-box">{error}</div>}
      </div>

      <div className="result-card" style={{ marginTop: 20 }}>
        <div className="result-title">
          Knowledge base{" "}
          {stats && <span className="badge info">{stats.total_chunks} chunks</span>}
        </div>
        {docs.length === 0 ? (
          <p className="muted" style={{ margin: 0 }}>
            Nothing indexed yet. Upload a PDF above, then ask questions on the{" "}
            <a href="/" style={{ color: "#818cf8" }}>Ask page</a>.
          </p>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table className="doc-table">
              <thead>
                <tr>
                  <th>File</th>
                  <th>Pages</th>
                  <th>Chunks</th>
                  <th>Content hash</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {docs.map((doc) => (
                  <tr key={doc.document_id}>
                    <td className="source-name">{doc.filename}</td>
                    <td>{doc.total_pages}</td>
                    <td>
                      <span className="badge info">{doc.chunk_count}</span>
                    </td>
                    <td className="mono">{doc.file_hash.slice(0, 12)}…</td>
                    <td style={{ textAlign: "right" }}>
                      <button className="btn-danger" onClick={() => handleDelete(doc)}>
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
