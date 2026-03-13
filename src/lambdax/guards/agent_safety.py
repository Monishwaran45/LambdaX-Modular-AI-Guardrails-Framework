"""AI agent safety guard.

This guard is intended for agent-style systems where models can suggest tool
invocations or actions. It performs lightweight checks to detect obviously
dangerous or destructive commands embedded in text, such as:

- Irreversible filesystem operations (e.g., rm -rf /, format C:)
- Explicit instructions to exfiltrate secrets or credentials

It is intentionally conservative and explainable; teams can extend or tighten
the rule set according to their threat model.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from lambdax.core.context import RequestContext
from lambdax.core.guard import Guard

logger = logging.getLogger(__name__)


class AgentSafetyGuard(Guard):
    """Detects obviously dangerous agent/tool instructions."""

    def _setup(self) -> None:
        # Simple pattern lists — in production, extend/override via config
        self.blocked_commands: List[str] = self.config.get(
            "blocked_commands",
            [
                "rm -rf /",
                "format c:",
                "mkfs",
                "drop database",
                "shutdown -h now",
                "disable firewall",
            ],
        )
        self.block_secrets_exfil: bool = self.config.get(
            "block_secrets_exfil", True
        )
        logger.info(
            "AgentSafetyGuard initialized (blocked_commands=%d, block_secrets_exfil=%s)",
            len(self.blocked_commands),
            self.block_secrets_exfil,
        )

    def _find_dangerous_pattern(self, text: str) -> Optional[str]:
        lower = text.lower()
        for cmd in self.blocked_commands:
            if cmd.lower() in lower:
                return cmd

        if self.block_secrets_exfil:
            exfil_markers = [
                "exfiltrate secrets",
                "steal credentials",
                "send all environment variables",
                "upload all files from",
            ]
            for marker in exfil_markers:
                if marker in lower:
                    return marker

        return None

    async def inspect_input(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        pattern = self._find_dangerous_pattern(text)
        if pattern:
            return {
                "reason": "Potentially dangerous agent instruction in input",
                "pattern": pattern,
                "guard": self.name,
            }
        return None

    async def inspect_output(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        pattern = self._find_dangerous_pattern(text)
        if pattern:
            return {
                "reason": "Potentially dangerous agent instruction in output",
                "pattern": pattern,
                "guard": self.name,
            }
        return None

