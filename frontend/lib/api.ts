// Typed client for the production-rag FastAPI backend.
// Single seam: every backend call goes through here, mirroring
// backend/app/api/schemas.py one-to-one.

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

// ---- response types (mirror backend schemas) ----

export interface HealthResponse {
  status: string;
  version: string;
}

export interface IndexResponse {
  filename: string;
  indexed_chunks: number;
  skipped_duplicate: boolean;
  document_id: string | null;
}

export interface SourceCitation {
  filename: string;
  page_number: number;
  chunk_index: number;
  document_id: string;
  score: number;
}

export interface AskResponse {
  question: string;
  answer: string;
  sources: SourceCitation[];
  refused: boolean;
  cited_indices: number[];
}

export interface DocumentSummary {
  document_id: string;
  filename: string;
  file_hash: string;
  total_pages: number;
  chunk_count: number;
}

export interface StatsResponse {
  collection: string;
  total_chunks: number;
}

export interface DeleteResponse {
  document_id: string;
  deleted_chunks: number;
}

// ---- error handling ----

async function parseError(resp: Response): Promise<never> {
  let detail = `Request failed (${resp.status})`;
  try {
    const body = await resp.json();
    if (body?.detail) detail = String(body.detail);
  } catch {
    /* keep default message */
  }
  throw new Error(detail);
}

// ---- API calls ----

export async function getHealth(): Promise<HealthResponse> {
  const resp = await fetch(`${API_URL}/api/health`);
  if (!resp.ok) return parseError(resp);
  return resp.json();
}

export async function uploadDocument(file: File): Promise<IndexResponse> {
  const form = new FormData();
  form.append("file", file);
  const resp = await fetch(`${API_URL}/api/documents`, {
    method: "POST",
    body: form,
  });
  if (!resp.ok) return parseError(resp);
  return resp.json();
}

export async function askQuestion(params: {
  question: string;
  document_id?: string;
  top_k?: number;
}): Promise<AskResponse> {
  const resp = await fetch(`${API_URL}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
  });
  if (!resp.ok) return parseError(resp);
  return resp.json();
}

export async function listDocuments(): Promise<DocumentSummary[]> {
  const resp = await fetch(`${API_URL}/api/documents`);
  if (!resp.ok) return parseError(resp);
  return resp.json();
}

export async function deleteDocument(documentId: string): Promise<DeleteResponse> {
  const resp = await fetch(`${API_URL}/api/documents/${documentId}`, {
    method: "DELETE",
  });
  if (!resp.ok) return parseError(resp);
  return resp.json();
}

export async function getStats(): Promise<StatsResponse> {
  const resp = await fetch(`${API_URL}/api/stats`);
  if (!resp.ok) return parseError(resp);
  return resp.json();
}
