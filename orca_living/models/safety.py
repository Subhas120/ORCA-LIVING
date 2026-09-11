"""Canonical safety-evaluation contract for ORCA-LIVING.

SafetyEvaluation represents the result of evaluating one candidate
against safety constraints.

M1 owns the contract and decision-flow integration.
M2 owns the scientific safety rules and calculations.

This module does not calculate marine safety thresholds.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


VALID_SAFETY_STATUSES = frozenset(
    {
        "SAFE",
        "UNSAFE",
        "INSUFFICIENT_EVIDENCE",
    }
)


@dataclass(frozen=True)
class SafetyEvaluation:
    """Deterministic record of a candidate's safety evaluation."""

    candidate_id: str
    status: str

    constraint_results: dict[str, bool] = field(default_factory=dict)

    failed_constraints: tuple[str, ...] = field(default_factory=tuple)

    evidence_refs: tuple[str, ...] = field(default_factory=tuple)

    uncertainty_refs: tuple[str, ...] = field(default_factory=tuple)

    reason: Optional[str] = None

    safety_margin: Optional[float] = None

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError(
                "SafetyEvaluation.candidate_id cannot be empty"
            )

        if self.status not in VALID_SAFETY_STATUSES:
            raise ValueError(
                "status must be SAFE, UNSAFE, or INSUFFICIENT_EVIDENCE"
            )

        for constraint, result in self.constraint_results.items():
            if not constraint.strip():
                raise ValueError(
                    "constraint_results cannot contain an empty constraint name"
                )

            if not isinstance(result, bool):
                raise ValueError(
                    "constraint_results values must be boolean"
                )

        if self.safety_margin is not None and self.safety_margin < 0.0:
            raise ValueError(
                "safety_margin cannot be negative"
            )
