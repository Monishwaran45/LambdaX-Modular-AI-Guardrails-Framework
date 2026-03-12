"""FastAPI application with production-ready features."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from lambdax.api.routes import router
from lambdax.core.orchestrator import Orchestrator
from lambdax.core.policy import PolicyEngine
from lambdax.utils.logging import setup_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info("Starting LambdaX API server")
    setup_logging(level="INFO", json_format=True)

    # Initialize policy engine
    policy_path = Path("policy.yaml")
    policy_engine = PolicyEngine(policy_path if policy_path.exists() else None)

    # Register guards
    from lambdax.guards import (
        PromptInjectionGuard,
        ToxicityGuard,
        PrivacyGuard,
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

    # Store in app state
    app.state.orchestrator = orchestrator
    app.state.policy_engine = policy_engine

    logger.info("LambdaX API server started successfully")

    yield

    # Shutdown
    logger.info("Shutting down LambdaX API server")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="LambdaX API",
        description="Production-ready AI guardrails framework",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routes
    app.include_router(router, prefix="/v1")

    # Prometheus metrics endpoint
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    # Health check
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


app = create_app()
