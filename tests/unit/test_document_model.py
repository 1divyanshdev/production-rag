from datetime import datetime

import pytest
from pydantic import ValidationError

from rag_core.models.document import Document, DocumentMetadata

REQUIRED_FIELDS = [
    "document_id",
    "filename",
    "file_hash",
    "file_size_bytes",
    "page_number",
    "total_pages",
]


def build_metadata(**overrides) -> DocumentMetadata:
    values = {
        "document_id": "11111111-1111-1111-1111-111111111111",
        "filename": "doc.pdf",
        "file_hash": "ab" * 32,
        "file_size_bytes": 2048,
        "page_number": 1,
        "total_pages": 5,
    }
    values.update(overrides)
    return DocumentMetadata(**values)


class TestDocumentMetadata:
    def test_defaults_applied(self):
        meta = build_metadata()

        assert meta.file_type == "pdf"
        assert meta.extra == {}
        datetime.fromisoformat(meta.created_at)  # must be valid ISO 8601

    def test_explicit_values_stored(self):
        meta = build_metadata(extra={"author": "Ada"}, page_number=3)

        assert meta.extra == {"author": "Ada"}
        assert meta.page_number == 3

    @pytest.mark.parametrize("field", REQUIRED_FIELDS)
    def test_missing_required_field_rejected(self, field):
        values = {
            "document_id": "x",
            "filename": "f.pdf",
            "file_hash": "h",
            "file_size_bytes": 1,
            "page_number": 1,
            "total_pages": 1,
        }
        del values[field]

        with pytest.raises(ValidationError):
            DocumentMetadata(**values)


class TestDocument:
    def test_to_dict_contains_content_and_metadata(self):
        doc = Document(page_content="hello world", metadata=build_metadata())

        payload = doc.to_dict()

        assert payload["page_content"] == "hello world"
        assert payload["metadata"]["filename"] == "doc.pdf"

    def test_serialization_round_trip_preserves_instance(self):
        doc = Document(page_content="round trip", metadata=build_metadata())

        restored = Document.model_validate(doc.to_dict())

        assert restored == doc
