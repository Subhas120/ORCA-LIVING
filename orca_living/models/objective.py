"""Canonical user objective contract for ORCA-LIVING.

This module contains data structures representing what the user wants
ORCA to accomplish. It contains no LLM logic and no decision logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class TimeWindow:
    """Time interval during which the requested operation is intended."""

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError("TimeWindow.end must be after TimeWindow.start")


@dataclass(frozen=True)
class GeographicRegion:
    """Geographic context associated with the user's objective."""

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    name: Optional[str] = None

    def __post_init__(self) -> None:
        if self.latitude is not None and not -90 <= self.latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")

        if self.longitude is not None and not -180 <= self.longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")

        if (
            self.latitude is None
            and self.longitude is None
            and not self.name
        ):
            raise ValueError(
                "GeographicRegion requires coordinates or a region name"
            )


@dataclass(frozen=True)
class VesselContext:
    """Vessel characteristics relevant to decision making."""

    category: str
    identifier: Optional[str] = None
    beam_m: Optional[float] = None
    length_m: Optional[float] = None

    def __post_init__(self) -> None:
        if not self.category.strip():
            raise ValueError("VesselContext.category cannot be empty")

        if self.beam_m is not None and self.beam_m <= 0:
            raise ValueError("beam_m must be positive")

        if self.length_m is not None and self.length_m <= 0:
            raise ValueError("length_m must be positive")


@dataclass(frozen=True)
class UserObjective:
    """Canonical representation of the user's operational objective.

    This object preserves the original natural-language request while
    providing structured information for deterministic downstream
    decision processing.
    """

    operation: str
    primary_objective: str
    original_query: str

    secondary_objectives: tuple[str, ...] = field(default_factory=tuple)
    time_window: Optional[TimeWindow] = None
    region: Optional[GeographicRegion] = None
    vessel: Optional[VesselContext] = None
    constraints: tuple[str, ...] = field(default_factory=tuple)
    preferences: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.operation.strip():
            raise ValueError("operation cannot be empty")

        if not self.primary_objective.strip():
            raise ValueError("primary_objective cannot be empty")

        if not self.original_query.strip():
            raise ValueError("original_query cannot be empty")

    @property
    def all_objectives(self) -> tuple[str, ...]:
        """Return objectives in priority order."""
        return (
            self.primary_objective,
            *self.secondary_objectives,
        )
