from typing import Iterable

from orca_living.models.decision import Decision
from orca_living.models.decision_intelligence import DecisionIntelligence


class DecisionIntelligenceAssembler:
    """
    Integrates the outputs of M1 decision-intelligence components.

    This component is an assembler, not a new decision algorithm.

    It does not:
    - calculate scientific facts
    - override safety
    - recalculate optimization
    - invent confidence
    - modify an existing Decision

    It packages the already-computed results into one coherent
    DecisionIntelligence object.
    """

    def assemble(
        self,
        decision: Decision,
        *,
        decision_trace=None,
        explanation=None,
        robustness=None,
        sensitivity=None,
        value_of_information=None,
        counterfactuals: Iterable = (),
    ) -> DecisionIntelligence:

        rejected_ids = tuple(decision.rejected_candidate_ids)

        rejection_reasons = tuple(
            f"{candidate_id}: {reason}"
            for candidate_id, reason
            in decision.rejection_reasons.items()
        )

        summary = self._build_summary(decision)

        return DecisionIntelligence(
            decision_id=decision.id,
            status=decision.status,
            recommended_candidate_id=decision.recommended_candidate_id,
            alternative_candidate_ids=tuple(
                decision.alternative_candidate_ids
            ),
            rejected_candidate_ids=rejected_ids,
            rejection_reasons=rejection_reasons,
            pareto_candidate_ids=tuple(
                decision.pareto_candidate_ids
            ),
            tradeoffs=tuple(decision.tradeoffs),
            evidence_refs=tuple(decision.evidence_refs),
            uncertainty_refs=tuple(decision.uncertainty_refs),
            robustness=robustness,
            sensitivity=sensitivity,
            value_of_information=value_of_information,
            counterfactuals=tuple(counterfactuals),
            explanation=explanation,
            decision_trace=decision_trace,
            confidence=decision.confidence,
            summary=summary,
        )

    @staticmethod
    def _build_summary(decision: Decision) -> str:
        if decision.status == "NO_SAFE_ACTION":
            return "No safe actionable candidate is available."

        if decision.status == "INSUFFICIENT_EVIDENCE":
            return "A decision cannot be safely completed because critical evidence is insufficient."

        if decision.status == "NO_ACTIONABLE_DIFFERENCE":
            return "No actionable difference was established between the evaluated alternatives."

        if decision.recommended_candidate_id:
            return (
                f"Candidate {decision.recommended_candidate_id} "
                f"is the recommended candidate after the declared "
                f"decision process."
            )

        return "The decision process completed without a recommended candidate."
