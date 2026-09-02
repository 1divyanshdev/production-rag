import logging

import pytest

from backend.app.models.document import Document, DocumentMetadata
from backend.app.services.chunking_service import ChunkingService
from backend.app.services.ingestion_service import DocumentIngestionService
from backend.app.services.text_splitter import RecursiveTextSplitter


def make_document(
    content,
    page_number=1,
    total_pages=1,
    document_id="11111111-1111-1111-1111-111111111111",
    filename="report.pdf",
):
    metadata = DocumentMetadata(
        document_id=document_id,
        filename=filename,
        file_hash="ab" * 32,
        file_size_bytes=1024,
        page_number=page_number,
        total_pages=total_pages,
        extra={"category": "docs"},
    )
    return Document(page_content=content, metadata=metadata)


@pytest.fixture
def service():
    return ChunkingService()


class TestChunkDocuments:
    def test_short_pages_become_one_chunk_each(self, service):
        docs = [
            make_document("Page one text.", page_number=1, total_pages=2),
            make_document("Page two text.", page_number=2, total_pages=2),
        ]

        chunks = service.chunk_documents(docs)

        assert len(chunks) == 2
        assert [c.metadata.page_number for c in chunks] == [1, 2]
        assert [c.content for c in chunks] == ["Page one text.", "Page two text."]

    def test_lineage_fields_inherited_from_source_page(self, service):
        docs = [make_document("Some content.")]

        chunk = service.chunk_documents(docs)[0]
        meta = chunk.metadata

        assert meta.document_id == docs[0].metadata.document_id
        assert meta.filename == "report.pdf"
        assert meta.file_hash == "ab" * 32
        assert meta.total_pages == 1
        assert meta.extra == {"category": "docs"}

    def test_chunk_indices_are_global_and_dense(self, service):
        splitter = RecursiveTextSplitter(chunk_size=100, chunk_overlap=0)
        svc = ChunkingService(splitter=splitter)
        long_text = "word " * 60  # ~300 chars -> multiple chunks per page
        docs = [
            make_document(long_text, page_number=1, total_pages=2),
            make_document(long_text, page_number=2, total_pages=2),
        ]

        chunks = svc.chunk_documents(docs)

        assert len(chunks) > 2
        assert [c.metadata.chunk_index for c in chunks] == list(range(len(chunks)))
        assert all(c.metadata.total_chunks == len(chunks) for c in chunks)

    def test_offsets_locate_chunk_inside_its_page(self, service):
        splitter = RecursiveTextSplitter(chunk_size=100, chunk_overlap=20)
        svc = ChunkingService(splitter=splitter)
        page_text = ("Sentence number %d sits here. " % 1) * 25
        docs = [make_document(page_text)]

        chunks = svc.chunk_documents(docs)

        for chunk in chunks:
            source_span = page_text[chunk.metadata.start_offset:chunk.metadata.end_offset]
            assert source_span == chunk.content

    def test_documents_grouped_by_parent_document(self, service):
        docs = [
            make_document("A doc content.", document_id="doc-a", page_number=1),
            make_document("B doc content.", document_id="doc-b", page_number=1),
            make_document("A doc page two.", document_id="doc-a", page_number=2),
        ]

        chunks = service.chunk_documents(docs)

        a_chunks = [c for c in chunks if c.metadata.document_id == "doc-a"]
        b_chunks = [c for c in chunks if c.metadata.document_id == "doc-b"]
        assert len(a_chunks) == 2 and len(b_chunks) == 1
        assert [c.metadata.chunk_index for c in a_chunks] == [0, 1]
        assert all(c.metadata.total_chunks == 2 for c in a_chunks)
        assert b_chunks[0].metadata.total_chunks == 1


class TestEdgeCases:
    def test_empty_input_returns_empty_list(self, service):
        assert service.chunk_documents([]) == []

    def test_non_document_item_rejected(self, service):
        with pytest.raises(ValueError):
            service.chunk_documents(["not a document"])

    def test_blank_page_skipped_with_warning(self, caplog, service):
        blank = make_document("", page_number=2, total_pages=3)
        normal = make_document("real text", page_number=1, total_pages=3)

        with caplog.at_level(
            logging.WARNING, logger="backend.app.services.chunking_service"
        ):
            chunks = service.chunk_documents([blank, normal])

        assert len(chunks) == 1
        assert chunks[0].metadata.page_number == 1
        assert "Skipping page 2" in caplog.text


class TestCustomSplitterInjection:
    def test_custom_splitter_settings_are_respected(self):
        tiny_splitter = RecursiveTextSplitter(chunk_size=30, chunk_overlap=5)
        service = ChunkingService(splitter=tiny_splitter)
        long_line = "abcdefghijklmnopqrstuvwxyz" * 4  # 104 chars, no separators

        chunks = service.chunk_documents([make_document(long_line)])

        assert len(chunks) >= 3
        assert all(len(c.content) <= 30 for c in chunks)


class TestIngestionIntegration:
    def test_ingestion_output_flows_through_chunking(self, make_pdf_bytes):
        data = make_pdf_bytes([
            "First page about retrieval augmented generation systems.",
            "Second page discusses vector databases and embeddings.",
        ])
        documents = DocumentIngestionService().ingest_pdf(data, filename="pipeline.pdf")

        chunks = ChunkingService().chunk_documents(documents)

        assert len(chunks) >= 2
        assert {c.metadata.page_number for c in chunks} == {1, 2}
        assert all(
            c.metadata.file_hash == documents[0].metadata.file_hash for c in chunks
        )
        assert all(c.metadata.total_chunks == len(chunks) for c in chunks)
