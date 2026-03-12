"""Request context management."""

from typing import Any, Dict, Optional
from uuid import uuid4


class RequestContext:
    """Context object passed through guard pipeline."""

    def __init__(
        self,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.request_id = request_id or str(uuid4())
        self.user_id = user_id
        self.metadata = metadata or {}
        self.guard_results: Dict[str, Any] = {}

    def add_guard_result(self, guard_name: str, result: Any) -> None:
        """Store result from a guard execution."""
        self.guard_results[guard_name] = result

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "request_id": self.request_id,
            "user_id": self.user_id,
            "metadata": self.metadata,
            "guard_results": self.guard_results,
        }
