from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class InformationRequest:
    id: str
    variable: str
    reason: str
    current_uncertainty_refs: Tuple[str, ...] = ()
    scenario_ids: Tuple[str, ...] = ()
    priority: str = "LOW"

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("InformationRequest id cannot be empty.")

        if not self.variable:
            raise ValueError("InformationRequest variable cannot be empty.")

        if self.priority not in {"HIGH", "MEDIUM", "LOW"}:
            raise ValueError(
                "InformationRequest priority must be HIGH, MEDIUM, or LOW."
            )


@dataclass(frozen=True)
class ValueOfInformationResult:
    baseline_decision_id: str
    information_requests: Tuple[InformationRequest, ...] = ()
    high_value_information: Tuple[str, ...] = ()
    medium_value_information: Tuple[str, ...] = ()
    low_value_information: Tuple[str, ...] = ()
    explanation: str = ""

    def __post_init__(self) -> None:
        if not self.baseline_decision_id:
            raise ValueError("baseline_decision_id cannot be empty.")
