"""
Recursive character text splitter.

Splits long text into chunks no longer than ``chunk_size`` characters,
preferring the highest-level separator that fits (paragraphs before lines
before sentences before words), falling back to hard character cuts only
when nothing else applies.

This is our own implementation of the well-known recursive strategy
(the same idea behind LangChain's RecursiveCharacterTextSplitter), written
explicitly so the mechanics stay transparent and fully testable.

Every emitted chunk carries its exact character span in the SOURCE text.
Invariant: source_text[start:end] == chunk_text for every chunk, including
overlap regions (an overlapping tail is literally shared between neighbors).
"""
import logging
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TextPiece:
    """An atomic fragment of the source text with its absolute span."""
    text: str
    start: int
    end: int


class RecursiveTextSplitter:
    DEFAULT_SEPARATORS: Tuple[str, ...] = ("\n\n", "\n", ". ", " ", "")

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 150,
        separators: Optional[Sequence[str]] = None,
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer.")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap cannot be negative.")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be strictly smaller than chunk_size.")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        seps = tuple(separators) if separators is not None else self.DEFAULT_SEPARATORS
        # The empty separator is the mandatory last-resort terminator.
        self.separators = seps if seps and seps[-1] == "" else seps + ("",)

    def split_text(self, text: str) -> List[str]:
        """Split ``text`` and return only the chunk strings."""
        return [piece.text for piece in self.split_text_with_offsets(text)]

    def split_text_with_offsets(self, text: str) -> List[TextPiece]:
        """
        Split ``text`` into chunks carrying their exact (start, end) offsets
        in the input. Guaranteed: input[start:end] == chunk.text.
        """
        if not text or not text.strip():
            return []

        root = TextPiece(text=text, start=0, end=len(text))
        atomic_pieces = self._recursive_split(root, self.separators)
        return self._merge_with_overlap(atomic_pieces)

    def _recursive_split(self, piece: TextPiece, separators: Tuple[str, ...]) -> List[TextPiece]:
        """Return pieces each no longer than chunk_size, tiling ``piece`` exactly."""
        if len(piece.text) <= self.chunk_size:
            return [piece]

        # Pick the first separator present in this piece; "" is the hard-cut floor.
        separator = separators[-1]
        remaining = ()
        for i, sep in enumerate(separators):
            if sep == "":
                separator, remaining = "", ()
                break
            if sep in piece.text:
                separator, remaining = sep, separators[i + 1:]
                break

        segments = self._split_keeping_delimiter(piece, separator)

        result: List[TextPiece] = []
        for segment in segments:
            if not segment.text:
                continue
            if len(segment.text) <= self.chunk_size:
                result.append(segment)
            elif remaining:
                result.extend(self._recursive_split(segment, remaining))
            else:
                # No separator anywhere: hard character cuts.
                result.extend(self._hard_cut(segment))
        return result

    @staticmethod
    def _split_keeping_delimiter(piece: TextPiece, separator: str) -> List[TextPiece]:
        """
        Split on ``separator``, attaching each delimiter to the END of the
        preceding segment so segment spans tile the piece with no gaps.
        """
        if separator == "":
            return [piece]

        segments: List[TextPiece] = []
        cursor = 0
        while cursor < len(piece.text):
            idx = piece.text.find(separator, cursor)
            if idx == -1:
                segments.append(TextPiece(
                    text=piece.text[cursor:],
                    start=piece.start + cursor,
                    end=piece.end,
                ))
                break
            seg_end = idx + len(separator)
            segments.append(TextPiece(
                text=piece.text[cursor:seg_end],
                start=piece.start + cursor,
                end=piece.start + seg_end,
            ))
            cursor = seg_end
        return segments

    def _hard_cut(self, piece: TextPiece) -> List[TextPiece]:
        """Cut a separator-less piece blindly every chunk_size characters."""
        return [
            TextPiece(
                text=piece.text[offset:offset + self.chunk_size],
                start=piece.start + offset,
                end=piece.start + min(offset + self.chunk_size, len(piece.text)),
            )
            for offset in range(0, len(piece.text), self.chunk_size)
        ]

    def _merge_with_overlap(self, pieces: List[TextPiece]) -> List[TextPiece]:
        """
        Pack pieces into chunks up to chunk_size, carrying a trailing overlap
        of roughly chunk_overlap characters into the next chunk. Group spans
        remain contiguous tilings of the source, so offsets stay exact.
        """
        chunks: List[TextPiece] = []
        group: List[TextPiece] = []

        for piece in pieces:
            projected = sum(len(p.text) for p in group) + len(piece.text)
            if group and projected > self.chunk_size:
                chunks.append(self._join(group))

                # Reuse trailing pieces totalling <= overlap as the new head.
                tail: List[TextPiece] = []
                tail_length = 0
                for q in reversed(group):
                    if tail_length + len(q.text) > self.chunk_overlap:
                        break
                    tail.insert(0, q)
                    tail_length += len(q.text)

                # If the tail plus the pending piece would still overflow,
                # flush the tail as its own chunk and start clean.
                if tail and tail_length + len(piece.text) > self.chunk_size:
                    chunks.append(self._join(tail))
                    tail, tail_length = [], 0
                group = tail

            group.append(piece)

        if group:
            chunks.append(self._join(group))
        return chunks

    @staticmethod
    def _join(group: Sequence[TextPiece]) -> TextPiece:
        """Join a contiguous group of pieces back into one spanned chunk."""
        return TextPiece(
            text="".join(p.text for p in group),
            start=group[0].start,
            end=group[-1].end,
        )
