"""
Generation service: grounded answer synthesis with citations.

Flow:
    question -> retrieve top-k chunks -> (low confidence? refuse)
             -> build numbered context -> LLM -> answer + sources

Grounding rules enforced by design:
  - The prompt instructs the model to answer ONLY from the numbered
    context and cite sources as [n].
  - If retrieval confidence is below score_threshold, the LLM is never
    called and the service returns a refusal - no hallucinated answers
    on empty/irrelevant indexes.
"""
import logging
import re
from dataclasses import dataclass, field
from typing import List, Optional

from backend.app.core.config import RetrievalSettings
from backend.app.core.exceptions import LLMError
from backend.app.models.retrieval import ScoredChunk
from backend.app.services.llm.base import LLMProvider
from backend.app.services.retrieval_service import RetrievalService

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a precise assistant answering questions about user-provided "
    "documents. Rules:\n"
    "1. Answer ONLY using the numbered context passages.\n"
    "2. Cite the passage numbers you used, like [1] or [2][4], inline.\n"
    "3. If the context does not contain the answer, reply exactly: "
    "'The documents do not contain enough information to answer this.'\n"
    "4. Do not use outside knowledge. Be concise."
)

REFUSAL_ANSWER = (
    "I could not find relevant information in the indexed documents "
    "to answer this question confidently."
)


@dataclass
class GeneratedAnswer:
    """Final RAG response with full source transparency."""

    question: str
    answer: str
    sources: List[dict] = field(default_factory=list)
    refused: bool = False

    @property
    def cited_indices(self) -> List[int]:
        """[n] markers found in the answer text."""
        return sorted({int(n) for n in re.findall(r"\[(\d+)\]", self.answer)})


class GenerationService:
    """Retrieve-then-generate with citations and confidence refusal."""

    def __init__(
        self,
        retrieval: RetrievalService,
        llm: LLMProvider,
        settings: Optional[RetrievalSettings] = None,
    ):
        self.retrieval = retrieval
        self.llm = llm
        self.settings = settings or retrieval.settings

    def ask(
        self,
        question: str,
        document_id: Optional[str] = None,
        extra_filters: Optional[dict] = None,
        top_k: Optional[int] = None,
    ) -> GeneratedAnswer:
        """Answer a question from the indexed corpus."""
        hits: List[ScoredChunk] = self.retrieval.retrieve(
            question,
            document_id=document_id,
            extra_filters=extra_filters,
            top_k=top_k,
        )

        # Low-confidence gate: best hit too weak -> refuse without LLM.
        if not hits or hits[0].score < self.settings.score_threshold:
            best = hits[0].score if hits else 0.0
            logger.info(
                "Refusing question (best score %.3f < threshold %.3f).",
                best,
                self.settings.score_threshold,
            )
            return GeneratedAnswer(
                question=question, answer=REFUSAL_ANSWER, sources=[], refused=True
            )

        user_prompt = self._build_context(question, hits)
        try:
            answer_text = self.llm.generate(SYSTEM_PROMPT, user_prompt)
        except LLMError as exc:
            logger.error("Generation failed: %s", exc)
            raise

        return GeneratedAnswer(
            question=question,
            answer=answer_text.strip(),
            sources=[hit.to_citation() for hit in hits],
        )

    @staticmethod
    def _build_context(question: str, hits: List[ScoredChunk]) -> str:
        """Numbered context blocks with page provenance for citations."""
        blocks = []
        for i, hit in enumerate(hits, start=1):
            meta = hit.chunk.metadata
            blocks.append(
                f"[{i}] (source: {meta.filename}, page {meta.page_number})\n"
                f"{hit.chunk.content}"
            )
        joined = "\n\n".join(blocks)
        return f"Context passages:\n\n{joined}\n\nQuestion: {question}"
