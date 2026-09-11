"""Canonical uncertainty contract for ORCA-LIVING."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Uncertainty:
    """Represents uncertainty associated with a decision-relevant variable."""

    id: str
    variable: str
    level: str

    confidence: Optional[float] = None
    reason: Optional[str] = None

    evidence_refs: tuple[str, ...] = field(default_factory=tuple)

    decision_impact: Optional[str] = None
    resolvable: Optional[bool] = None

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Uncertainty.id cannot be empty")

        if not self.variable.strip():
            raise ValueError("Uncertainty.variable cannot be empty")

        if not self.level.strip():
            raise ValueError("Uncertainty.level cannot be empty")

        if (
            self.confidence is not None
            and not 0.0 <= self.confidence <= 1.0
        ):
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )
