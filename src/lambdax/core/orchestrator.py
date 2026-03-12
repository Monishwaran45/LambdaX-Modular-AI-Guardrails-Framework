"""Main orchestration logic with concurrency and caching."""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

import cachetools

from lambdax.core.context import RequestContext
from lambdax.core.exceptions import TimeoutException
from lambdax.core.policy import PolicyEngine

logger = logging.getLogger(__name__)


class Orchestrator:
    """Orchestrates guard execution with concurrency, caching, and timeouts."""

    def __init__(
        self,
        policy_engine: PolicyEngine,
        cache_ttl: int = 300,
        cache_maxsize: int = 1000,
        timeout: float = 5.0,
    ):
        self.policy_engine = policy_engine
        self.cache: cachetools.TTLCache = cachetools.TTLCache(
            maxsize=cache_maxsize, ttl=cache_ttl
        )
        self.timeout = timeout

    def _get_cache_key(self, text: str, direction: str, policy_id: str) -> str:
        """Generate cache key for a request."""
        return f"{direction}:{policy_id}:{hash(text)}"

    async def inspect_input(
        self,
        text: str,
        context: RequestContext,
        policy_id: str = "default",
        use_cache: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Inspect input text through all configured guards.

        Args:
            text: Input text to inspect
            context: Request context
            policy_id: Policy to use
            use_cache: Whether to use caching

        Returns:
            Block result if any guard blocks, else None
        """
        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(text, "input", policy_id)
            if cache_key in self.cache:
                logger.debug(f"Cache hit for request {context.request_id}")
                return self.cache[cache_key]

        # Get guards from policy
        guards = self.policy_engine.get_input_guards(context, policy_id)
        if not guards:
            logger.warning(f"No input guards configured for policy {policy_id}")
            return None

        # Run guards concurrently with timeout
        start_time = time.time()
        tasks = [guard(text, context, direction="input") for guard in guards]

        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.timeout,
            )
        except asyncio.TimeoutError:
            logger.error(f"Guard execution timed out after {self.timeout}s")
            raise TimeoutException(f"Guard execution exceeded {self.timeout}s timeout")

        elapsed = time.time() - start_time
        logger.info(
            f"Executed {len(guards)} input guards in {elapsed:.3f}s for request {context.request_id}"
        )

        # Process results: first block wins
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Guard {guards[i].name} raised exception: {result}")
                continue

            if isinstance(result, dict):  # Block detected
                logger.warning(
                    f"Input blocked by {guards[i].name}: {result.get('reason')}"
                )
                if use_cache:
                    self.cache[cache_key] = result
                return result

        # No blocks
        if use_cache:
            self.cache[cache_key] = None
        return None

    async def inspect_output(
        self,
        text: str,
        context: RequestContext,
        policy_id: str = "default",
        use_cache: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Inspect output text through all configured guards.

        Args:
            text: Output text to inspect
            context: Request context
            policy_id: Policy to use
            use_cache: Whether to use caching

        Returns:
            Block result if any guard blocks, else None
        """
        # Check cache
        if use_cache:
            cache_key = self._get_cache_key(text, "output", policy_id)
            if cache_key in self.cache:
                logger.debug(f"Cache hit for request {context.request_id}")
                return self.cache[cache_key]

        # Get guards from policy
        guards = self.policy_engine.get_output_guards(context, policy_id)
        if not guards:
            logger.warning(f"No output guards configured for policy {policy_id}")
            return None

        # Run guards concurrently with timeout
        start_time = time.time()
        tasks = [guard(text, context, direction="output") for guard in guards]

        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.timeout,
            )
        except asyncio.TimeoutError:
            logger.error(f"Guard execution timed out after {self.timeout}s")
            raise TimeoutException(f"Guard execution exceeded {self.timeout}s timeout")

        elapsed = time.time() - start_time
        logger.info(
            f"Executed {len(guards)} output guards in {elapsed:.3f}s for request {context.request_id}"
        )

        # Process results: first block wins
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Guard {guards[i].name} raised exception: {result}")
                continue

            if isinstance(result, dict):  # Block detected
                logger.warning(
                    f"Output blocked by {guards[i].name}: {result.get('reason')}"
                )
                if use_cache:
                    self.cache[cache_key] = result
                return result

        # No blocks
        if use_cache:
            self.cache[cache_key] = None
        return None

    def clear_cache(self) -> None:
        """Clear the cache."""
        self.cache.clear()
        logger.info("Cache cleared")
