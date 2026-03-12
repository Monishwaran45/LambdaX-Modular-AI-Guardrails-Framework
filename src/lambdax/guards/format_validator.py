"""Format validator for structured outputs."""

import json
import logging
from typing import Any, Dict, Optional

from lambdax.core.context import RequestContext
from lambdax.core.guard import Guard

logger = logging.getLogger(__name__)


class FormatValidatorGuard(Guard):
    """Validates structured outputs like JSON against schemas."""

    def _setup(self) -> None:
        """Initialize validator configuration."""
        self.expected_format = self.config.get("format", "json")
        self.schema = self.config.get("schema", None)
        self.strict = self.config.get("strict", True)

    def _validate_json(self, text: str) -> tuple[bool, Optional[str]]:
        """Validate JSON format."""
        try:
            data = json.loads(text)

            # If schema provided, validate against it
            if self.schema:
                # Basic schema validation (can be extended with jsonschema library)
                for key in self.schema.get("required", []):
                    if key not in data:
                        return False, f"Missing required field: {key}"

            return True, None

        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"

    async def inspect_input(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """Input validation not typically needed for format."""
        return None

    async def inspect_output(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """Validate output format."""
        if self.expected_format == "json":
            valid, error = self._validate_json(text)

            if not valid:
                return {
                    "reason": f"Output format validation failed: {error}",
                    "expected_format": self.expected_format,
                    "guard": self.name,
                }

        return None
