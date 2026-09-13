"""Canonical decision contract for ORCA-LIVING.

A Decision represents the structured result of ORCA's decision
process after safety evaluation, candidate comparison, and
multi-objective reasoning.

This module defines the decision result contract only.
It does not calculate rankings or perform optimization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


VALID_DECISION_STATUSES = frozenset(
    {
        "RECOMMENDED",
        "NO_SAFE_ACTION",
        "INSUFFICIENT_EVIDENCE",
        "NO_ACTIONABLE_DIFFERENCE",
    }
)


@dataclass(frozen=True)
class DecisionTradeoff:
    """One explicit tradeoff between decision objectives."""

    objective_a: str
    objective_b: str
    relationship: str
    candidate_a: str
    candidate_b: str

    def __post_init__(self) -> None:
        if not self.objective_a.strip():
            raise ValueError(
                "DecisionTradeoff.objective_a cannot be empty"
            )

        if not self.objective_b.strip():
            raise ValueError(
                "DecisionTradeoff.objective_b cannot be empty"
            )

        if not self.relationship.strip():
            raise ValueError(
                "DecisionTradeoff.relationship cannot be empty"
            )

        if not self.candidate_a.strip():
            raise ValueError(
                "DecisionTradeoff.candidate_a cannot be empty"
            )

        if not self.candidate_b.strip():
            raise ValueError(
                "DecisionTradeoff.candidate_b cannot be empty"
            )


@dataclass(frozen=True)
class Decision:
    """Structured output of ORCA-LIVING decision reasoning."""

    id: str
    status: str

    recommended_candidate_id: Optional[str] = None

    alternative_candidate_ids: tuple[str, ...] = field(
        default_factory=tuple
    )

    rejected_candidate_ids: tuple[str, ...] = field(
        default_factory=tuple
    )

    rejection_reasons: dict[str, str] = field(
        default_factory=dict
    )

    pareto_candidate_ids: tuple[str, ...] = field(
        default_factory=tuple
    )

    tradeoffs: tuple[DecisionTradeoff, ...] = field(
        default_factory=tuple
    )

    evidence_refs: tuple[str, ...] = field(
        default_factory=tuple
    )

    uncertainty_refs: tuple[str, ...] = field(
        default_factory=tuple
    )

    optimization_objectives: tuple[str, ...] = field(
        default_factory=tuple
    )

    sensitivity_summary: Optional[str] = None

    confidence: Optional[float] = None

    reason: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError(
                "Decision.id cannot be empty"
            )

        if self.status not in VALID_DECISION_STATUSES:
            raise ValueError(
                "status must be RECOMMENDED, NO_SAFE_ACTION, "
                "INSUFFICIENT_EVIDENCE, or NO_ACTIONABLE_DIFFERENCE"
            )

        if self.recommended_candidate_id is not None:
            if not self.recommended_candidate_id.strip():
                raise ValueError(
                    "recommended_candidate_id cannot be empty"
                )

        for candidate_id in self.alternative_candidate_ids:
            if not candidate_id.strip():
                raise ValueError(
                    "alternative_candidate_ids cannot contain empty IDs"
                )

        for candidate_id in self.rejected_candidate_ids:
            if not candidate_id.strip():
                raise ValueError(
                    "rejected_candidate_ids cannot contain empty IDs"
                )

        for candidate_id, rejection_reason in self.rejection_reasons.items():
            if not candidate_id.strip():
                raise ValueError(
                    "rejection_reasons cannot contain an empty candidate ID"
                )

            if not rejection_reason.strip():
                raise ValueError(
                    "rejection_reasons cannot contain an empty reason"
                )

        for candidate_id in self.pareto_candidate_ids:
            if not candidate_id.strip():
                raise ValueError(
                    "pareto_candidate_ids cannot contain empty IDs"
                )

        if self.confidence is not None:
            if not 0.0 <= self.confidence <= 1.0:
                raise ValueError(
                    "confidence must be between 0.0 and 1.0"
                )
