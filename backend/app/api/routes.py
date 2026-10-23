"""API routes: document indexing and grounded question answering."""
import logging

from fastapi import APIRouter, Depends, Request, UploadFile

from backend.app.api.deps import Services, get_services
from backend.app.api.schemas import (
    AskRequest,
    AskResponse,
    DeleteResponse,
    DocumentSummary,
    HealthResponse,
    IndexResponse,
    SourceCitation,
    StatsResponse,
)
from backend.app.core.exceptions import LLMError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["rag"])

MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version="0.1.0")


@router.post("/documents", response_model=IndexResponse)
async def upload_document(
    request: Request,
    file: UploadFile,
    services: Services = Depends(get_services),
) -> IndexResponse:
    """Upload a PDF: ingest -> chunk -> embed -> vector index.

    Re-uploading an identical file is a no-op (hash dedup).
    """
    if not (file.filename or "").lower().endswith(".pdf"):
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Only .pdf files are supported.")

    content = await file.read()
    if len(content) == 0:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(content) > MAX_UPLOAD_BYTES:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=413, detail="File exceeds the 50 MB upload limit."
        )

    result = services.pipeline.index_pdf(content, filename=file.filename)
    return IndexResponse(
        filename=result.filename,
        indexed_chunks=result.indexed_chunks,
        skipped_duplicate=result.skipped_duplicate,
        document_id=result.document_id,
    )


@router.post("/ask", response_model=AskResponse)
def ask(
    payload: AskRequest,
    services: Services = Depends(get_services),
) -> AskResponse:
    """Ask a question over the indexed corpus; returns a grounded answer
    with source citations. Low retrieval confidence yields a refusal."""
    try:
        answer = services.generation.ask(
            payload.question,
            document_id=payload.document_id,
            extra_filters=payload.extra_filters,
            top_k=payload.top_k,
        )
    except LLMError as exc:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=503,
            detail=f"LLM backend unavailable: {exc}",
        ) from exc

    return AskResponse(
        question=answer.question,
        answer=answer.answer,
        sources=[SourceCitation(**s) for s in answer.sources],
        refused=answer.refused,
        cited_indices=answer.cited_indices,
    )


@router.get("/stats", response_model=StatsResponse)
def stats(services: Services = Depends(get_services)) -> StatsResponse:
    return StatsResponse(
        collection=services.store.settings.collection,
        total_chunks=services.store.count(),
    )


@router.get("/documents", response_model=list[DocumentSummary])
def list_documents(
    services: Services = Depends(get_services),
) -> list[DocumentSummary]:
    """List every distinct indexed document with chunk counts."""
    return [
        DocumentSummary(**doc) for doc in services.store.list_documents()
    ]


@router.delete("/documents/{document_id}", response_model=DeleteResponse)
def delete_document(
    document_id: str,
    services: Services = Depends(get_services),
) -> DeleteResponse:
    """Delete all indexed chunks of one document."""
    deleted = services.store.delete_document(document_id)
    if deleted == 0:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404, detail=f"Document '{document_id}' not found in index."
        )
    return DeleteResponse(document_id=document_id, deleted_chunks=deleted)
