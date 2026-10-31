from typing import List, Tuple, Union

import pymupdf

from rag_core.exceptions import PDFParseError


class PDFParser:
    """
    Parser service dedicated to extracting raw text from digital PDFs using PyMuPDF (fitz).
    Separated from ingestion business logic for single-responsibility design.
    """

    @staticmethod
    def parse_pdf(file_source: Union[str, bytes]) -> Tuple[List[dict], int]:
        """
        Parses a PDF from file path or bytes and returns raw page content and page counts.

        Args:
            file_source: File path (str) or raw binary content (bytes) of the PDF.

        Returns:
            Tuple of (pages, total_pages) where pages is a list of dicts:
            [{'page_number': int (1-indexed), 'text': str}]. Pages with no
            extractable text are included with empty text; filtering policy
            belongs to the caller.

        Raises:
            ValueError: If file_source is neither str nor bytes.
            PDFParseError: If the PDF cannot be opened, is corrupt, or is encrypted.
        """
        if isinstance(file_source, bytes):
            try:
                doc = pymupdf.open(stream=file_source, filetype="pdf")
            except Exception as exc:
                raise PDFParseError(f"Could not open PDF from bytes: {exc}") from exc
        elif isinstance(file_source, str):
            try:
                doc = pymupdf.open(file_source)
            except Exception as exc:
                raise PDFParseError(f"Could not open PDF at path '{file_source}': {exc}") from exc
        else:
            raise ValueError("Unsupported file source. Expected file path (str) or raw bytes.")

        if doc.needs_pass or doc.is_encrypted:
            doc.close()
            raise PDFParseError(
                "PDF is encrypted/password-protected; text extraction is not possible."
            )

        pages_content = []
        total_pages = len(doc)
        if total_pages == 0:
            doc.close()
            raise PDFParseError("PDF contains zero pages; the file may be corrupt.")

        try:
            for page_index in range(total_pages):
                page = doc[page_index]
                # Extract text using PyMuPDF text layout engine
                raw_text = page.get_text("text")

                # Clean null characters or extreme white spaces while keeping paragraph structures
                cleaned_text = PDFParser._clean_text(raw_text)

                pages_content.append({
                    "page_number": page_index + 1,  # 1-indexed
                    "text": cleaned_text
                })
        finally:
            doc.close()

        return pages_content, total_pages

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Basic text cleaning on raw extracted page text.
        Removes null bytes and standardizes whitespace without losing paragraph context.
        """
        if not text:
            return ""
        
        # Remove null characters which sometimes appear in corrupted PDF font encodings
        text = text.replace("\x00", "")

        # Normalize carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Strip leading/trailing blank lines
        return text.strip()
