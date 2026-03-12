"""Audit logging for transparency and compliance."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from lambdax.core.context import RequestContext

logger = logging.getLogger(__name__)


class AuditLogger:
    """Records all AI interactions for transparency and compliance."""

    def __init__(self, log_path: Optional[Path] = None, enabled: bool = True):
        self.enabled = enabled
        self.log_path = log_path or Path("audit.log")
        self.logger = logging.getLogger("lambdax.audit")

        if enabled and log_path:
            # Create file handler for audit logs
            handler = logging.FileHandler(self.log_path)
            handler.setFormatter(
                logging.Formatter("%(asctime)s - %(message)s")
            )
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log_request(
        self,
        context: RequestContext,
        text: str,
        direction: str,
        policy_id: str,
    ) -> None:
        """Log incoming request."""
        if not self.enabled:
            return

        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "request",
            "request_id": context.request_id,
            "user_id": context.user_id,
            "direction": direction,
            "policy_id": policy_id,
            "text_length": len(text),
            "metadata": context.metadata,
        }

        self.logger.info(json.dumps(record))

    def log_guard_result(
        self,
        context: RequestContext,
        guard_name: str,
        result: Optional[Dict[str, Any]],
        duration: float,
    ) -> None:
        """Log guard execution result."""
        if not self.enabled:
            return

        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "guard_execution",
            "request_id": context.request_id,
            "guard_name": guard_name,
            "blocked": result is not None,
            "reason": result.get("reason") if result else None,
            "duration_ms": round(duration * 1000, 2),
        }

        self.logger.info(json.dumps(record))

    def log_response(
        self,
        context: RequestContext,
        blocked: bool,
        reason: Optional[str],
        total_duration: float,
    ) -> None:
        """Log final response."""
        if not self.enabled:
            return

        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": "response",
            "request_id": context.request_id,
            "blocked": blocked,
            "reason": reason,
            "total_duration_ms": round(total_duration * 1000, 2),
            "guards_executed": len(context.guard_results),
        }

        self.logger.info(json.dumps(record))
