"""Canonical counterfactual contract for ORCA-LIVING.

A Counterfactual represents a controlled change to the marine
decision state and the resulting decision comparison.

The model records results produced by the counterfactual engine.
It does not perform scientific calculations itself.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class CounterfactualChange:
    """One controlled change applied to the baseline state."""

    variable: str
    original_value: float
    changed_value: float
    unit: str
    reason: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.variable.strip():
            raise ValueError(
                "CounterfactualChange.variable cannot be empty"
            )

        if not self.unit.strip():
            raise ValueError(
                "CounterfactualChange.unit cannot be empty"
            )


@dataclass(frozen=True)
class Counterfactual:
    """Result of recomputing ORCA under a changed world state."""

    id: str
    baseline_decision_id: str

    changes: tuple[CounterfactualChange, ...] = field(
        default_factory=tuple
    )

    affected_variables: tuple[str, ...] = field(
        default_factory=tuple
    )

    recomputed_features: tuple[str, ...] = field(
        default_factory=tuple
    )

    safety_status: Optional[str] = None

    changed_decision_id: Optional[str] = None

    baseline_recommended_candidate_id: Optional[str] = None

    counterfactual_recommended_candidate_id: Optional[str] = None

    decision_changed: bool = False

    explanation: Optional[str] = None

    evidence_refs: tuple[str, ...] = field(
        default_factory=tuple
    )

    uncertainty_refs: tuple[str, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError(
                "Counterfactual.id cannot be empty"
            )

        if not self.baseline_decision_id.strip():
            raise ValueError(
                "baseline_decision_id cannot be empty"
            )

        if self.safety_status is not None:
            valid_statuses = {
                "SAFE",
                "UNSAFE",
                "INSUFFICIENT_EVIDENCE",
            }

            if self.safety_status not in valid_statuses:
                raise ValueError(
                    "safety_status must be SAFE, UNSAFE, "
                    "or INSUFFICIENT_EVIDENCE"
                )

        if (
            self.changed_decision_id is not None
            and not self.changed_decision_id.strip()
        ):
            raise ValueError(
                "changed_decision_id cannot be empty"
            )

        if (
            self.baseline_recommended_candidate_id is not None
            and not self.baseline_recommended_candidate_id.strip()
        ):
            raise ValueError(
                "baseline_recommended_candidate_id cannot be empty"
            )

        if (
            self.counterfactual_recommended_candidate_id is not None
            and not self.counterfactual_recommended_candidate_id.strip()
        ):
            raise ValueError(
                "counterfactual_recommended_candidate_id "
                "cannot be empty"
            )

        for variable in self.affected_variables:
            if not variable.strip():
                raise ValueError(
                    "affected_variables cannot contain empty values"
                )

        for feature in self.recomputed_features:
            if not feature.strip():
                raise ValueError(
                    "recomputed_features cannot contain empty values"
                )
