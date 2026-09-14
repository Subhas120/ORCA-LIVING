"""M4 Response Adapter.

Converts M1 DecisionIntelligence into the public M4 API response.

M4 performs structural response adaptation only.
Decision logic remains owned by M1.
"""

from __future__ import annotations

from typing import Any, Iterable

from orca_living.engines.candidate_generator import CandidateProposal
from orca_living.models.decision_intelligence import DecisionIntelligence

from backend.models.response import (
    Candidate,
    DecisionResponse,
    Objective,
    StatusEnum,
)


class ResponseAdapter:
    """Adapt M1 decision output into the public M4 API response."""

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
        """Convert a candidate proposal into the public API shape.

        This is structural adaptation only.
        No safety score is fabricated.
        """

        uncertainty_value = proposal.objective_values.get(
            "uncertainty",
            0.0,
        )

        expected_opportunity = (
            proposal.expected_opportunity
        )

        opportunity = None
        confidence = None

        if expected_opportunity is not None:
            opportunity_value = max(
                0.0,
                min(
                    1.0,
                    float(expected_opportunity),
                ),
            )

            opportunity = round(
                opportunity_value * 100
            )

            confidence = (
                f"{round(opportunity_value * 100)}%"
            )

        uncertainty = None

        if uncertainty_value is not None:
            uncertainty_value = max(
                0.0,
                min(
                    1.0,
                    float(uncertainty_value),
                ),
            )

            uncertainty = round(
                uncertainty_value * 100
            )

        distance = None

        if proposal.distance is not None:
            distance = round(
                float(proposal.distance)
            )

        return Candidate(
            id=proposal.id,
            name=proposal.name or proposal.id,
            status=status,

            # M1/M2 safety is represented separately by
            # marineSafetyStatus. M4 does not invent a score.
            safety=None,

            opportunity=opportunity,
            uncertainty=uncertainty,
            distance=distance,
            confidence=confidence,

            lat=proposal.latitude,
            lng=proposal.longitude,

            reason=reason,
        )

    @staticmethod
    def adapt(
        decision_intel: DecisionIntelligence,
        status: StatusEnum,
        proposals: Iterable[CandidateProposal] = (),
        *,
        objective: Objective | None = None,
        marine_safety_status: str | None = None,
        marine_safety_reasons: Iterable[str] = (),
        uncertainty: Any = None,
        evidence: Iterable[Any] = (),
        sensitivity: Any = None,
    ) -> DecisionResponse:
        """Convert M1 output into the public M4 response.

        M4 does not recalculate:
        - recommendation
        - alternatives
        - rejected candidates
        - Pareto results
        - tradeoffs
        - robustness
        - sensitivity
        - counterfactuals
        - value of information
        - explanation
        - decision trace
        - confidence

        Those remain M1-owned outputs.
        """

        proposals = tuple(proposals)

        proposal_by_id = {
            proposal.id: proposal
            for proposal in proposals
        }

        # ---------------------------------------------------------
        # Recommended candidate
        # ---------------------------------------------------------

        recommended_candidate = None

        recommended_id = (
            decision_intel.recommended_candidate_id
        )

        if recommended_id:
            proposal = proposal_by_id.get(
                recommended_id
            )

            if proposal is not None:
                recommended_candidate = (
                    ResponseAdapter._candidate(
                        proposal,
                        status="RECOMMENDED",
                    )
                )

        # ---------------------------------------------------------
        # Alternatives
        #
        # Only M1-classified alternatives are exposed.
        # ---------------------------------------------------------

        alternative_candidates = []

        for candidate_id in (
            decision_intel.alternative_candidate_ids
            or ()
        ):
            proposal = proposal_by_id.get(
                candidate_id
            )

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
        # Rejected candidates can never become alternatives.
        # ---------------------------------------------------------

        rejected_candidates = []

        rejection_reasons = (
            decision_intel.rejection_reasons
            or ()
        )

        for candidate_id in (
            decision_intel.rejected_candidate_ids
            or ()
        ):
            proposal = proposal_by_id.get(
                candidate_id
            )

            if proposal is None:
                continue

            rejected_candidates.append(
                ResponseAdapter._candidate(
                    proposal,
                    status="REJECTED",
                    reason=(
                        ResponseAdapter._rejection_reason(
                            candidate_id,
                            rejection_reasons,
                        )
                    ),
                )
            )

        # ---------------------------------------------------------
        # Evidence and uncertainty
        #
        # M4 only forwards values supplied by upstream layers.
        # Empty values remain empty rather than being fabricated.
        # ---------------------------------------------------------

        evidence_items = list(
            evidence or ()
        )

        # ---------------------------------------------------------
        # Final public response
        # ---------------------------------------------------------

        return DecisionResponse(
            status=status,

            objective=objective,

            recommendedCandidate=(
                recommended_candidate
            ),

            alternativeCandidates=(
                alternative_candidates
            ),

            rejectedCandidates=(
                rejected_candidates
            ),

            decisionSummary=(
                decision_intel.summary
            ),

            tradeoffs=list(
                decision_intel.tradeoffs
                or ()
            ),

            uncertainty=uncertainty,

            evidence=evidence_items,

            sensitivity=sensitivity,

            # Preserve M1 decision intelligence.
            paretoCandidateIds=list(
                decision_intel.pareto_candidate_ids
                or ()
            ),

            robustness=(
                decision_intel.robustness
            ),

            valueOfInformation=(
                decision_intel.value_of_information
            ),

            counterfactuals=list(
                decision_intel.counterfactuals
                or ()
            ),

            explanation=(
                decision_intel.explanation
            ),

            decisionTrace=(
                decision_intel.decision_trace
            ),

            confidence=(
                decision_intel.confidence
            ),

            marineSafetyStatus=(
                marine_safety_status
            ),

            marineSafetyReasons=list(
                dict.fromkeys(
                    reason
                    for reason in (
                        marine_safety_reasons
                        or ()
                    )
                    if reason
                )
            ),

            dataMode="DEMO",
        )