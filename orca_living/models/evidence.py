"""Canonical evidence contract for ORCA-LIVING.

Evidence represents an auditable observation or derived data point
used by the decision-intelligence system.

This module contains no LLM logic and no decision logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class EvidenceLocation:
    """Geographic location associated with an evidence item."""

    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not -90 <= self.latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")

        if not -180 <= self.longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")


@dataclass(frozen=True)
class EvidenceProvenance:
    """Information describing the origin and retrieval of evidence."""

    source_id: Optional[str] = None
    dataset: Optional[str] = None
    uri: Optional[str] = None
    retrieved_at: Optional[datetime] = None


@dataclass(frozen=True)
class Evidence:
    """Canonical, traceable evidence object.

    Every important numerical input used by ORCA should be represented
    through this contract so that decisions can be traced back to their
    underlying sources.
    """

    id: str
    source: str
    source_type: str
    variable: str
    value: float
    unit: str
    timestamp: datetime

    location: Optional[EvidenceLocation] = None

    spatial_resolution: Optional[str] = None
    temporal_resolution: Optional[str] = None

    quality: Optional[str] = None
    freshness: Optional[str] = None

    confidence: Optional[float] = None

    provenance: Optional[EvidenceProvenance] = None

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("Evidence.id cannot be empty")

        if not self.source.strip():
            raise ValueError("Evidence.source cannot be empty")

        if not self.source_type.strip():
            raise ValueError("Evidence.source_type cannot be empty")

        if not self.variable.strip():
            raise ValueError("Evidence.variable cannot be empty")

        if not self.unit.strip():
            raise ValueError("Evidence.unit cannot be empty")

        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
