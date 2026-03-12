"""Base guard interface with production-ready error handling."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from lambdax.core.context import RequestContext
from lambdax.core.exceptions import GuardException

logger = logging.getLogger(__name__)


class Guard(ABC):
    """Base class for all guards with built-in error handling."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
        self._setup()

    def _setup(self) -> None:
        """Override for one-time initialization (e.g., load model)."""
        pass

    @abstractmethod
    async def inspect_input(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """
        Inspect input text.

        Returns:
            Dict with 'reason' and optional metadata if blocked, else None.
        """
        pass

    @abstractmethod
    async def inspect_output(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """
        Inspect output text.

        Returns:
            Dict with 'reason' and optional metadata if blocked, else None.
        """
        pass

    async def __call__(
        self, text: str, context: RequestContext, direction: str = "input"
    ) -> Optional[Dict[str, Any]]:
        """
        Unified entry point with error catching.

        Args:
            text: Text to inspect
            context: Request context
            direction: Either 'input' or 'output'

        Returns:
            Block result or None
        """
        try:
            if direction == "input":
                result = await self.inspect_input(text, context)
            else:
                result = await self.inspect_output(text, context)

            # Store result in context
            context.add_guard_result(self.name, result)
            return result

        except Exception as e:
            logger.exception(f"Guard {self.name} failed: {e}")

            # Depending on policy, either raise (fail-closed) or return None (fail-open)
            if self.config.get("fail_open", False):
                logger.warning(f"Guard {self.name} failed open, allowing request")
                return None
            raise GuardException(f"Guard {self.name} failed: {e}") from e
