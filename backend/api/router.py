"""M4 Backend API Router."""

from fastapi import APIRouter, HTTPException

from backend.models.request import DecisionRequest
from backend.models.response import DecisionResponse, StatusEnum
from backend.services.m2_adapter import (
    M2Adapter,
    M2AdapterError,
    InsufficientEvidenceError,
)
from backend.services.m1_service import M1Service
from backend.services.response_adapter import ResponseAdapter


router = APIRouter()

m1_service = M1Service()
m2_adapter = M2Adapter()


@router.post("/decision", response_model=DecisionResponse)
async def get_decision(request: DecisionRequest):
    try:
        # ---------------------------------------------------------
        # 1. M2 Adapter
        # ---------------------------------------------------------
        try:
            world_state, proposals, safety_evals = (
                m2_adapter.get_marine_state_and_safety(request)
            )

        except InsufficientEvidenceError as e:
            return DecisionResponse(
                status=StatusEnum.INSUFFICIENT_EVIDENCE,
                decisionSummary=str(e),
            )

        except M2AdapterError as e:
            return DecisionResponse(
                status=StatusEnum.SERVICE_UNAVAILABLE,
                decisionSummary=str(e),
            )

        # ---------------------------------------------------------
        # 2. M1 Decision Intelligence Pipeline
        # ---------------------------------------------------------
        try:
            decision_intel = m1_service.run_decision_pipeline(
                world_state,
                proposals,
                safety_evals,
                request,
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"M1 pipeline failed: {str(e)}",
            )

        # ---------------------------------------------------------
        # 3. Determine API status
        # ---------------------------------------------------------
        if not decision_intel.recommended_candidate_id:
            status = StatusEnum.NO_SAFE_CANDIDATES
        else:
            status = StatusEnum.DECISION_AVAILABLE

        # ---------------------------------------------------------
        # 4. M4 Response Adapter
        #
        # Pass the original proposals so the response adapter can
        # attach the actual candidate details to the M1 recommendation.
        # ---------------------------------------------------------
        return ResponseAdapter.adapt(
            decision_intel,
            status,
            proposals,
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )