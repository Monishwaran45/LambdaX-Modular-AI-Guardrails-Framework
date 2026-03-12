"""Privacy guard for PII detection."""

import logging
import re
from typing import Any, Dict, List, Optional

from lambdax.core.context import RequestContext
from lambdax.core.guard import Guard

logger = logging.getLogger(__name__)


class PrivacyGuard(Guard):
    """Detects personally identifiable information (PII)."""

    # Simple regex patterns for common PII types
    PATTERNS = {
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "PHONE": r"\b(?:\+?1[-.]?)?\(?([0-9]{3})\)?[-.]?([0-9]{3})[-.]?([0-9]{4})\b",
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "CREDIT_CARD": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
        "IP_ADDRESS": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    }

    def _setup(self) -> None:
        """Initialize PII patterns."""
        self.pii_types = self.config.get("pii_types", list(self.PATTERNS.keys()))
        self.compiled_patterns = {
            pii_type: re.compile(self.PATTERNS[pii_type])
            for pii_type in self.pii_types
            if pii_type in self.PATTERNS
        }
        logger.info(f"PrivacyGuard initialized for types: {self.pii_types}")

    def _detect_pii(self, text: str) -> List[Dict[str, Any]]:
        """Detect PII in text."""
        findings = []

        for pii_type, pattern in self.compiled_patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                findings.append(
                    {
                        "type": pii_type,
                        "value": match.group(),
                        "start": match.start(),
                        "end": match.end(),
                    }
                )

        return findings

    async def inspect_input(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """Check input for PII."""
        findings = self._detect_pii(text)

        if findings:
            return {
                "reason": f"PII detected in input: {', '.join(set(f['type'] for f in findings))}",
                "findings": findings,
                "count": len(findings),
                "guard": self.name,
            }
        return None

    async def inspect_output(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """Check output for PII."""
        findings = self._detect_pii(text)

        if findings:
            return {
                "reason": f"PII detected in output: {', '.join(set(f['type'] for f in findings))}",
                "findings": findings,
                "count": len(findings),
                "guard": self.name,
            }
        return None
