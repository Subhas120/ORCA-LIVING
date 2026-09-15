"""Counterfactual reasoning engine for ORCA-LIVING.

The counterfactual engine evaluates a controlled modification of the
decision context and compares the resulting decision with a baseline.

Scientific feature recomputation is injected into the engine.
M1 does not invent scientific consequences.

The engine:
1. Applies a controlled scenario through the recomputation function.
2. Receives recomputed candidates and safety evaluations.
3. Runs the normal DecisionEngine.
4. Compares baseline and counterfactual decisions.
5. Produces a Counterfactual record.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from orca_living.engines.decision_engine import DecisionEngine
from orca_living.models.candidate import CandidateAction
from orca_living.models.counterfactual import (
    Counterfactual,
    CounterfactualChange,
)
from orca_living.models.decision import Decision
from orca_living.models.objective import UserObjective
from orca_living.models.safety import SafetyEvaluation


@dataclass(frozen=True)
class CounterfactualInput:
    """Controlled scenario requested by the user or planner."""

    changes: tuple[CounterfactualChange, ...]


@dataclass(frozen=True)
class RecomputedScenario:
    """Scientifically recomputed state relevant to decision-making."""

    candidates: tuple[CandidateAction, ...]

    evaluations: tuple[SafetyEvaluation, ...]

    affected_variables: tuple[str, ...]

    recomputed_features: tuple[str, ...]


RecomputeFunction = Callable[
    [CounterfactualInput],
    RecomputedScenario,
]


class CounterfactualEngine:
    """Runs controlled what-if decision recomputation."""

    def __init__(
        self,
        decision_engine: DecisionEngine | None = None,
    ) -> None:
        self.decision_engine = (
            decision_engine
            if decision_engine is not None
            else DecisionEngine()
        )

    def evaluate(
        self,
        baseline_decision: Decision,
        scenario: CounterfactualInput,
        objective: UserObjective,
        recompute: RecomputeFunction,
        counterfactual_id: str,
    ) -> Counterfactual:
        """Evaluate a controlled scenario against a baseline decision."""

        if not counterfactual_id.strip():
            raise ValueError(
                "counterfactual_id cannot be empty"
            )

        if not scenario.changes:
            raise ValueError(
                "counterfactual scenario must contain at least one change"
            )

        recomputed = recompute(scenario)

        changed_decision = self.decision_engine.decide(
            candidates=recomputed.candidates,
            evaluations=recomputed.evaluations,
            objective=objective,
            decision_id=f"{counterfactual_id}_decision",
        )

        baseline_candidate = (
            baseline_decision.recommended_candidate_id
        )

        changed_candidate = (
            changed_decision.recommended_candidate_id
        )

        decision_changed = (
            baseline_decision.status != changed_decision.status
            or baseline_candidate != changed_candidate
        )

        explanation = (
            "Counterfactual scenario did not change the decision."
            if not decision_changed
            else
            "Counterfactual scenario changed the decision from "
            f"{baseline_candidate} to {changed_candidate}."
        )

        safety_status = None

        if changed_candidate is not None:
            for evaluation in recomputed.evaluations:
                if evaluation.candidate_id == changed_candidate:
                    safety_status = evaluation.status
                    break

        evidence_refs = tuple(
            dict.fromkeys(
                ref
                for candidate in recomputed.candidates
                for ref in candidate.evidence_refs
            )
        )

        uncertainty_refs = tuple(
            dict.fromkeys(
                ref
                for candidate in recomputed.candidates
                for ref in candidate.uncertainty_refs
            )
        )

        return Counterfactual(
            id=counterfactual_id,
            baseline_decision_id=baseline_decision.id,
            changes=scenario.changes,
            affected_variables=recomputed.affected_variables,
            recomputed_features=recomputed.recomputed_features,
            safety_status=safety_status,
            changed_decision_id=changed_decision.id,
            baseline_recommended_candidate_id=baseline_candidate,
            counterfactual_recommended_candidate_id=changed_candidate,
            decision_changed=decision_changed,
            explanation=explanation,
            evidence_refs=evidence_refs,
            uncertainty_refs=uncertainty_refs,
        )
