"""CLI for LambdaX."""

import asyncio
import logging
from pathlib import Path

import click

from lambdax.core.context import RequestContext
from lambdax.core.orchestrator import Orchestrator
from lambdax.core.policy import PolicyEngine
from lambdax.guards import PromptInjectionGuard, ToxicityGuard, PrivacyGuard
from lambdax.utils.logging import setup_logging

logger = logging.getLogger(__name__)


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
def cli(debug: bool):
    """LambdaX CLI - AI guardrails framework."""
    level = "DEBUG" if debug else "INFO"
    setup_logging(level=level, json_format=False)


@cli.command()
@click.option("--input", "-i", "text", required=True, help="Text to inspect")
@click.option(
    "--policy", "-p", default="default", help="Policy ID to use (default: default)"
)
@click.option(
    "--direction",
    "-d",
    type=click.Choice(["input", "output"]),
    default="input",
    help="Direction to inspect",
)
@click.option(
    "--policy-file", type=click.Path(exists=True), help="Path to policy YAML file"
)
def inspect(text: str, policy: str, direction: str, policy_file: str):
    """Inspect text through configured guards."""

    async def run_inspection():
        # Initialize policy engine
        policy_path = Path(policy_file) if policy_file else None
        policy_engine = PolicyEngine(policy_path)

        # Register guards
        from lambdax.guards import (
            InputSanitizerGuard,
            FormatValidatorGuard,
        )

        policy_engine.register_guard("prompt_injection", PromptInjectionGuard)
        policy_engine.register_guard("toxicity", ToxicityGuard)
        policy_engine.register_guard("privacy", PrivacyGuard)
        policy_engine.register_guard("input_sanitizer", InputSanitizerGuard)
        policy_engine.register_guard("format_validator", FormatValidatorGuard)

        # Initialize orchestrator
        orchestrator = Orchestrator(policy_engine)

        # Create context
        context = RequestContext()

        # Run inspection
        if direction == "input":
            result = await orchestrator.inspect_input(text, context, policy)
        else:
            result = await orchestrator.inspect_output(text, context, policy)

        # Display result
        if result:
            click.echo(click.style("❌ BLOCKED", fg="red", bold=True))
            click.echo(f"Reason: {result.get('reason')}")
            click.echo(f"Details: {result}")
        else:
            click.echo(click.style("✓ PASSED", fg="green", bold=True))

        return result

    asyncio.run(run_inspection())


@cli.command()
@click.option(
    "--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)"
)
@click.option("--port", default=8000, help="Port to bind to (default: 8000)")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def serve(host: str, port: int, reload: bool):
    """Start the LambdaX API server."""
    import uvicorn

    uvicorn.run(
        "lambdax.api.app:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    cli()
