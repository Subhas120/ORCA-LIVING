"""Deterministic decision trace and explanation engine.

This engine assembles explanations from authoritative M1 decision
outputs. It does not calculate scientific facts, select candidates,
or modify decisions.
"""

from __future__ import annotations

from orca_living.models.decision import Decision
from orca_living.models.explanation import (
    DecisionExplanation,
    DecisionTrace,
)


class ExplanationEngine:
    """Builds deterministic decision lineage and explanations."""

    def build_trace(
        self,
        decision: Decision,
        candidate_ids: tuple[str, ...],
        safe_candidate_ids: tuple[str, ...],
        optimization_objectives: tuple[str, ...],
    ) -> DecisionTrace:
        """Build a machine-readable trace from an existing decision."""

        if not candidate_ids:
            raise ValueError("candidate_ids cannot be empty")

        safe_ids = tuple(
            candidate_id
            for candidate_id in safe_candidate_ids
            if candidate_id in candidate_ids
        )

        rejected_ids = tuple(
            candidate_id
            for candidate_id in decision.rejected_candidate_ids
            if candidate_id in candidate_ids
        )

        return DecisionTrace(
            decision_id=decision.id,
            candidate_ids=candidate_ids,
            recommended_candidate_id=(
                decision.recommended_candidate_id
            ),
            safe_candidate_ids=safe_ids,
            rejected_candidate_ids=rejected_ids,
            rejection_reasons=dict(decision.rejection_reasons),
            pareto_candidate_ids=decision.pareto_candidate_ids,
            tradeoffs=tuple(
                self._format_tradeoff(tradeoff)
                for tradeoff in decision.tradeoffs
            ),
            optimization_objectives=optimization_objectives,
            evidence_refs=decision.evidence_refs,
            uncertainty_refs=decision.uncertainty_refs,
        )

    def build_explanation(
        self,
        trace: DecisionTrace,
        decision: Decision,
    ) -> DecisionExplanation:
        """Build a deterministic explanation from an existing trace."""

        if trace.decision_id != decision.id:
            raise ValueError(
                "trace decision_id must match decision.id"
            )

        if decision.status == "RECOMMENDED":
            summary = (
                f"Candidate "
                f"{decision.recommended_candidate_id} "
                f"was selected from the evaluated alternatives."
            )
        elif decision.status == "NO_SAFE_ACTION":
            summary = (
                "No safe actionable candidate was available."
            )
        elif decision.status == "INSUFFICIENT_EVIDENCE":
            summary = (
                "A recommendation could not be made because "
                "critical evidence was insufficient."
            )
        else:
            summary = (
                "No actionable difference was established "
                "between the evaluated candidates."
            )

        safety_reason = self._build_safety_reason(trace)

        preference_reason = self._build_preference_reason(
            trace,
            decision,
        )

        return DecisionExplanation(
            decision_id=decision.id,
            summary=summary,
            safety_reason=safety_reason,
            preference_reason=preference_reason,
            tradeoffs=trace.tradeoffs,
            rejected_candidates=trace.rejected_candidate_ids,
            evidence_refs=trace.evidence_refs,
            uncertainty_refs=trace.uncertainty_refs,
        )

    @staticmethod
    def _format_tradeoff(tradeoff) -> str:
        return (
            f"{tradeoff.candidate_a} vs "
            f"{tradeoff.candidate_b}: "
            f"{tradeoff.objective_a} "
            f"{tradeoff.relationship} "
            f"{tradeoff.objective_b}"
        )

    @staticmethod
    def _build_safety_reason(
        trace: DecisionTrace,
    ) -> str:
        if trace.recommended_candidate_id is None:
            if trace.rejected_candidate_ids:
                return (
                    "No candidate passed the safety decision "
                    "requirements needed for recommendation."
                )

            return (
                "No candidate was available for a safety-backed "
                "recommendation."
            )

        return (
            f"Candidate {trace.recommended_candidate_id} "
            "was retained after the safety filtering stage."
        )

    @staticmethod
    def _build_preference_reason(
        trace: DecisionTrace,
        decision: Decision,
    ) -> str:
        if decision.recommended_candidate_id is None:
            return (
                "No preference was established because the "
                "decision did not produce a recommendation."
            )

        if trace.optimization_objectives:
            objectives = ", ".join(
                trace.optimization_objectives
            )

            return (
                f"Candidate "
                f"{decision.recommended_candidate_id} "
                f"was preferred using the declared objective "
                f"priority: {objectives}."
            )

        return (
            f"Candidate "
            f"{decision.recommended_candidate_id} "
            "was preferred by the decision engine."
        )
