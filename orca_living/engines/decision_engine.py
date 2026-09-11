"""Decision engine for ORCA-LIVING.

The DecisionEngine coordinates the deterministic M1 decision pipeline:

CandidateAction[]
        ↓
Safety Firewall
        ↓
Dominance Filter
        ↓
Multi-Objective Optimizer
        ↓
Decision

Scientific safety is supplied by M2 through SafetyEvaluation.

The engine never overrides an UNSAFE or INSUFFICIENT_EVIDENCE
evaluation.
"""

from __future__ import annotations

from orca_living.engines.dominance import DominanceFilter
from orca_living.engines.optimizer import MultiObjectiveOptimizer
from orca_living.engines.safety_firewall import SafetyFirewall
from orca_living.models.candidate import CandidateAction
from orca_living.models.decision import Decision
from orca_living.models.objective import UserObjective
from orca_living.models.safety import SafetyEvaluation


class DecisionEngine:
    """Coordinates the deterministic ORCA decision pipeline."""

    def __init__(
        self,
        safety_firewall: SafetyFirewall | None = None,
        dominance_filter: DominanceFilter | None = None,
        optimizer: MultiObjectiveOptimizer | None = None,
    ) -> None:
        self.safety_firewall = (
            safety_firewall
            if safety_firewall is not None
            else SafetyFirewall()
        )

        self.dominance_filter = (
            dominance_filter
            if dominance_filter is not None
            else DominanceFilter()
        )

        self.optimizer = (
            optimizer
            if optimizer is not None
            else MultiObjectiveOptimizer()
        )

    def decide(
        self,
        candidates: tuple[CandidateAction, ...],
        evaluations: tuple[SafetyEvaluation, ...],
        objective: UserObjective,
        decision_id: str,
    ) -> Decision:
        """Produce a structured decision from evaluated candidates."""

        if not decision_id.strip():
            raise ValueError(
                "decision_id cannot be empty"
            )

        if not candidates:
            return Decision(
                id=decision_id,
                status="NO_SAFE_ACTION",
                reason="No candidate actions were generated.",
            )

        firewall_result = self.safety_firewall.filter(
            candidates=candidates,
            evaluations=evaluations,
        )

        safe_candidates = firewall_result.safe_candidates
        rejected_candidates = firewall_result.rejected_candidates

        rejection_reasons = {}

        evaluation_by_id = {
            evaluation.candidate_id: evaluation
            for evaluation in evaluations
        }

        for candidate in rejected_candidates:
            evaluation = evaluation_by_id.get(candidate.id)

            if evaluation is None:
                rejection_reasons[candidate.id] = (
                    "No safety evaluation was available."
                )
            elif evaluation.reason:
                rejection_reasons[candidate.id] = evaluation.reason
            else:
                rejection_reasons[candidate.id] = (
                    f"Candidate classified as {evaluation.status}."
                )

        if not safe_candidates:
            has_insufficient_evidence = any(
                evaluation.status == "INSUFFICIENT_EVIDENCE"
                for evaluation in evaluations
            )

            status = (
                "INSUFFICIENT_EVIDENCE"
                if has_insufficient_evidence
                else "NO_SAFE_ACTION"
            )

            return Decision(
                id=decision_id,
                status=status,
                rejected_candidate_ids=tuple(
                    candidate.id
                    for candidate in rejected_candidates
                ),
                rejection_reasons=rejection_reasons,
                evidence_refs=tuple(
                    ref
                    for evaluation in evaluations
                    for ref in evaluation.evidence_refs
                ),
                uncertainty_refs=tuple(
                    ref
                    for evaluation in evaluations
                    for ref in evaluation.uncertainty_refs
                ),
                reason=(
                    "No safe actionable candidate is available."
                    if status == "NO_SAFE_ACTION"
                    else
                    "A safe decision cannot be made because "
                    "critical evidence is insufficient."
                ),
            )

        dominance_result = self.dominance_filter.filter(
            safe_candidates
        )

        frontier = dominance_result.non_dominated_candidates
        dominated = dominance_result.dominated_candidates

        optimization_result = self.optimizer.optimize(
            candidates=frontier,
            objective=objective,
        )

        preferred = optimization_result.preferred_candidate

        alternative_ids = tuple(
            candidate.id
            for candidate in frontier
            if candidate.id != preferred.id
        )

        rejection_reasons.update(
            dominance_result.domination_reasons
        )

        rejected_ids = tuple(
            candidate.id
            for candidate in rejected_candidates
        ) + tuple(
            candidate.id
            for candidate in dominated
        )

        evidence_refs = tuple(
            dict.fromkeys(
                ref
                for candidate in candidates
                for ref in candidate.evidence_refs
            )
        )

        uncertainty_refs = tuple(
            dict.fromkeys(
                ref
                for candidate in candidates
                for ref in candidate.uncertainty_refs
            )
        )

        return Decision(
            id=decision_id,
            status="RECOMMENDED",
            recommended_candidate_id=preferred.id,
            alternative_candidate_ids=alternative_ids,
            rejected_candidate_ids=rejected_ids,
            rejection_reasons=rejection_reasons,
            pareto_candidate_ids=tuple(
                candidate.id
                for candidate in frontier
            ),
            evidence_refs=evidence_refs,
            uncertainty_refs=uncertainty_refs,
            reason=(
                f"{preferred.id} was preferred using the explicit "
                f"objective priority order: "
                f"{optimization_result.comparison_order}."
            ),
        )
