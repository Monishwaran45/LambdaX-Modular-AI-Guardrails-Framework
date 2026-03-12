"""Unit tests for format validator guard."""

import pytest

from lambdax.core.context import RequestContext
from lambdax.guards import FormatValidatorGuard


@pytest.mark.asyncio
async def test_format_validator_valid_json():
    """Test that validator passes valid JSON."""
    guard = FormatValidatorGuard(config={"format": "json"})
    context = RequestContext()

    text = '{"name": "John", "age": 30}'
    result = await guard.inspect_output(text, context)

    assert result is None


@pytest.mark.asyncio
async def test_format_validator_invalid_json():
    """Test that validator blocks invalid JSON."""
    guard = FormatValidatorGuard(config={"format": "json"})
    context = RequestContext()

    text = '{name: "John", age: 30}'  # Invalid JSON (no quotes on keys)
    result = await guard.inspect_output(text, context)

    assert result is not None
    assert "Invalid JSON" in result["reason"]


@pytest.mark.asyncio
async def test_format_validator_with_schema():
    """Test validator with required fields."""
    guard = FormatValidatorGuard(
        config={"format": "json", "schema": {"required": ["name", "age"]}}
    )
    context = RequestContext()

    # Missing required field
    text = '{"name": "John"}'
    result = await guard.inspect_output(text, context)

    assert result is not None
    assert "Missing required field" in result["reason"]

    # All required fields present
    text = '{"name": "John", "age": 30}'
    result = await guard.inspect_output(text, context)

    assert result is None
