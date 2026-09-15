"""Decision trace and explanation contracts for ORCA-LIVING.

DecisionTrace represents machine/audit lineage.
DecisionExplanation represents deterministic human-readable reasoning.

These models do not calculate scientific facts and do not select
or modify decisions.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DecisionTrace:
    """Machine-readable lineage for a completed decision."""

    decision_id: str

    candidate_ids: tuple[str, ...] = field(default_factory=tuple)

    recommended_candidate_id: str | None = None

    safe_candidate_ids: tuple[str, ...] = field(default_factory=tuple)

    rejected_candidate_ids: tuple[str, ...] = field(default_factory=tuple)

    rejection_reasons: dict[str, str] = field(default_factory=dict)

    pareto_candidate_ids: tuple[str, ...] = field(default_factory=tuple)

    tradeoffs: tuple[str, ...] = field(default_factory=tuple)

    optimization_objectives: tuple[str, ...] = field(
        default_factory=tuple
    )

    evidence_refs: tuple[str, ...] = field(default_factory=tuple)

    uncertainty_refs: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.decision_id.strip():
            raise ValueError("decision_id cannot be empty")

        if self.recommended_candidate_id is not None:
            if not self.recommended_candidate_id.strip():
                raise ValueError(
                    "recommended_candidate_id cannot be empty"
                )

        for candidate_id in self.candidate_ids:
            if not candidate_id.strip():
                raise ValueError(
                    "candidate_ids cannot contain empty values"
                )

        for candidate_id in self.safe_candidate_ids:
            if not candidate_id.strip():
                raise ValueError(
                    "safe_candidate_ids cannot contain empty values"
                )

        for candidate_id in self.rejected_candidate_ids:
            if not candidate_id.strip():
                raise ValueError(
                    "rejected_candidate_ids cannot contain empty values"
                )

        for candidate_id, reason in self.rejection_reasons.items():
            if not candidate_id.strip():
                raise ValueError(
                    "rejection_reasons cannot contain empty candidate ids"
                )

            if not reason.strip():
                raise ValueError(
                    "rejection reason cannot be empty"
                )

        for candidate_id in self.pareto_candidate_ids:
            if not candidate_id.strip():
                raise ValueError(
                    "pareto_candidate_ids cannot contain empty values"
                )

        for objective in self.optimization_objectives:
            if not objective.strip():
                raise ValueError(
                    "optimization_objectives cannot contain empty values"
                )

        for evidence_ref in self.evidence_refs:
            if not evidence_ref.strip():
                raise ValueError(
                    "evidence_refs cannot contain empty values"
                )

        for uncertainty_ref in self.uncertainty_refs:
            if not uncertainty_ref.strip():
                raise ValueError(
                    "uncertainty_refs cannot contain empty values"
                )


@dataclass(frozen=True)
class DecisionExplanation:
    """Deterministic human-readable explanation of a decision."""

    decision_id: str

    summary: str

    safety_reason: str

    preference_reason: str

    tradeoffs: tuple[str, ...] = field(default_factory=tuple)

    rejected_candidates: tuple[str, ...] = field(
        default_factory=tuple
    )

    evidence_refs: tuple[str, ...] = field(default_factory=tuple)

    uncertainty_refs: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.decision_id.strip():
            raise ValueError("decision_id cannot be empty")

        if not self.summary.strip():
            raise ValueError("summary cannot be empty")

        if not self.safety_reason.strip():
            raise ValueError("safety_reason cannot be empty")

        if not self.preference_reason.strip():
            raise ValueError(
                "preference_reason cannot be empty"
            )

        for candidate_id in self.rejected_candidates:
            if not candidate_id.strip():
                raise ValueError(
                    "rejected_candidates cannot contain empty values"
                )

        for evidence_ref in self.evidence_refs:
            if not evidence_ref.strip():
                raise ValueError(
                    "evidence_refs cannot contain empty values"
                )

        for uncertainty_ref in self.uncertainty_refs:
            if not uncertainty_ref.strip():
                raise ValueError(
                    "uncertainty_refs cannot contain empty values"
                )
