import pytest

from backend.app.services.text_splitter import RecursiveTextSplitter


def build_paragraphic_text(paragraph_count, words_per_paragraph=30):
    """Multi-paragraph text sized to force several chunks at default settings."""
    paragraphs = [
        f"Paragraph {i}: " + " ".join(f"word{i}x{j}" for j in range(words_per_paragraph))
        for i in range(paragraph_count)
    ]
    return "\n\n".join(paragraphs)


def assert_span_invariants(source, chunks, *, overlap_expected=True):
    """
    Core contract of the splitter:
      1. Every chunk reproduces its exact source span.
      2. Chunks cover the source in order, without gaps.
      3. No chunk exceeds chunk_size.
    """
    assert chunks, "expected at least one chunk"
    assert chunks[0].start == 0
    assert chunks[-1].end == len(source)

    for chunk in chunks:
        assert source[chunk.start:chunk.end] == chunk.text
        assert len(chunk.text) <= 1000

    for prev, nxt in zip(chunks, chunks[1:]):
        assert nxt.start <= prev.end, "chunks must not leave gaps"
        if overlap_expected:
            assert nxt.start < prev.end, "expected overlap between consecutive chunks"


class TestValidation:
    def test_zero_chunk_size_rejected(self):
        with pytest.raises(ValueError):
            RecursiveTextSplitter(chunk_size=0)

    def test_negative_overlap_rejected(self):
        with pytest.raises(ValueError):
            RecursiveTextSplitter(chunk_size=100, chunk_overlap=-1)

    def test_overlap_must_be_smaller_than_chunk_size(self):
        with pytest.raises(ValueError):
            RecursiveTextSplitter(chunk_size=100, chunk_overlap=100)

    def test_empty_separator_appended_automatically(self):
        splitter = RecursiveTextSplitter(separators=["\n\n"])
        assert splitter.separators[-1] == ""


class TestBasicSplitting:
    def test_short_text_returns_single_full_span_chunk(self):
        splitter = RecursiveTextSplitter()
        source = "A short page of text."

        chunks = splitter.split_text_with_offsets(source)

        assert len(chunks) == 1
        assert chunks[0].text == source
        assert (chunks[0].start, chunks[0].end) == (0, len(source))

    @pytest.mark.parametrize("text", ["", "   ", "\n\n"])
    def test_blank_input_returns_no_chunks(self, text):
        assert RecursiveTextSplitter().split_text_with_offsets(text) == []

    def test_split_text_matches_offset_variant(self):
        splitter = RecursiveTextSplitter()
        source = build_paragraphic_text(6)

        plain = splitter.split_text(source)
        spanned = splitter.split_text_with_offsets(source)

        assert plain == [c.text for c in spanned]

    def test_deterministic_output(self):
        splitter = RecursiveTextSplitter()
        source = build_paragraphic_text(10)

        assert splitter.split_text(source) == splitter.split_text(source)


class TestRecursiveBehavior:
    def test_greedy_packing_prefers_paragraph_boundaries(self):
        # Each paragraph fits in chunk_size; together they don't. Chunks fill
        # greedily with WHOLE paragraphs - boundaries land only on "\n\n".
        splitter = RecursiveTextSplitter(
            chunk_size=300, chunk_overlap=0, separators=["\n\n"]
        )
        paragraphs = ["alpha " * 20, "beta " * 20, "gamma " * 20]  # 120 chars each
        source = "\n\n".join(paragraphs)                           # 364 chars

        chunks = splitter.split_text_with_offsets(source)

        assert [c.text for c in chunks] == [
            "alpha " * 20 + "\n\n" + "beta " * 20 + "\n\n",
            "gamma " * 20,
        ]
        for chunk in chunks:
            assert source[chunk.start:chunk.end] == chunk.text

    def test_sentence_fallback_when_paragraph_too_large(self):
        # A giant "paragraph" made of sentences must fall through to ". "
        # splitting rather than hard cuts mid-sentence.
        splitter = RecursiveTextSplitter(chunk_size=120, chunk_overlap=0)
        source = "Sentence one here. " * 30

        chunks = splitter.split_text_with_offsets(source)

        assert_span_invariants(source, chunks, overlap_expected=False)
        # No sentence is cut in half: every chunk boundary aligns with ". "
        for chunk in chunks[:-1]:
            assert chunk.text.endswith(". ")

    def test_unbreakable_string_falls_back_to_hard_cuts(self):
        splitter = RecursiveTextSplitter(chunk_size=50, chunk_overlap=0)
        source = "x" * 137

        chunks = splitter.split_text_with_offsets(source)

        assert [len(c.text) for c in chunks] == [50, 50, 37]
        assert "".join(c.text for c in chunks) == source


class TestOverlap:
    def test_consecutive_chunks_overlap_at_sentence_level(self):
        # Overlap works at the granularity of the pieces actually used.
        # Short sentences (< overlap window) guarantee real overlap.
        splitter = RecursiveTextSplitter(chunk_size=120, chunk_overlap=60)
        source = "".join(f"Sentence {i} talks about stuff here. " for i in range(40))

        chunks = splitter.split_text_with_offsets(source)

        assert len(chunks) > 2
        assert_span_invariants(source, chunks, overlap_expected=True)
        # The overlapping region is literally shared text between neighbors.
        for prev, nxt in zip(chunks, chunks[1:]):
            shared = source[nxt.start:prev.end]
            assert prev.text.endswith(shared)
            assert nxt.text.startswith(shared)

    def test_zero_overlap_produces_gapless_tiling(self):
        splitter = RecursiveTextSplitter(chunk_size=200, chunk_overlap=0)
        source = build_paragraphic_text(12, words_per_paragraph=10)

        chunks = splitter.split_text_with_offsets(source)

        for prev, nxt in zip(chunks, chunks[1:]):
            assert nxt.start == prev.end

    def test_all_chunks_respect_max_size_even_after_rollover(self):
        # Adversarial layout: tiny pieces just under overlap threshold so the
        # tail-reuse path is exercised repeatedly.
        splitter = RecursiveTextSplitter(chunk_size=100, chunk_overlap=60)
        source = ("ab" * 30 + "\n") * 40

        chunks = splitter.split_text_with_offsets(source)

        for chunk in chunks:
            assert len(chunk.text) <= 100
