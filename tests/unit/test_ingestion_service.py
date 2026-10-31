import hashlib
import logging

import pytest

from rag_core.exceptions import NoTextExtractedError, PDFParseError
from rag_core.models.document import Document
from rag_core.ingestion.ingestion_service import DocumentIngestionService


@pytest.fixture
def service():
    return DocumentIngestionService()


class TestHappyPath:
    def test_ingest_from_path_defaults_filename(self, tmp_path, service, make_pdf_bytes):
        data = make_pdf_bytes(["first page words", "second page words"])
        pdf_path = tmp_path / "report.pdf"
        pdf_path.write_bytes(data)

        docs = service.ingest_pdf(str(pdf_path))

        assert len(docs) == 2
        assert docs[0].metadata.filename == "report.pdf"
        assert "second page words" in docs[1].page_content

    def test_ingest_from_bytes_with_explicit_filename(self, service, make_pdf_bytes):
        data = make_pdf_bytes(["bytes page"])

        docs = service.ingest_pdf(data, filename="uploaded.pdf")

        assert len(docs) == 1
        assert docs[0].metadata.filename == "uploaded.pdf"

    def test_identity_fields_shared_across_pages_and_correct(
        self, service, make_pdf_bytes
    ):
        data = make_pdf_bytes(["one", "two", "three"])

        docs = service.ingest_pdf(data, filename="multi.pdf")

        assert {d.metadata.file_hash for d in docs} == {hashlib.sha256(data).hexdigest()}
        assert len({d.metadata.document_id for d in docs}) == 1
        assert all(d.metadata.file_size_bytes == len(data) for d in docs)
        assert all(d.metadata.total_pages == 3 for d in docs)
        assert [d.metadata.page_number for d in docs] == [1, 2, 3]

    def test_custom_metadata_lands_in_extra(self, service, make_pdf_bytes):
        docs = service.ingest_pdf(
            make_pdf_bytes(["content"]),
            filename="contracts.pdf",
            custom_metadata={"category": "contracts"},
        )

        assert docs[0].metadata.extra == {"category": "contracts"}

    def test_returns_document_instances(self, service, make_pdf_bytes):
        docs = service.ingest_pdf(make_pdf_bytes(["a"]), filename="t.pdf")

        assert all(isinstance(d, Document) for d in docs)


class TestEmptyPagePolicy:
    def test_blank_pages_skipped_but_lineage_kept(
        self, caplog, service, make_pdf_bytes
    ):
        data = make_pdf_bytes(["real text", "", "more real text"])

        with caplog.at_level(
            logging.WARNING, logger="backend.app.services.ingestion_service"
        ):
            docs = service.ingest_pdf(data, filename="gaps.pdf")

        assert [d.metadata.page_number for d in docs] == [1, 3]
        assert all(d.metadata.total_pages == 3 for d in docs)
        assert "Skipped 1 page(s)" in caplog.text
        assert "'gaps.pdf'" in caplog.text

    def test_all_blank_document_raises_no_text_extracted(
        self, service, make_pdf_bytes
    ):
        data = make_pdf_bytes(["", ""])

        with pytest.raises(NoTextExtractedError):
            service.ingest_pdf(data, filename="scanned.pdf")


class TestInvalidInputs:
    def test_bytes_without_filename_raises_value_error(
        self, service, make_pdf_bytes
    ):
        with pytest.raises(ValueError):
            service.ingest_pdf(make_pdf_bytes(["x"]))

    def test_missing_path_raises_file_not_found(self, service, tmp_path):
        with pytest.raises(FileNotFoundError):
            service.ingest_pdf(str(tmp_path / "ghost.pdf"))

    def test_unsupported_source_type_raises_value_error(self, service):
        with pytest.raises(ValueError):
            service.ingest_pdf(42)

    def test_corrupt_bytes_surface_as_pdf_parse_error(self, service):
        with pytest.raises(PDFParseError):
            service.ingest_pdf(b"junk bytes not a pdf", filename="broken.pdf")
