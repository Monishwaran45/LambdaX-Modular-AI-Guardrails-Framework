"""API routes for LambdaX."""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from lambdax.core.context import RequestContext

logger = logging.getLogger(__name__)

router = APIRouter()


class InspectRequest(BaseModel):
    """Request model for inspection endpoint."""

    text: str = Field(..., description="Text to inspect")
    direction: str = Field("input", description="Direction: input or output")
    policy_id: str = Field("default", description="Policy ID to use")
    user_id: Optional[str] = Field(None, description="User ID for context")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class InspectResponse(BaseModel):
    """Response model for inspection endpoint."""

    blocked: bool
    reason: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    request_id: str


@router.post("/inspect", response_model=InspectResponse)
async def inspect_text(request_data: InspectRequest, request: Request):
    """
    Inspect text through configured guards.

    Args:
        request_data: Inspection request
        request: FastAPI request object

    Returns:
        Inspection result
    """
    orchestrator = request.app.state.orchestrator

    # Create context
    context = RequestContext(
        user_id=request_data.user_id,
        metadata=request_data.metadata or {},
    )

    try:
        # Run inspection
        if request_data.direction == "input":
            result = await orchestrator.inspect_input(
                request_data.text, context, request_data.policy_id
            )
        elif request_data.direction == "output":
            result = await orchestrator.inspect_output(
                request_data.text, context, request_data.policy_id
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid direction: {request_data.direction}. Must be 'input' or 'output'",
            )

        # Build response
        if result:
            return InspectResponse(
                blocked=True,
                reason=result.get("reason"),
                details=result,
                request_id=context.request_id,
            )
        else:
            return InspectResponse(
                blocked=False,
                request_id=context.request_id,
            )

    except Exception as e:
        logger.exception(f"Error during inspection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-cache")
async def clear_cache(request: Request):
    """Clear the orchestrator cache."""
    orchestrator = request.app.state.orchestrator
    orchestrator.clear_cache()
    return {"status": "cache cleared"}
