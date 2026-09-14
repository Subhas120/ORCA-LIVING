"""M4 Backend API Router.

M4 owns API orchestration and transport semantics.

Safety authority:
    M2 -> marine science and marine safety

Decision authority:
    M1 -> candidate filtering, dominance, optimization and decision

M4:
    - transports M2 safety state
    - invokes M1
    - maps the authoritative upstream state to the API contract
    - never converts insufficient evidence into SAFE
    - never overrides UNSAFE
"""

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


@router.post(
    "/decision",
    response_model=DecisionResponse,
)
async def get_decision(request: DecisionRequest):
    try:

        # ---------------------------------------------------------
        # 1. M2 Adapter
        # ---------------------------------------------------------
        try:
            (
                world_state,
                proposals,
                safety_evals,
            ) = m2_adapter.get_marine_state_and_safety(
                request
            )

        except InsufficientEvidenceError as exc:
            return DecisionResponse(
                status=StatusEnum.INSUFFICIENT_EVIDENCE,
                objective={
                    "text": request.query,
                    "vessel": request.vessel_type,
                    "time": request.time,
                },
                decisionSummary=str(exc),
                marineSafetyStatus="INSUFFICIENT_EVIDENCE",
                marineSafetyReasons=[str(exc)],
            )

        except M2AdapterError as exc:
            return DecisionResponse(
                status=StatusEnum.SERVICE_UNAVAILABLE,
                objective={
                    "text": request.query,
                    "vessel": request.vessel_type,
                    "time": request.time,
                },
                decisionSummary=str(exc),
            )

        # ---------------------------------------------------------
        # 2. Extract M2-authoritative safety state
        #
        # M4 transports this result.
        # M4 does NOT recalculate marine safety.
        # ---------------------------------------------------------
        marine_safety_status = None
        marine_safety_reasons: list[str] = []

        if safety_evals:

            statuses = {
                evaluation.status
                for evaluation in safety_evals
            }

            if "UNSAFE" in statuses:
                marine_safety_status = "UNSAFE"

            elif "INSUFFICIENT_EVIDENCE" in statuses:
                marine_safety_status = (
                    "INSUFFICIENT_EVIDENCE"
                )

            elif statuses == {"SAFE"}:
                marine_safety_status = "SAFE"

            marine_safety_reasons = list(
                dict.fromkeys(
                    evaluation.reason
                    for evaluation in safety_evals
                    if evaluation.reason
                )
            )

        # ---------------------------------------------------------
        # 3. M1 Decision Intelligence Pipeline
        # ---------------------------------------------------------
        try:
            decision_intel = (
                m1_service.run_decision_pipeline(
                    world_state,
                    proposals,
                    safety_evals,
                    request,
                )
            )

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=(
                    "M1 pipeline failed: "
                    f"{exc}"
                ),
            )

        # ---------------------------------------------------------
        # 4. Determine API status
        #
        # IMPORTANT:
        # M2 safety status has precedence over the generic
        # "no recommendation" result.
        #
        # This prevents:
        #
        #   INSUFFICIENT_EVIDENCE
        #       ->
        #   NO_SAFE_CANDIDATES
        #
        # when the actual upstream condition is lack of evidence.
        # ---------------------------------------------------------
        if (
            marine_safety_status
            == "INSUFFICIENT_EVIDENCE"
        ):
            status = StatusEnum.INSUFFICIENT_EVIDENCE

        elif (
            marine_safety_status == "UNSAFE"
            and not decision_intel.recommended_candidate_id
        ):
            status = StatusEnum.NO_SAFE_CANDIDATES

        elif not decision_intel.recommended_candidate_id:
            status = StatusEnum.NO_SAFE_CANDIDATES

        else:
            status = StatusEnum.DECISION_AVAILABLE

        # ---------------------------------------------------------
        # 5. Build objective representation
        #
        # This is transport information from the original request.
        # M4 does not reinterpret the user's objective here.
        # ---------------------------------------------------------
        objective = {
            "text": request.query,
            "vessel": request.vessel_type,
            "time": request.time,
        }

        # ---------------------------------------------------------
        # 6. M4 Response Adapter
        # ---------------------------------------------------------
        return ResponseAdapter.adapt(
            decision_intel,
            status,
            proposals,
            objective=objective,
            marine_safety_status=marine_safety_status,
            marine_safety_reasons=marine_safety_reasons,
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )