"""Decision sensitivity analysis for ORCA-LIVING.

Sensitivity analysis compares explicitly recomputed scenarios
against a baseline decision.

It identifies decision dependency, not scientific causality.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from orca_living.models.decision import Decision
from orca_living.models.sensitivity import (
    SensitivityResult,
    SensitivityVariableResult,
)


@dataclass(frozen=True)
class SensitivityScenario:
    """One explicitly recomputed scenario."""

    scenario_id: str
    variable: str
    decision: Decision

    def __post_init__(self) -> None:
        if not self.scenario_id.strip():
            raise ValueError(
                "scenario_id cannot be empty"
            )

        if not self.variable.strip():
            raise ValueError(
                "variable cannot be empty"
            )


class SensitivityAnalyzer:
    """Determines which variables affect the decision."""

    def analyze(
        self,
        baseline_decision: Decision,
        scenarios: tuple[SensitivityScenario, ...],
    ) -> SensitivityResult:
        """Analyze explicitly recomputed sensitivity scenarios."""

        if not scenarios:
            raise ValueError(
                "at least one sensitivity scenario is required"
            )

        grouped: dict[
            str,
            list[SensitivityScenario],
        ] = {}

        for scenario in scenarios:
            grouped.setdefault(
                scenario.variable,
                [],
            ).append(scenario)

        results: list[SensitivityVariableResult] = []

        for variable, variable_scenarios in grouped.items():
            tested_ids = tuple(
                scenario.scenario_id
                for scenario in variable_scenarios
            )

            changed_ids = tuple(
                scenario.scenario_id
                for scenario in variable_scenarios
                if self._decision_changed(
                    baseline_decision,
                    scenario.decision,
                )
            )

            sensitive = bool(changed_ids)

            if sensitive:
                explanation = (
                    f"Changes to {variable} altered the decision "
                    f"under the tested scenario(s): "
                    f"{', '.join(changed_ids)}."
                )
            else:
                explanation = (
                    f"Changes to {variable} did not alter the "
                    "decision under the tested scenarios."
                )

            results.append(
                SensitivityVariableResult(
                    variable=variable,
                    scenarios_tested=tested_ids,
                    changed_scenario_ids=changed_ids,
                    materially_affects_decision=sensitive,
                    explanation=explanation,
                )
            )

        sensitive_variables = tuple(
            result.variable
            for result in results
            if result.materially_affects_decision
        )

        insensitive_variables = tuple(
            result.variable
            for result in results
            if not result.materially_affects_decision
        )

        if sensitive_variables:
            explanation = (
                "The decision changed under controlled "
                "perturbations of: "
                f"{', '.join(sensitive_variables)}."
            )
        else:
            explanation = (
                "The decision remained unchanged across all "
                "tested variable perturbations."
            )

        return SensitivityResult(
            baseline_decision_id=baseline_decision.id,
            variables=tuple(results),
            sensitive_variables=sensitive_variables,
            insensitive_variables=insensitive_variables,
            explanation=explanation,
        )

    @staticmethod
    def _decision_changed(
        baseline: Decision,
        scenario: Decision,
    ) -> bool:
        """Return whether the scenario changed the decision."""

        return (
            baseline.status != scenario.status
            or baseline.recommended_candidate_id
            != scenario.recommended_candidate_id
        )
