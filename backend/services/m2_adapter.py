"""M4 Adapter for M2 Marine Agent.

M4 performs structural contract adaptation only.
Scientific marine safety remains authoritative from M2.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
import uuid

from agents.common.agent_contract import AgentRequest
from agents.ocean.ocean_agent import handle_ocean

from orca_living.engines.candidate_generator import CandidateProposal
from orca_living.models.marine_world_state import (
    MarineWorldState,
    StateRegion,
    OceanState,
    WeatherState,
    HazardState,
    GeospatialState,
    EcologicalState,
    VesselState,
    DecisionState,
)
from orca_living.models.safety import SafetyEvaluation

from backend.models.request import DecisionRequest


class M2AdapterError(Exception):
    """Raised when M2 cannot provide a usable response."""


class InsufficientEvidenceError(Exception):
    """Raised when M2 lacks decision-critical evidence."""


class M2Adapter:
    """Adapt the M2 marine-agent response to M1 contracts."""

    @staticmethod
    def get_marine_state_and_safety(
        request: DecisionRequest,
    ) -> tuple[
        MarineWorldState,
        tuple[CandidateProposal, ...],
        tuple[SafetyEvaluation, ...],
    ]:

        # ---------------------------------------------------------
        # 1. Build M2 request
        # ---------------------------------------------------------
        m2_request = AgentRequest(
            query=request.query,
            location=request.location,
            destination=None,
            date=request.date,
            time=request.time,
            activity=request.activity,
        )

        # ---------------------------------------------------------
        # 2. Call M2
        # ---------------------------------------------------------
        m2_response = handle_ocean(m2_request)

        if m2_response.status in {"unavailable", "error"}:
            raise M2AdapterError(
                m2_response.error or "M2 service unavailable"
            )

        data: dict[str, Any] = m2_response.data or {}

        if not data:
            raise InsufficientEvidenceError(
                "M2 returned no data"
            )

        # ---------------------------------------------------------
        # 3. Read M2-authoritative marine safety
        # ---------------------------------------------------------
        marine_safety = data.get("marine_safety")

        if not isinstance(marine_safety, dict):
            raise InsufficientEvidenceError(
                "M2 response does not contain marine_safety"
            )

        safety_status = marine_safety.get("status")

        if safety_status not in {
            "SAFE",
            "UNSAFE",
            "INSUFFICIENT_EVIDENCE",
        }:
            raise InsufficientEvidenceError(
                "M2 returned an invalid marine safety status"
            )

        hazards = tuple(
            marine_safety.get("hazards") or ()
        )

        reasons = tuple(
            marine_safety.get("reasons") or ()
        )

        # ---------------------------------------------------------
        # 4. Build evidence references
        # ---------------------------------------------------------
        evidence_data = data.get("evidence") or {}

        evidence_refs = tuple(
            f"m2:{parameter}"
            for parameter in evidence_data
        )

        # ---------------------------------------------------------
        # 5. Adapt M2 PFZ recommendations into M1 proposals
        # ---------------------------------------------------------
        pfz = data.get("pfz") or []

        proposals: list[CandidateProposal] = []

        for index, candidate in enumerate(pfz):

            if not isinstance(candidate, dict):
                continue

            candidate_id = str(
                candidate.get("pfz_id")
                or f"m2-pfz-{index + 1}"
            )

            latitude = candidate.get("latitude")
            longitude = candidate.get("longitude")

            if latitude is None or longitude is None:
                continue

            distance = candidate.get("distance_km")
            confidence = candidate.get("confidence")

            # -----------------------------------------------------
            # M2 confidence is already normalized between 0 and 1.
            # M1 expected_opportunity requires the same range.
            # -----------------------------------------------------
            if confidence is None:
                opportunity = 0.0
            else:
                try:
                    opportunity = float(confidence)
                except (TypeError, ValueError):
                    opportunity = 0.0

            opportunity = max(
                0.0,
                min(1.0, opportunity),
            )

            # Confidence -> uncertainty for M1 objective handling.
            uncertainty = 1.0 - opportunity

            distance_value = (
                float(distance)
                if distance is not None
                else 0.0
            )

            proposals.append(
                CandidateProposal(
                    id=candidate_id,
                    action_type=request.activity,
                    latitude=float(latitude),
                    longitude=float(longitude),
                    name=candidate_id,
                    expected_opportunity=opportunity,
                    distance=(
                        float(distance)
                        if distance is not None
                        else None
                    ),
                    objective_values={
                        "opportunity": opportunity,
                        "distance": distance_value,
                        "uncertainty": uncertainty,
                    },
                    evidence_refs=(
                        f"m2:pfz:{candidate_id}",
                    ),
                    uncertainty_refs=(
                        f"m2:confidence:{candidate_id}",
                    ),
                )
            )

        # ---------------------------------------------------------
        # 6. Ensure candidates exist
        # ---------------------------------------------------------
        if not proposals:
            raise InsufficientEvidenceError(
                "M2 returned no valid PFZ candidates"
            )

        # ---------------------------------------------------------
        # 7. Build MarineWorldState
        # ---------------------------------------------------------
        now = datetime.now()

        world_state = MarineWorldState(
            state_id=f"m2-{uuid.uuid4()}",
            schema_version="1.0",
            generated_at=now,
            time=now,
            region=StateRegion(
                name=request.location,
            ),
            ocean_state=OceanState(
                variables={
                    "sst": data.get("sst"),
                    "chlorophyll": data.get("chlorophyll"),
                    "wave_height": data.get("wave_height"),
                    "wave_period": data.get("wave_period"),
                    "current_speed": data.get("current_speed"),
                }
            ),
            weather_state=WeatherState(),
            hazard_state=HazardState(
                hazards=hazards,
            ),
            geospatial_state=GeospatialState(),
            ecological_state=EcologicalState(),
            vessel_state=VesselState(
                category=request.vessel_type or "Unknown",
            ),
            constraints=tuple(),
            evidence=tuple(),
            uncertainties=tuple(),
            candidate_actions=tuple(),
            decision_state=DecisionState(
                status="M2_EVALUATED",
            ),
        )

        # ---------------------------------------------------------
        # 8. Convert M2 safety into M1 SafetyEvaluation
        # ---------------------------------------------------------
        safety_evaluations = tuple(
            SafetyEvaluation(
                candidate_id=proposal.id,
                status=safety_status,
                constraint_results={
                    str(hazard): False
                    for hazard in hazards
                },
                failed_constraints=tuple(
                    str(hazard)
                    for hazard in hazards
                ),
                evidence_refs=evidence_refs,
                uncertainty_refs=proposal.uncertainty_refs,
                reason=(
                    "; ".join(
                        str(reason)
                        for reason in reasons
                    )
                    or None
                ),
                safety_margin=None,
            )
            for proposal in proposals
        )

        # ---------------------------------------------------------
        # 9. Return M4 -> M1 integration contract
        # ---------------------------------------------------------
        return (
            world_state,
            tuple(proposals),
            safety_evaluations,
        )