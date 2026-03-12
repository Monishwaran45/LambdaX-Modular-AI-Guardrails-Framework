"""Bias detection guard (rule-based).

This guard focuses on simple, transparent heuristics for catching obviously
biased generalizations without relying on large external models. It is meant
as a safe baseline that teams can extend with domain- and culture-specific
rules or ML classifiers.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from lambdax.core.context import RequestContext
from lambdax.core.guard import Guard

logger = logging.getLogger(__name__)


class BiasGuard(Guard):
    """Detects simple biased generalizations about protected groups."""

    def _setup(self) -> None:
        self.protected_groups: List[str] = self.config.get(
            "protected_groups",
            [
                "men",
                "women",
                "black people",
                "white people",
                "asians",
                "muslims",
                "christians",
                "jews",
                "jewish people",
                "immigrants",
            ],
        )
        # Patterns like "all X are", "X are all", "every X is"
        self.patterns = [
            r"\ball\s+{group}\s+are\b",
            r"\b{group}\s+are\s+all\b",
            r"\bevery\s+{group}\s+is\b",
        ]
        logger.info("BiasGuard initialized with %d protected groups", len(self.protected_groups))

    def _detect_bias(self, text: str) -> Optional[Dict[str, Any]]:
        lowered = text.lower()
        for group in self.protected_groups:
            escaped_group = re.escape(group.lower())
            for pattern_tpl in self.patterns:
                pattern = pattern_tpl.format(group=escaped_group)
                if re.search(pattern, lowered):
                    return {
                        "group": group,
                        "pattern": pattern,
                    }
        return None

    async def inspect_input(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """Flag biased generalizations in user input."""
        match = self._detect_bias(text)
        if match:
            return {
                "reason": "Potentially biased generalization detected in input",
                "group": match["group"],
                "pattern": match["pattern"],
                "guard": self.name,
            }
        return None

    async def inspect_output(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """Flag biased generalizations in model output."""
        match = self._detect_bias(text)
        if match:
            return {
                "reason": "Potentially biased generalization detected in output",
                "group": match["group"],
                "pattern": match["pattern"],
                "guard": self.name,
            }
        return None

