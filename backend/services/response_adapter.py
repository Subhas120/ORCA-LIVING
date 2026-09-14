"""M4 Response Adapter.

Converts M1 DecisionIntelligence into the public M4 API response.

M4 performs structural response adaptation only.
Decision logic remains owned by M1.
"""

from __future__ import annotations

from typing import Iterable

from orca_living.engines.candidate_generator import CandidateProposal
from orca_living.models.decision_intelligence import DecisionIntelligence

from backend.models.response import (
    Candidate,
    DecisionResponse,
    StatusEnum,
)


class ResponseAdapter:
    """Adapt M1 decision output into the M4 API response."""

    @staticmethod
    def adapt(
        decision_intel: DecisionIntelligence,
        status: StatusEnum,
        proposals: Iterable[CandidateProposal] = (),
    ) -> DecisionResponse:
        """Convert M1 decision output into the public API response."""

        proposals = tuple(proposals)

        proposal_by_id = {
            proposal.id: proposal
            for proposal in proposals
        }

        recommended_candidate = None

        recommended_id = decision_intel.recommended_candidate_id

        # ---------------------------------------------------------
        # Recommended candidate
        # ---------------------------------------------------------
        if recommended_id:
            proposal = proposal_by_id.get(recommended_id)

            if proposal is not None:
                uncertainty_value = proposal.objective_values.get(
                    "uncertainty",
                    0.0,
                )

                recommended_candidate = Candidate(
                    id=proposal.id,
                    name=proposal.name or proposal.id,
                    status="RECOMMENDED",
                    safety=1,
                    opportunity=round(
                        proposal.expected_opportunity * 100
                    ),
                    uncertainty=round(
                        float(uncertainty_value) * 100
                    ),
                    distance=round(
                        proposal.distance or 0.0
                    ),
                    confidence=(
                        f"{round(proposal.expected_opportunity * 100)}%"
                    ),
                    lat=proposal.latitude,
                    lng=proposal.longitude,
                    reason=None,
                )

        # ---------------------------------------------------------
        # Alternative candidates
        # ---------------------------------------------------------
        alternative_candidates = []

        for proposal in proposals:
            if proposal.id == recommended_id:
                continue

            uncertainty_value = proposal.objective_values.get(
                "uncertainty",
                0.0,
            )

            alternative_candidates.append(
                Candidate(
                    id=proposal.id,
                    name=proposal.name or proposal.id,
                    status="ALTERNATIVE",
                    safety=1,
                    opportunity=round(
                        proposal.expected_opportunity * 100
                    ),
                    uncertainty=round(
                        float(uncertainty_value) * 100
                    ),
                    distance=round(
                        proposal.distance or 0.0
                    ),
                    confidence=(
                        f"{round(proposal.expected_opportunity * 100)}%"
                    ),
                    lat=proposal.latitude,
                    lng=proposal.longitude,
                    reason=None,
                )
            )

        # ---------------------------------------------------------
        # Return API response
        # ---------------------------------------------------------
        return DecisionResponse(
            status=status,
            recommendedCandidate=recommended_candidate,
            alternativeCandidates=alternative_candidates,
            decisionSummary=decision_intel.summary,
            tradeoffs=list(
                decision_intel.tradeoffs or ()
            ),
        )