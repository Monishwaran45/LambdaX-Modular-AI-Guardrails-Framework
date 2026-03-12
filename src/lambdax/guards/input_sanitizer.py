"""Input sanitizer to remove malicious tokens and hidden instructions."""

import logging
import re
from typing import Any, Dict, Optional

from lambdax.core.context import RequestContext
from lambdax.core.guard import Guard

logger = logging.getLogger(__name__)


class InputSanitizerGuard(Guard):
    """Removes malicious tokens, hidden instructions, and control characters."""

    def _setup(self) -> None:
        """Initialize sanitization patterns."""
        self.remove_control_chars = self.config.get("remove_control_chars", True)
        self.remove_unicode_tricks = self.config.get("remove_unicode_tricks", True)
        self.block_system_prompts = self.config.get("block_system_prompts", True)

        # Patterns for system prompt attempts
        self.system_patterns = [
            r"ignore\s+(previous|all|above)\s+instructions?",
            r"disregard\s+(previous|all|above)\s+instructions?",
            r"forget\s+(previous|all|above)\s+instructions?",
            r"system\s*:\s*",
            r"<\|im_start\|>",
            r"<\|im_end\|>",
        ]

    def _sanitize_text(self, text: str) -> tuple[str, list[str]]:
        """Sanitize text and return cleaned version with list of issues found."""
        issues = []
        cleaned = text

        # Remove control characters
        if self.remove_control_chars:
            control_chars = re.findall(r"[\x00-\x1f\x7f-\x9f]", cleaned)
            if control_chars:
                issues.append(f"Removed {len(control_chars)} control characters")
                cleaned = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", cleaned)

        # Remove zero-width characters and other Unicode tricks
        if self.remove_unicode_tricks:
            zero_width = ["\u200b", "\u200c", "\u200d", "\ufeff"]
            for char in zero_width:
                if char in cleaned:
                    issues.append("Removed zero-width characters")
                    cleaned = cleaned.replace(char, "")

        # Check for system prompt injection attempts
        if self.block_system_prompts:
            for pattern in self.system_patterns:
                if re.search(pattern, cleaned, re.IGNORECASE):
                    issues.append(f"Detected system prompt pattern: {pattern}")

        return cleaned, issues

    async def inspect_input(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """Sanitize and check input text."""
        cleaned, issues = self._sanitize_text(text)

        if issues:
            # Store cleaned text in context for downstream use
            context.metadata["sanitized_input"] = cleaned
            context.metadata["sanitization_issues"] = issues

            # Block if system prompt patterns detected
            if any("system prompt" in issue.lower() for issue in issues):
                return {
                    "reason": "Input contains system prompt injection attempt",
                    "issues": issues,
                    "guard": self.name,
                }

            # Otherwise just log and pass (text is sanitized)
            logger.info(f"Sanitized input: {issues}")

        return None

    async def inspect_output(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """Output sanitization not typically needed."""
        return None
