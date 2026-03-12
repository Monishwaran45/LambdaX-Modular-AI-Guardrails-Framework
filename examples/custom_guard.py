"""Example of creating a custom guard."""

import asyncio
import re
from typing import Any, Dict, Optional

from lambdax.core.guard import Guard
from lambdax.core.context import RequestContext
from lambdax import Orchestrator, PolicyEngine


class ProfanityGuard(Guard):
    """Custom guard that detects profanity."""

    def _setup(self) -> None:
        """Initialize profanity word list."""
        # In production, load from a comprehensive list
        self.profanity_words = set(
            self.config.get("words", ["badword1", "badword2", "profanity"])
        )
        self.case_sensitive = self.config.get("case_sensitive", False)

    def _contains_profanity(self, text: str) -> Optional[str]:
        """Check if text contains profanity."""
        check_text = text if self.case_sensitive else text.lower()

        for word in self.profanity_words:
            check_word = word if self.case_sensitive else word.lower()
            # Use word boundaries to avoid false positives
            pattern = r"\b" + re.escape(check_word) + r"\b"
            if re.search(pattern, check_text):
                return word
        return None

    async def inspect_input(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """Check input for profanity."""
        found_word = self._contains_profanity(text)

        if found_word:
            return {
                "reason": "Profanity detected in input",
                "word": found_word,
                "guard": self.name,
            }
        return None

    async def inspect_output(
        self, text: str, context: RequestContext
    ) -> Optional[Dict[str, Any]]:
        """Check output for profanity."""
        found_word = self._contains_profanity(text)

        if found_word:
            return {
                "reason": "Profanity detected in output",
                "word": found_word,
                "guard": self.name,
            }
        return None


async def main():
    """Demonstrate custom guard usage."""
    # Initialize policy engine
    policy_engine = PolicyEngine()

    # Register custom guard
    policy_engine.register_guard("profanity", ProfanityGuard)

    # Create a simple policy programmatically
    from lambdax.core.policy import Policy, GuardConfig

    policy = Policy(
        id="custom",
        description="Policy with custom profanity guard",
        input_guards=[
            GuardConfig(
                name="profanity",
                config={"words": ["damn", "hell", "crap"], "case_sensitive": False},
            )
        ],
    )

    # Set policy
    from lambdax.core.policy import PolicyConfig

    policy_engine.config = PolicyConfig(version=1, policies=[policy])

    # Create orchestrator
    orchestrator = Orchestrator(policy_engine)

    # Test inputs
    test_cases = [
        "This is a clean message",
        "What the hell is going on?",
        "Damn, that's impressive!",
    ]

    print("=" * 60)
    print("Custom Profanity Guard Demo")
    print("=" * 60)

    for text in test_cases:
        print(f"\nInput: {text}")
        context = RequestContext()
        result = await orchestrator.inspect_input(text, context, policy_id="custom")

        if result:
            print(f"❌ BLOCKED - {result['reason']}")
            print(f"Found word: {result.get('word')}")
        else:
            print("✓ PASSED")


if __name__ == "__main__":
    asyncio.run(main())
