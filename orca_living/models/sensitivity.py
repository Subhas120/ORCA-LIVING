"""Decision sensitivity contracts for ORCA-LIVING.

Sensitivity identifies variables whose controlled perturbations
materially change a decision.

It does not establish scientific causality.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SensitivityVariableResult:
    """Sensitivity result for one decision-relevant variable."""

    variable: str

    scenarios_tested: tuple[str, ...] = field(
        default_factory=tuple
    )

    changed_scenario_ids: tuple[str, ...] = field(
        default_factory=tuple
    )

    materially_affects_decision: bool = False

    explanation: str = ""

    def __post_init__(self) -> None:
        if not self.variable.strip():
            raise ValueError("variable cannot be empty")

        for scenario_id in self.scenarios_tested:
            if not scenario_id.strip():
                raise ValueError(
                    "scenarios_tested cannot contain empty values"
                )

        for scenario_id in self.changed_scenario_ids:
            if not scenario_id.strip():
                raise ValueError(
                    "changed_scenario_ids cannot contain empty values"
                )

        if not self.explanation.strip():
            raise ValueError("explanation cannot be empty")

        for scenario_id in self.changed_scenario_ids:
            if scenario_id not in self.scenarios_tested:
                raise ValueError(
                    "changed scenario must be one of the tested scenarios"
                )


@dataclass(frozen=True)
class SensitivityResult:
    """Aggregate decision sensitivity across variables."""

    baseline_decision_id: str

    variables: tuple[SensitivityVariableResult, ...] = field(
        default_factory=tuple
    )

    sensitive_variables: tuple[str, ...] = field(
        default_factory=tuple
    )

    insensitive_variables: tuple[str, ...] = field(
        default_factory=tuple
    )

    explanation: str = ""

    def __post_init__(self) -> None:
        if not self.baseline_decision_id.strip():
            raise ValueError(
                "baseline_decision_id cannot be empty"
            )

        if not self.variables:
            raise ValueError(
                "at least one sensitivity variable is required"
            )

        if not self.explanation.strip():
            raise ValueError("explanation cannot be empty")

        variable_names = {
            result.variable
            for result in self.variables
        }

        for variable in self.sensitive_variables:
            if variable not in variable_names:
                raise ValueError(
                    "sensitive variable must be present in variables"
                )

        for variable in self.insensitive_variables:
            if variable not in variable_names:
                raise ValueError(
                    "insensitive variable must be present in variables"
                )

        if set(self.sensitive_variables) & set(
            self.insensitive_variables
        ):
            raise ValueError(
                "a variable cannot be both sensitive and insensitive"
            )
