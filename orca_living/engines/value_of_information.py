from dataclasses import dataclass
from typing import Iterable, Tuple

from orca_living.models.decision import Decision
from orca_living.models.value_of_information import (
    InformationRequest,
    ValueOfInformationResult,
)


@dataclass(frozen=True)
class InformationScenario:
    scenario_id: str
    variable: str
    decision: Decision


class ValueOfInformationAnalyzer:
    """
    Deterministic prototype Value-of-Information analyzer.

    This component does not calculate scientific value, monetary value,
    or probabilities. It evaluates whether additional information about
    an uncertain variable could materially affect the current decision.

    Scenario decisions are supplied externally and are expected to come
    from the scientific recomputation pipeline in later integration.
    """

    def analyze(
        self,
        baseline_decision: Decision,
        uncertain_variables: Iterable[tuple[str, tuple[str, ...]]],
        scenarios: Iterable[InformationScenario],
    ) -> ValueOfInformationResult:
        scenario_list = tuple(scenarios)

        requests = []

        for variable, uncertainty_refs in uncertain_variables:
            variable_scenarios = tuple(
                scenario
                for scenario in scenario_list
                if scenario.variable == variable
            )

            changed_scenarios = tuple(
                scenario.scenario_id
                for scenario in variable_scenarios
                if self._decision_changed(
                    baseline_decision,
                    scenario.decision,
                )
            )

            if changed_scenarios:
                priority = self._priority_for_changes(
                    baseline_decision,
                    variable_scenarios,
                )

                reason = (
                    f"Additional information about {variable} may have "
                    f"decision value because tested scenarios changed "
                    f"the baseline decision."
                )
            else:
                priority = "LOW"
                reason = (
                    f"Additional information about {variable} has low "
                    f"decision value in the tested scenarios because "
                    f"the baseline decision remained unchanged."
                )

            requests.append(
                InformationRequest(
                    id=f"voi_{variable}",
                    variable=variable,
                    reason=reason,
                    current_uncertainty_refs=tuple(uncertainty_refs),
                    scenario_ids=tuple(
                        scenario.scenario_id
                        for scenario in variable_scenarios
                    ),
                    priority=priority,
                )
            )

        requests_tuple = tuple(requests)

        high = tuple(
            request.variable
            for request in requests_tuple
            if request.priority == "HIGH"
        )

        medium = tuple(
            request.variable
            for request in requests_tuple
            if request.priority == "MEDIUM"
        )

        low = tuple(
            request.variable
            for request in requests_tuple
            if request.priority == "LOW"
        )

        valued_variables = high + medium

        if valued_variables:
            explanation = (
                "Additional information may materially improve the "
                "decision for: "
                + ", ".join(valued_variables)
                + "."
            )
        else:
            explanation = (
                "No tested uncertain variable materially changed "
                "the baseline decision."
            )

        return ValueOfInformationResult(
            baseline_decision_id=baseline_decision.id,
            information_requests=requests_tuple,
            high_value_information=high,
            medium_value_information=medium,
            low_value_information=low,
            explanation=explanation,
        )

    @staticmethod
    def _decision_changed(
        baseline: Decision,
        scenario: Decision,
    ) -> bool:
        return (
            baseline.status != scenario.status
            or baseline.recommended_candidate_id
            != scenario.recommended_candidate_id
        )

    @staticmethod
    def _priority_for_changes(
        baseline: Decision,
        scenarios: Tuple[InformationScenario, ...],
    ) -> str:
        """
        HIGH:
            A tested scenario changes the recommended candidate.

        MEDIUM:
            A tested scenario changes the decision status without
            changing the recommended candidate.

        LOW:
            No material decision change.
        """
        for scenario in scenarios:
            if (
                baseline.recommended_candidate_id
                != scenario.decision.recommended_candidate_id
            ):
                return "HIGH"

        for scenario in scenarios:
            if baseline.status != scenario.decision.status:
                return "MEDIUM"

        return "LOW"
