import pytest

from backend.app.core.exceptions import PDFParseError
from backend.app.services.pdf_parser import PDFParser

PAGE_TEXTS = [
    "Alpha page: retrieval augmented generation",
    "Beta page: vector similarity search",
]


class TestParsePdfHappyPath:
    def test_path_and_bytes_sources_agree(self, tmp_path, make_pdf_bytes):
        data = make_pdf_bytes(PAGE_TEXTS)
        pdf_path = tmp_path / "sample.pdf"
        pdf_path.write_bytes(data)

        from_path, total_from_path = PDFParser.parse_pdf(str(pdf_path))
        from_bytes, total_from_bytes = PDFParser.parse_pdf(data)

        assert from_path == from_bytes
        assert total_from_path == total_from_bytes == 2

    def test_pages_are_one_indexed_in_order(self, make_pdf_bytes):
        pages, total = PDFParser.parse_pdf(make_pdf_bytes(PAGE_TEXTS))

        assert [p["page_number"] for p in pages] == [1, 2]
        assert total == 2

    def test_page_boundaries_preserved(self, make_pdf_bytes):
        pages, _ = PDFParser.parse_pdf(make_pdf_bytes(PAGE_TEXTS))

        assert "Alpha page" in pages[0]["text"]
        assert "vector similarity" in pages[1]["text"]
        assert "Beta page" not in pages[0]["text"]


class TestParsePdfEdgeCases:
    def test_blank_page_preserved_with_empty_text(self, make_pdf_bytes):
        pages, total = PDFParser.parse_pdf(make_pdf_bytes(["first", "", "third"]))

        assert total == 3
        assert pages[1]["text"] == ""
        assert pages[0]["text"] and pages[2]["text"]

    def test_non_str_or_bytes_source_raises_value_error(self):
        with pytest.raises(ValueError):
            PDFParser.parse_pdf(12345)

    def test_corrupt_bytes_raise_pdf_parse_error(self):
        with pytest.raises(PDFParseError):
            PDFParser.parse_pdf(b"definitely not a real pdf payload")

    def test_encrypted_pdf_raises_pdf_parse_error(self, make_encrypted_pdf_bytes):
        data, _password = make_encrypted_pdf_bytes(["classified"])

        with pytest.raises(PDFParseError, match="encrypted"):
            PDFParser.parse_pdf(data)


class TestCleanText:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("", ""),
            ("\x00hidden\x00nulls", "hiddennulls"),
            ("line one\r\nline two\rline three", "line one\nline two\nline three"),
            ("\n\n  padded content  \n", "padded content"),
            ("no change", "no change"),
        ],
    )
    def test_cleaning_rules(self, raw, expected):
        assert PDFParser._clean_text(raw) == expected
