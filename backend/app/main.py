"""
FastAPI application factory.

Domain exceptions are translated to precise HTTP status codes at this
boundary; deeper layers raise typed errors and never touch HTTP.

Run locally:
    .venv\\Scripts\\python.exe -m uvicorn backend.app.main:app --reload
"""
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import router
from backend.app.core.exceptions import (
    EmbeddingError,
    LLMError,
    NoTextExtractedError,
    PDFParseError,
    VectorStoreError,
)

logger = logging.getLogger(__name__)

API_VERSION = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_dotenv()  # populate env from .env when present
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logger.info("production-rag API v%s starting", API_VERSION)
    yield
    logger.info("production-rag API shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title="production-rag API",
        version=API_VERSION,
        description="Document indexing and grounded question answering.",
        lifespan=lifespan,
    )

    # Open CORS for the future Next.js frontend (tighten origins later).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    # ---- domain exception -> HTTP mapping ----

    @app.exception_handler(PDFParseError)
    def _pdf_parse_error(request: Request, exc: PDFParseError):
        raise HTTPException(status_code=400, detail=str(exc))

    @app.exception_handler(NoTextExtractedError)
    def _no_text_error(request: Request, exc: NoTextExtractedError):
        raise HTTPException(
            status_code=422,
            detail=f"{exc} (scanned/image-only PDFs require OCR, which is not enabled).",
        )

    @app.exception_handler(EmbeddingError)
    def _embedding_error(request: Request, exc: EmbeddingError):
        logger.error("Embedding failure: %s", exc)
        raise HTTPException(status_code=502, detail=f"Embedding provider error: {exc}")

    @app.exception_handler(LLMError)
    def _llm_error(request: Request, exc: LLMError):
        logger.error("LLM failure: %s", exc)
        raise HTTPException(status_code=502, detail=f"LLM provider error: {exc}")

    @app.exception_handler(VectorStoreError)
    def _vector_store_error(request: Request, exc: VectorStoreError):
        logger.error("Vector store failure: %s", exc)
        raise HTTPException(status_code=500, detail=f"Vector store error: {exc}")

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
