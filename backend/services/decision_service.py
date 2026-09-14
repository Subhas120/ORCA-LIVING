"""Authoritative M4 decision orchestration.

M4 is responsible for integration and transport orchestration only.

Ownership boundaries:
    M2 -> marine science, evidence and marine safety
    M1 -> candidate filtering, dominance, optimization and decision
    M3 -> frontend/GIS presentation
    M4 -> request normalization, orchestration and response adaptation

REST and voice use this same service so there is exactly one M4 decision path.
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
        return {
            "text": request.query,
            "vessel": request.vessel_type,
            "time": request.time,
        }

    @staticmethod
    def _marine_safety(safety_evals) -> tuple[str | None, list[str]]:
        """Read M2 safety metadata without recalculating marine safety."""
        statuses = {evaluation.status for evaluation in safety_evals}

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

    @staticmethod
    def _failure(
        status: StatusEnum,
        objective: dict[str, str | None],
        summary: str,
        *,
        safety_status: str | None = None,
        safety_reasons: list[str] | None = None,
    ) -> DecisionResponse:
        """Create a fail-closed response with no recommendation."""
        return DecisionResponse(
            status=status,
            objective=objective,
            decisionSummary=summary,
            marineSafetyStatus=safety_status,
            marineSafetyReasons=safety_reasons or [],
        )

    def run(self, request: DecisionRequest) -> DecisionResponse:
        """Run M4 -> M2 -> M1 -> M4 with fail-closed safety semantics."""
        objective = self._objective(request)

        try:
            world_state, proposals, safety_evals = (
                self.m2_adapter.get_marine_state_and_safety(request)
            )
        except InsufficientEvidenceError as exc:
            return self._failure(
                StatusEnum.INSUFFICIENT_EVIDENCE,
                objective,
                str(exc),
                safety_status="INSUFFICIENT_EVIDENCE",
                safety_reasons=[str(exc)],
            )
        except M2AdapterError as exc:
            return self._failure(
                StatusEnum.SERVICE_UNAVAILABLE,
                objective,
                str(exc),
            )
        except Exception as exc:
            # Unexpected M2 failure is also fail-closed.
            return self._failure(
                StatusEnum.SERVICE_UNAVAILABLE,
                objective,
                f"M2 integration failed: {exc}",
            )

        marine_safety_status, marine_safety_reasons = self._marine_safety(
            safety_evals
        )

        # Missing/invalid safety metadata must never be treated as SAFE.
        if marine_safety_status is None:
            return self._failure(
                StatusEnum.INSUFFICIENT_EVIDENCE,
                objective,
                "M2 did not provide a valid authoritative marine-safety status",
                safety_status="INSUFFICIENT_EVIDENCE",
                safety_reasons=[
                    "Authoritative marine-safety status is unavailable"
                ],
            )

        if marine_safety_status == "INSUFFICIENT_EVIDENCE":
            return self._failure(
                StatusEnum.INSUFFICIENT_EVIDENCE,
                objective,
                (
                    marine_safety_reasons[0]
                    if marine_safety_reasons
                    else "M2 reports insufficient evidence"
                ),
                safety_status=marine_safety_status,
                safety_reasons=marine_safety_reasons,
            )

        try:
            decision_intel = self.m1_service.run_decision_pipeline(
                world_state,
                proposals,
                safety_evals,
                request,
            )
        except Exception as exc:
            return self._failure(
                StatusEnum.SERVICE_UNAVAILABLE,
                objective,
                f"M1 pipeline failed: {exc}",
                safety_status=marine_safety_status,
                safety_reasons=marine_safety_reasons,
            )

        # M1 owns the decision. M4 only enforces the cross-layer safety
        # invariant: an M2 UNSAFE result can never expose a recommendation.
        if marine_safety_status == "UNSAFE":
            if decision_intel.recommended_candidate_id:
                return self._failure(
                    StatusEnum.SERVICE_UNAVAILABLE,
                    objective,
                    (
                        "M1 returned a recommendation despite an authoritative "
                        "M2 UNSAFE marine-safety result"
                    ),
                    safety_status="UNSAFE",
                    safety_reasons=marine_safety_reasons,
                )

            status = StatusEnum.NO_SAFE_CANDIDATES
        elif not decision_intel.recommended_candidate_id:
            status = StatusEnum.NO_SAFE_CANDIDATES
        else:
            status = StatusEnum.DECISION_AVAILABLE

        return ResponseAdapter.adapt(
            decision_intel,
            status,
            proposals,
            objective=objective,
            marine_safety_status=marine_safety_status,
            marine_safety_reasons=marine_safety_reasons,
        )


# Shared singleton used by REST and voice.
decision_service = DecisionService()
