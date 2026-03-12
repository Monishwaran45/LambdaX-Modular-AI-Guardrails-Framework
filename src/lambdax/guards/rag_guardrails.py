"""RAG guardrails for retrieval-augmented generation.

This guard enforces basic alignment between retrieved context and generated
answers in RAG-style pipelines by checking for:

- Presence of answer text that is too short or empty when documents exist.
- Missing citation markers when configured to require citations.

It does not attempt deep semantic verification; instead, it provides a
lightweight policy hook that can be extended with retrieval-specific logic.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from lambdax.core.context import RequestContext
from lambdax.core.guard import Guard

logger = logging.getLogger(__name__)


class RagGuardrailsGuard(Guard):
    """Simple RAG-specific guard for answer/context consistency."""

    def _setup(self) -> None:
        # Minimum non-whitespace characters required if documents exist
        self.min_answer_chars: int = int(self.config.get("min_answer_chars", 32))
        # Whether to enforce that answers with documents must contain citations
        self.require_citations: bool = self.config.get("require_citations", True)
        logger.info(
            "RagGuardrailsGuard initialized "
            f"(min_answer_chars={self.min_answer_chars}, "
            f"require_citations={self.require_citations})"
        )

    def _has_citation(self, text: str) -> bool:
        return "[" in text and "]" in text

    async def inspect_input(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        # RAG checks are output-focused; no-op for input.
        return None

    async def inspect_output(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        metadata = context.metadata or {}
        docs = metadata.get("retrieved_documents") or metadata.get("rag_documents")
        if not docs:
            return None

        stripped = text.strip()
        if len(stripped) < self.min_answer_chars:
            return {
                "reason": "RAG answer too short given retrieved documents",
                "guard": self.name,
                "length": len(stripped),
                "min_answer_chars": self.min_answer_chars,
                "doc_count": len(docs),
            }

        if self.require_citations and not self._has_citation(text):
            return {
                "reason": "RAG answer missing citations for retrieved documents",
                "guard": self.name,
                "doc_count": len(docs),
            }

        return None

