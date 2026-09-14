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
    def _rejection_reason(
        candidate_id: str,
        rejection_reasons: Iterable[str],
    ) -> str | None:
        """Extract the M1 rejection reason for a candidate."""

        prefix = f"{candidate_id}:"

        for reason in rejection_reasons:
            if reason.startswith(prefix):
                return reason[len(prefix):].strip()

        return None

    @staticmethod
    def _candidate(
        proposal: CandidateProposal,
        *,
        status: str,
        reason: str | None = None,
    ) -> Candidate:
        """Convert a proposal into the public candidate shape."""

        uncertainty_value = proposal.objective_values.get(
            "uncertainty",
            0.0,
        )

        return Candidate(
            id=proposal.id,
            name=proposal.name or proposal.id,
            status=status,

            # M1 does not expose a numeric safety score.
            # Do not invent one at the M4 boundary.
            safety=None,

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
            reason=reason,
        )

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

        recommended_id = decision_intel.recommended_candidate_id

        # ---------------------------------------------------------
        # Recommended candidate
        # ---------------------------------------------------------
        recommended_candidate = None

        if recommended_id:
            proposal = proposal_by_id.get(recommended_id)

            if proposal is not None:
                recommended_candidate = ResponseAdapter._candidate(
                    proposal,
                    status="RECOMMENDED",
                )

        # ---------------------------------------------------------
        # Alternative candidates
        #
        # IMPORTANT:
        # Only candidates explicitly classified as alternatives
        # by M1 may appear here.
        # ---------------------------------------------------------
        alternative_candidates = []

        for candidate_id in decision_intel.alternative_candidate_ids or ():
            proposal = proposal_by_id.get(candidate_id)

            if proposal is None:
                continue

            alternative_candidates.append(
                ResponseAdapter._candidate(
                    proposal,
                    status="ALTERNATIVE",
                )
            )

        # ---------------------------------------------------------
        # Rejected candidates
        #
        # IMPORTANT:
        # Rejected/unsafe candidates must NEVER be exposed as
        # alternatives.
        # ---------------------------------------------------------
        rejected_candidates = []

        rejection_reasons = (
            decision_intel.rejection_reasons or ()
        )

        for candidate_id in decision_intel.rejected_candidate_ids or ():
            proposal = proposal_by_id.get(candidate_id)

            if proposal is None:
                continue

            rejected_candidates.append(
                ResponseAdapter._candidate(
                    proposal,
                    status="REJECTED",
                    reason=ResponseAdapter._rejection_reason(
                        candidate_id,
                        rejection_reasons,
                    ),
                )
            )

        # ---------------------------------------------------------
        # Return API response
        # ---------------------------------------------------------
        return DecisionResponse(
            status=status,
            recommendedCandidate=recommended_candidate,
            alternativeCandidates=alternative_candidates,
            rejectedCandidates=rejected_candidates,
            decisionSummary=decision_intel.summary,
            tradeoffs=list(
                decision_intel.tradeoffs or ()
            ),
        )