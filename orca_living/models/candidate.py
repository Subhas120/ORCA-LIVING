"""Canonical candidate-action contract for ORCA-LIVING.

A CandidateAction represents one feasible operational alternative
that ORCA may evaluate.

This module defines data contracts only. It does not determine
scientific safety or select the final recommendation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .objective import TimeWindow


@dataclass(frozen=True)
class CandidateLocation:
    """Geographic location associated with a candidate action."""

    latitude: float
    longitude: float
    name: Optional[str] = None

    def __post_init__(self) -> None:
        if not -90 <= self.latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")

        if not -180 <= self.longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")


@dataclass(frozen=True)
class CandidateAction:
    """Canonical representation of an operational alternative."""

    id: str
    action_type: str
    location: CandidateLocation

    route: Optional[Any] = None
    time_window: Optional[TimeWindow] = None

    expected_opportunity: Optional[float] = None
    distance: Optional[float] = None
    environmental_suitability: Optional[float] = None
    hazard_exposure: Optional[float] = None

    safety_status: str = "NOT_EVALUATED"

    uncertainty_refs: tuple[str, ...] = field(default_factory=tuple)

    robustness: Optional[str] = None

    objective_values: dict[str, float] = field(default_factory=dict)

    evidence_refs: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("CandidateAction.id cannot be empty")

        if not self.action_type.strip():
            raise ValueError(
                "CandidateAction.action_type cannot be empty"
            )

        if self.expected_opportunity is not None:
            if not 0.0 <= self.expected_opportunity <= 1.0:
                raise ValueError(
                    "expected_opportunity must be between 0.0 and 1.0"
                )

        if self.environmental_suitability is not None:
            if not 0.0 <= self.environmental_suitability <= 1.0:
                raise ValueError(
                    "environmental_suitability must be between 0.0 and 1.0"
                )

        if self.hazard_exposure is not None:
            if self.hazard_exposure < 0.0:
                raise ValueError(
                    "hazard_exposure cannot be negative"
                )

        if self.distance is not None and self.distance < 0.0:
            raise ValueError("distance cannot be negative")

        for name, value in self.objective_values.items():
            if not name.strip():
                raise ValueError(
                    "objective_values cannot contain an empty objective name"
                )
            if not isinstance(value, (int, float)):
                raise ValueError(
                    "objective_values must contain numeric values"
                )
