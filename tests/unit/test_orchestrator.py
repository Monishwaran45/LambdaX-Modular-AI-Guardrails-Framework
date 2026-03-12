"""Unit tests for orchestrator."""

import pytest

from lambdax.core.context import RequestContext
from lambdax.core.orchestrator import Orchestrator
from lambdax.core.policy import PolicyEngine
from lambdax.guards import PrivacyGuard


@pytest.mark.asyncio
async def test_orchestrator_caching():
    """Test that orchestrator caches results."""
    policy_engine = PolicyEngine()
    policy_engine.register_guard("privacy", PrivacyGuard)

    orchestrator = Orchestrator(policy_engine, cache_ttl=60)

    # Mock a simple policy
    from lambdax.core.policy import Policy, GuardConfig

    policy = Policy(
        id="test",
        input_guards=[GuardConfig(name="privacy", config={"pii_types": ["EMAIL"]})],
    )
    policy_engine.config = type("Config", (), {"policies": [policy]})()

    context = RequestContext()
    text = "Contact user@example.com"

    # First call - should execute guard
    result1 = await orchestrator.inspect_input(text, context, policy_id="test")

    # Second call - should use cache
    result2 = await orchestrator.inspect_input(text, context, policy_id="test")

    assert result1 == result2
    assert result1 is not None


@pytest.mark.asyncio
async def test_orchestrator_no_guards():
    """Test orchestrator behavior with no guards configured."""
    policy_engine = PolicyEngine()
    orchestrator = Orchestrator(policy_engine)

    context = RequestContext()
    result = await orchestrator.inspect_input("test", context)

    assert result is None
