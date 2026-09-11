"""Candidate generation engine for ORCA-LIVING.

The candidate generator transforms candidate proposals into canonical
CandidateAction objects.

It proposes operational alternatives only.

It does NOT:
- evaluate scientific safety
- select the best candidate
- calculate final risk
- perform optimization
- override M2 safety decisions
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from orca_living.models.candidate import (
    CandidateAction,
    CandidateLocation,
)
from orca_living.models.marine_world_state import MarineWorldState
from orca_living.models.objective import TimeWindow


@dataclass(frozen=True)
class CandidateProposal:
    """Input proposal from a scientific, demo, or external source."""

    id: str
    action_type: str
    latitude: float
    longitude: float

    name: Optional[str] = None

    route: Optional[Any] = None
    time_window: Optional[TimeWindow] = None

    expected_opportunity: Optional[float] = None
    distance: Optional[float] = None
    environmental_suitability: Optional[float] = None
    hazard_exposure: Optional[float] = None

    objective_values: dict[str, float] = field(
        default_factory=dict
    )

    evidence_refs: tuple[str, ...] = field(
        default_factory=tuple
    )

    uncertainty_refs: tuple[str, ...] = field(
        default_factory=tuple
    )

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError(
                "CandidateProposal.id cannot be empty"
            )

        if not self.action_type.strip():
            raise ValueError(
                "CandidateProposal.action_type cannot be empty"
            )

        if not -90 <= self.latitude <= 90:
            raise ValueError(
                "latitude must be between -90 and 90"
            )

        if not -180 <= self.longitude <= 180:
            raise ValueError(
                "longitude must be between -180 and 180"
            )


class CandidateGenerator:
    """Deterministic transformation from proposals to candidates."""

    def generate(
        self,
        world_state: MarineWorldState,
        proposals: tuple[CandidateProposal, ...],
    ) -> tuple[CandidateAction, ...]:
        """Generate canonical candidates from validated proposals.

        The world state provides the decision context. Scientific
        safety evaluation is intentionally outside this engine.
        """

        if not proposals:
            return ()

        candidates: list[CandidateAction] = []

        for proposal in proposals:
            candidate = CandidateAction(
                id=proposal.id,
                action_type=proposal.action_type,
                location=CandidateLocation(
                    latitude=proposal.latitude,
                    longitude=proposal.longitude,
                    name=proposal.name,
                ),
                route=proposal.route,
                time_window=proposal.time_window,
                expected_opportunity=proposal.expected_opportunity,
                distance=proposal.distance,
                environmental_suitability=(
                    proposal.environmental_suitability
                ),
                hazard_exposure=proposal.hazard_exposure,
                uncertainty_refs=proposal.uncertainty_refs,
                objective_values=proposal.objective_values,
                evidence_refs=proposal.evidence_refs,
            )

            candidates.append(candidate)

        return tuple(candidates)
