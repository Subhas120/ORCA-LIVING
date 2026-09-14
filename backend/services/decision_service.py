"""Authoritative M4 decision orchestration.

M4 is responsible for integration and transport orchestration only.

Ownership boundaries:
    M2 -> marine science, evidence and marine safety
    M1 -> candidate filtering, dominance, optimization and decision
    M3 -> frontend/GIS presentation
    M4 -> request normalization, orchestration and response adaptation

Both REST and voice MUST use this service so that there is exactly one
M4 decision path and both interfaces receive identical decision semantics.
"""

from __future__ import annotations

from backend.models.request import DecisionRequest
from backend.models.response import DecisionResponse, StatusEnum
from backend.services.m1_service import M1Service
from backend.services.m2_adapter import (
    InsufficientEvidenceError,
    M2Adapter,
    M2AdapterError,
)
from backend.services.response_adapter import ResponseAdapter


class DecisionService:
    """Single authoritative M4 orchestration boundary for decisions."""

    def __init__(
        self,
        *,
        m1_service: M1Service | None = None,
        m2_adapter: M2Adapter | None = None,
    ) -> None:
        self.m1_service = m1_service or M1Service()
        self.m2_adapter = m2_adapter or M2Adapter()

    @staticmethod
    def _objective(request: DecisionRequest) -> dict[str, str | None]:
        """Build the transport-level representation of the user request."""
        return {
            "text": request.query,
            "vessel": request.vessel_type,
            "time": request.time,
        }

    @staticmethod
    def _marine_safety(
        safety_evals,
    ) -> tuple[str | None, list[str]]:
        """Extract M2 safety metadata without recalculating safety."""
        statuses = {
            evaluation.status
            for evaluation in safety_evals
        }

        if "UNSAFE" in statuses:
            status = "UNSAFE"
        elif "INSUFFICIENT_EVIDENCE" in statuses:
            status = "INSUFFICIENT_EVIDENCE"
        elif statuses == {"SAFE"}:
            status = "SAFE"
        else:
            status = None

        reasons = list(
            dict.fromkeys(
                evaluation.reason
                for evaluation in safety_evals
                if evaluation.reason
            )
        )
        return status, reasons

    def run(self, request: DecisionRequest) -> DecisionResponse:
        """Run the complete M4 -> M2 -> M1 -> M4 decision flow.

        Failure behavior is fail-closed: an upstream failure never creates
        a recommendation. M2 safety remains authoritative throughout.
        """
        objective = self._objective(request)

        # -------------------------------------------------------------
        # 1. M2: marine state + authoritative marine safety
        # -------------------------------------------------------------
        try:
            world_state, proposals, safety_evals = (
                self.m2_adapter.get_marine_state_and_safety(request)
            )
        except InsufficientEvidenceError as exc:
            return DecisionResponse(
                status=StatusEnum.INSUFFICIENT_EVIDENCE,
                objective=objective,
                decisionSummary=str(exc),
                marineSafetyStatus="INSUFFICIENT_EVIDENCE",
                marineSafetyReasons=[str(exc)],
            )
        except M2AdapterError as exc:
            return DecisionResponse(
                status=StatusEnum.SERVICE_UNAVAILABLE,
                objective=objective,
                decisionSummary=str(exc),
            )

        marine_safety_status, marine_safety_reasons = (
            self._marine_safety(safety_evals)
        )

        # M2 itself reports insufficient evidence through safety metadata.
        # Do not send that state through a normal decision path where it could
        # be misrepresented as a safe recommendation.
        if marine_safety_status == "INSUFFICIENT_EVIDENCE":
            return DecisionResponse(
                status=StatusEnum.INSUFFICIENT_EVIDENCE,
                objective=objective,
                decisionSummary=(
                    marine_safety_reasons[0]
                    if marine_safety_reasons
                    else "M2 reports insufficient evidence"
                ),
                marineSafetyStatus=marine_safety_status,
                marineSafetyReasons=marine_safety_reasons,
            )

        # -------------------------------------------------------------
        # 2. M1: authoritative decision intelligence
        # -------------------------------------------------------------
        try:
            decision_intel = self.m1_service.run_decision_pipeline(
                world_state,
                proposals,
                safety_evals,
                request,
            )
        except Exception as exc:
            # Fail closed. REST and voice intentionally share this behavior.
            return DecisionResponse(
                status=StatusEnum.SERVICE_UNAVAILABLE,
                objective=objective,
                decisionSummary=f"M1 pipeline failed: {exc}",
                marineSafetyStatus=marine_safety_status,
                marineSafetyReasons=marine_safety_reasons,
            )

        # -------------------------------------------------------------
        # 3. Safety contract invariant
        # -------------------------------------------------------------
        # M1 owns safety filtering/decision logic. If it nevertheless returns
        # a recommendation while M2 says the marine state is UNSAFE, M4 must
        # fail closed rather than expose that candidate to M3 or voice.
        if (
            marine_safety_status == "UNSAFE"
            and decision_intel.recommended_candidate_id
        ):
            return DecisionResponse(
                status=StatusEnum.SERVICE_UNAVAILABLE,
                objective=objective,
                decisionSummary=(
                    "M1 returned a recommendation despite an authoritative "
                    "M2 UNSAFE marine-safety result"
                ),
                marineSafetyStatus="UNSAFE",
                marineSafetyReasons=marine_safety_reasons,
            )

        # -------------------------------------------------------------
        # 4. Public status mapping
        # -------------------------------------------------------------
        if marine_safety_status == "UNSAFE":
            status = StatusEnum.NO_SAFE_CANDIDATES
        elif not decision_intel.recommended_candidate_id:
            status = StatusEnum.NO_SAFE_CANDIDATES
        else:
            status = StatusEnum.DECISION_AVAILABLE

        # -------------------------------------------------------------
        # 5. M4: structural response adaptation only
        # -------------------------------------------------------------
        return ResponseAdapter.adapt(
            decision_intel,
            status,
            proposals,
            objective=objective,
            marine_safety_status=marine_safety_status,
            marine_safety_reasons=marine_safety_reasons,
        )


# One process-wide service keeps REST and voice on the same orchestration
# implementation while remaining easy to replace in tests.
decision_service = DecisionService()
