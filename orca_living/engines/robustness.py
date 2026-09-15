"""Robustness analysis for ORCA-LIVING.

Robustness measures how stable an existing decision is under
controlled perturbations.

It does not claim statistical confidence or probabilistic certainty.

Each scenario must be explicitly recomputed by the supplied
counterfactual/recomputation function.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from orca_living.models.decision import Decision


@dataclass(frozen=True)
class RobustnessScenarioResult:
    """Result of one controlled perturbation."""

    scenario_id: str
    decision_id: str
    recommended_candidate_id: str | None
    decision_changed: bool


@dataclass(frozen=True)
class RobustnessResult:
    """Aggregate robustness assessment."""

    level: str
    baseline_decision_id: str
    baseline_candidate_id: str | None
    scenarios: tuple[RobustnessScenarioResult, ...]
    changed_scenario_ids: tuple[str, ...]
    explanation: str


class RobustnessAnalyzer:
    """Evaluates decision stability across controlled scenarios."""

    def analyze(
        self,
        baseline_decision: Decision,
        scenario_decisions: tuple[
            tuple[str, Decision],
            ...,
        ],
    ) -> RobustnessResult:
        """Classify robustness from explicit scenario decisions."""

        if not scenario_decisions:
            raise ValueError(
                "at least one robustness scenario is required"
            )

        baseline_candidate = (
            baseline_decision.recommended_candidate_id
        )

        results: list[RobustnessScenarioResult] = []
        changed_ids: list[str] = []

        for scenario_id, decision in scenario_decisions:
            changed = (
                baseline_decision.status != decision.status
                or baseline_candidate
                != decision.recommended_candidate_id
            )

            results.append(
                RobustnessScenarioResult(
                    scenario_id=scenario_id,
                    decision_id=decision.id,
                    recommended_candidate_id=(
                        decision.recommended_candidate_id
                    ),
                    decision_changed=changed,
                )
            )

            if changed:
                changed_ids.append(scenario_id)

        changed_count = len(changed_ids)
        total_count = len(scenario_decisions)

        if changed_count == 0:
            level = "HIGH"
            explanation = (
                "The recommendation remained unchanged across "
                "all tested perturbation scenarios."
            )
        elif changed_count < total_count:
            level = "MEDIUM"
            explanation = (
                "The recommendation changed under some but not "
                "all tested perturbation scenarios."
            )
        else:
            level = "LOW"
            explanation = (
                "The recommendation changed under every tested "
                "perturbation scenario."
            )

        return RobustnessResult(
            level=level,
            baseline_decision_id=baseline_decision.id,
            baseline_candidate_id=baseline_candidate,
            scenarios=tuple(results),
            changed_scenario_ids=tuple(changed_ids),
            explanation=explanation,
        )
