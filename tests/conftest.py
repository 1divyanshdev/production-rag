"""Shared fixtures for the ingestion test suite.

All PDFs are generated in-memory with PyMuPDF so the suite is fast,
offline, and deterministic.
"""
import io

import pytest
import pymupdf


@pytest.fixture
def make_pdf_bytes():
    """Factory fixture: build_pdf_bytes(["page one text", "", "page three"]) -> bytes."""

    def _build(page_texts) -> bytes:
        doc = pymupdf.open()
        try:
            for text in page_texts:
                page = doc.new_page()
                if text:
                    page.insert_text((50, 50), text, fontsize=12)
            return doc.tobytes()
        finally:
            doc.close()

    return _build


@pytest.fixture
def make_encrypted_pdf_bytes():
    """Factory fixture: returns (encrypted_pdf_bytes, user_password)."""

    def _build(page_texts, password="test-passphrase") -> tuple:
        doc = pymupdf.open()
        try:
            for text in page_texts:
                page = doc.new_page()
                if text:
                    page.insert_text((50, 50), text, fontsize=12)
            buffer = io.BytesIO()
            doc.save(
                buffer,
                encryption=pymupdf.PDF_ENCRYPT_AES_256,
                user_pw=password,
                owner_pw=password,
            )
            return buffer.getvalue(), password
        finally:
            doc.close()

    return _build
