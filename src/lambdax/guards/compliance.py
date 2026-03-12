"""Compliance guard for policy- and domain-specific restrictions.

This guard provides a simple, configurable keyword/pattern based mechanism
for enforcing compliance requirements (e.g., blocking financial advice,
medical diagnosis, or other regulated content).

It is intentionally lightweight and explainable; organizations can plug in
more advanced detection logic by subclassing or replacing this guard.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from lambdax.core.context import RequestContext
from lambdax.core.guard import Guard

logger = logging.getLogger(__name__)


class ComplianceGuard(Guard):
    """Detects potential compliance violations based on configurable rules."""

    def _setup(self) -> None:
        # Simple keyword-based matcher grouped by domain
        self.blocked_categories: Dict[str, List[str]] = self.config.get(
            "blocked_categories",
            {
                "financial_advice": [
                    "buy this stock",
                    "guaranteed returns",
                    "insider trading",
                ],
                "medical_diagnosis": [
                    "this is a diagnosis",
                    "i diagnose you with",
                    "prescribe you",
                ],
                "legal_advice": [
                    "this is legal advice",
                    "i as your lawyer",
                    "circumvent the law",
                ],
            },
        )
        self.case_sensitive: bool = self.config.get("case_sensitive", False)
        logger.info(
            "ComplianceGuard initialized with %d categories",
            len(self.blocked_categories),
        )

    def _find_violation(self, text: str) -> Optional[Dict[str, Any]]:
        check_text = text if self.case_sensitive else text.lower()
        for category, patterns in self.blocked_categories.items():
            for pattern in patterns:
                check_pattern = pattern if self.case_sensitive else pattern.lower()
                if check_pattern in check_text:
                    return {"category": category, "pattern": pattern}
        return None

    async def inspect_input(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        violation = self._find_violation(text)
        if violation:
            return {
                "reason": "Potential compliance violation in input",
                "category": violation["category"],
                "pattern": violation["pattern"],
                "guard": self.name,
            }
        return None

    async def inspect_output(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        violation = self._find_violation(text)
        if violation:
            return {
                "reason": "Potential compliance violation in output",
                "category": violation["category"],
                "pattern": violation["pattern"],
                "guard": self.name,
            }
        return None

