"""Hallucination detection guard (heuristic, model-agnostic).

This guard is designed to be lightweight and not depend on any specific LLM
provider. It focuses on simple, explainable heuristics that work well in
RAG-style scenarios:

- If the context provides retrieved documents, require that the answer
  references at least one citation marker like "[1]" or "[source]".
- Flag obviously speculative language when the policy is configured to
  enforce high factual confidence.

The goal is to provide a production-safe baseline implementation that teams
can extend with their own model- or retrieval-specific checks.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Optional

from lambdax.core.context import RequestContext
from lambdax.core.guard import Guard

logger = logging.getLogger(__name__)


class HallucinationGuard(Guard):
    """Detects potentially hallucinated or unsupported claims."""

    def _setup(self) -> None:
        # Whether to require citations when RAG context is present
        self.require_citations: bool = self.config.get("require_citations", True)
        # Phrases that suggest speculation or fabricated certainty
        self.speculative_markers = [
            "i'm making this up",
            "this may not be accurate",
            "not sure if this is true",
        ]
        # If True, speculative language in output will be blocked
        self.block_speculation: bool = self.config.get("block_speculation", False)

        logger.info(
            "HallucinationGuard initialized "
            f"(require_citations={self.require_citations}, "
            f"block_speculation={self.block_speculation})"
        )

    def _has_citation(self, text: str) -> bool:
        """Return True if the text appears to contain a citation marker."""
        return bool(re.search(r"\[[0-9]+\]", text) or re.search(r"\[source.*?\]", text, re.I))

    def _has_speculation(self, text: str) -> Optional[str]:
        """Return the first speculative marker found, if any."""
        lower = text.lower()
        for marker in self.speculative_markers:
            if marker in lower:
                return marker
        return None

    async def inspect_input(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        # Hallucination is primarily an output-side concern; no-op for input.
        return None

    async def inspect_output(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """Check output for signs of hallucination."""
        metadata = context.metadata or {}

        # 1) RAG-style citation enforcement
        retrieved_docs = metadata.get("retrieved_documents") or metadata.get("rag_documents")
        if self.require_citations and retrieved_docs:
            if not self._has_citation(text):
                return {
                    "reason": "RAG answer missing citations for retrieved documents",
                    "guard": self.name,
                    "require_citations": self.require_citations,
                    "doc_count": len(retrieved_docs),
                }

        # 2) Speculative language blocking (optional)
        if self.block_speculation:
            marker = self._has_speculation(text)
            if marker:
                return {
                    "reason": "Speculative language detected in output",
                    "marker": marker,
                    "guard": self.name,
                }

        return None

