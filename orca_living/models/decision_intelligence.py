from dataclasses import dataclass
from typing import Any, Tuple


@dataclass(frozen=True)
class DecisionIntelligence:
    """
    Unified M1 decision-intelligence output.

    This model integrates outputs from the individual M1 reasoning
    components without recalculating or modifying their decisions.

    Scientific facts remain owned by M2.
    Safety remains authoritative.
    """

    decision_id: str
    status: str

    recommended_candidate_id: str | None

    alternative_candidate_ids: Tuple[str, ...] = ()
    rejected_candidate_ids: Tuple[str, ...] = ()
    rejection_reasons: Tuple[str, ...] = ()

    pareto_candidate_ids: Tuple[str, ...] = ()
    tradeoffs: Tuple[str, ...] = ()

    evidence_refs: Tuple[str, ...] = ()
    uncertainty_refs: Tuple[str, ...] = ()

    robustness: Any | None = None
    sensitivity: Any | None = None
    value_of_information: Any | None = None
    counterfactuals: Tuple[Any, ...] = ()

    explanation: Any | None = None
    decision_trace: Any | None = None

    confidence: str | None = None
    summary: str = ""

    def __post_init__(self) -> None:
        if not self.decision_id:
            raise ValueError("decision_id cannot be empty.")

        if not self.status:
            raise ValueError("status cannot be empty.")

        if self.recommended_candidate_id is not None:
            if self.recommended_candidate_id in self.rejected_candidate_ids:
                raise ValueError(
                    "Recommended candidate cannot also be rejected."
                )
