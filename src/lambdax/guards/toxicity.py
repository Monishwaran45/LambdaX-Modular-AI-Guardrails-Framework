"""Toxicity detection guard."""

import asyncio
import logging
from typing import Any, Dict, Optional

from lambdax.core.context import RequestContext
from lambdax.core.guard import Guard

logger = logging.getLogger(__name__)


class ToxicityGuard(Guard):
    """Detects toxic content in text."""

    def _setup(self) -> None:
        """Initialize the model."""
        self.threshold = self.config.get("threshold", 0.7)
        self.model_name = self.config.get("model", "unitary/toxic-bert")
        self._model = None
        logger.info(f"ToxicityGuard initialized with threshold {self.threshold}")

    async def _load_model(self) -> None:
        """Lazy load the model in background."""
        if self._model is not None:
            return

        try:
            from transformers import pipeline

            loop = asyncio.get_event_loop()
            self._model = await loop.run_in_executor(
                None, pipeline, "text-classification", self.model_name
            )
            logger.info(f"Loaded model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            raise

    async def _predict(self, text: str) -> float:
        """Run prediction on text."""
        if self._model is None:
            await self._load_model()

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self._model, text)

        # Extract toxicity score
        for item in result:
            if item.get("label") in ["toxic", "LABEL_1"]:
                return item["score"]
        return 0.0

    async def inspect_input(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """Check input for toxicity."""
        score = await self._predict(text)

        if score >= self.threshold:
            return {
                "reason": "Toxic content detected in input",
                "score": score,
                "threshold": self.threshold,
                "guard": self.name,
            }
        return None

    async def inspect_output(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """Check output for toxicity."""
        score = await self._predict(text)

        if score >= self.threshold:
            return {
                "reason": "Toxic content detected in output",
                "score": score,
                "threshold": self.threshold,
                "guard": self.name,
            }
        return None
