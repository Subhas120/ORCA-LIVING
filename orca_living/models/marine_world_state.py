"""Canonical Marine World State for ORCA-LIVING.

The MarineWorldState is the shared, versioned representation of the
decision-relevant marine environment and user context.

This module defines state contracts only. Scientific calculations,
safety rules, optimization, and LLM reasoning belong elsewhere.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from .evidence import Evidence
from .objective import UserObjective
from .uncertainty import Uncertainty


@dataclass(frozen=True)
class StateRegion:
    """Geographic region represented by the world state."""

    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    def __post_init__(self) -> None:
        if self.latitude is not None and not -90 <= self.latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")

        if self.longitude is not None and not -180 <= self.longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")

        if (
            self.name is None
            and self.latitude is None
            and self.longitude is None
        ):
            raise ValueError(
                "StateRegion requires a name or geographic coordinates"
            )


@dataclass(frozen=True)
class OceanState:
    """Decision-relevant ocean conditions.

    Scientific variables will be populated and validated by the
    marine-science subsystem.
    """

    variables: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WeatherState:
    """Decision-relevant meteorological conditions."""

    variables: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class HazardState:
    """Known hazards affecting the current decision context."""

    hazards: tuple[Any, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class GeospatialState:
    """Geographic constraints and spatial context."""

    features: tuple[Any, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class EcologicalState:
    """Decision-relevant ecological information."""

    variables: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class VesselState:
    """Operational characteristics of the vessel."""

    category: Optional[str] = None
    identifier: Optional[str] = None
    characteristics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DecisionState:
    """Current decision-processing status within the world state."""

    status: str = "NOT_EVALUATED"
    decision_id: Optional[str] = None


@dataclass(frozen=True)
class MarineWorldState:
    """Canonical versioned representation of ORCA's decision state."""

    state_id: str
    schema_version: str
    generated_at: datetime

    time: datetime
    region: StateRegion

    ocean_state: OceanState = field(default_factory=OceanState)
    weather_state: WeatherState = field(default_factory=WeatherState)
    hazard_state: HazardState = field(default_factory=HazardState)
    geospatial_state: GeospatialState = field(
        default_factory=GeospatialState
    )
    ecological_state: EcologicalState = field(
        default_factory=EcologicalState
    )
    vessel_state: VesselState = field(default_factory=VesselState)

    user_objective: Optional[UserObjective] = None

    constraints: tuple[Any, ...] = field(default_factory=tuple)

    evidence: tuple[Evidence, ...] = field(default_factory=tuple)

    uncertainties: tuple[Uncertainty, ...] = field(
        default_factory=tuple
    )

    candidate_actions: tuple[Any, ...] = field(
        default_factory=tuple
    )

    decision_state: DecisionState = field(
        default_factory=DecisionState
    )

    def __post_init__(self) -> None:
        if not self.state_id.strip():
            raise ValueError("state_id cannot be empty")

        if not self.schema_version.strip():
            raise ValueError("schema_version cannot be empty")
