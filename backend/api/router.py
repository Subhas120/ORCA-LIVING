"""M4 REST API router.

The router is intentionally thin. All decision orchestration lives in
backend.services.decision_service so REST and voice use the exact same
M2 -> M1 -> M4 path and safety semantics.
"""

from fastapi import APIRouter, HTTPException

from backend.models.request import DecisionRequest
from backend.models.response import DecisionResponse
from backend.services.decision_service import decision_service


router = APIRouter()


@router.post(
    "/decision",
    response_model=DecisionResponse,
)
async def get_decision(request: DecisionRequest) -> DecisionResponse:
    """Execute the authoritative M4 decision flow."""
    try:
        return decision_service.run(request)
    except Exception as exc:
        # The decision service already maps expected upstream failures.
        # This final boundary protects the API from leaking an invented
        # fallback recommendation.
        raise HTTPException(
            status_code=500,
            detail=f"M4 decision orchestration failed: {exc}",
        ) from exc
