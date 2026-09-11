"""Multi-objective optimizer for ORCA-LIVING.

The optimizer operates only on candidates that have already passed
the safety firewall and dominance filtering.

Objective direction is explicitly declared through ObjectiveSpec.
No objective is implicitly assumed to be a maximize/minimize objective.

This module does not evaluate scientific safety.
"""

from __future__ import annotations

from dataclasses import dataclass

from orca_living.models.candidate import CandidateAction
from orca_living.models.objective import UserObjective
from orca_living.models.objective_spec import (
    ObjectiveConfiguration,
    ObjectiveSpec,
)


@dataclass(frozen=True)
class OptimizationResult:
    """Result of transparent multi-objective candidate selection."""

    preferred_candidate: CandidateAction

    frontier_candidates: tuple[CandidateAction, ...]

    comparison_order: tuple[str, ...]


class MultiObjectiveOptimizer:
    """Transparent preference-based optimizer."""

    DEFAULT_OBJECTIVES = ObjectiveConfiguration(
        objectives=(
            ObjectiveSpec(
                name="opportunity",
                direction="maximize",
                priority=0,
            ),
            ObjectiveSpec(
                name="distance",
                direction="minimize",
                priority=1,
            ),
            ObjectiveSpec(
                name="uncertainty",
                direction="minimize",
                priority=2,
            ),
            ObjectiveSpec(
                name="hazard_exposure",
                direction="minimize",
                priority=3,
            ),
            ObjectiveSpec(
                name="environmental_suitability",
                direction="maximize",
                priority=4,
            ),
        )
    )

    def __init__(
        self,
        objective_configuration: ObjectiveConfiguration | None = None,
    ) -> None:
        self.objective_configuration = (
            objective_configuration
            if objective_configuration is not None
            else self.DEFAULT_OBJECTIVES
        )

    def optimize(
        self,
        candidates: tuple[CandidateAction, ...],
        objective: UserObjective,
    ) -> OptimizationResult:
        """Select a preferred candidate from safe candidates."""

        if not candidates:
            raise ValueError(
                "cannot optimize an empty candidate set"
            )

        objective_order = objective.all_objectives

        available_objectives = []

        for name in objective_order:
            if not all(
                name in candidate.objective_values
                for candidate in candidates
            ):
                continue

            specification = self.objective_configuration.get(name)

            if specification is None:
                raise ValueError(
                    f"no objective specification exists for '{name}'"
                )

            available_objectives.append(name)

        available_objectives = tuple(available_objectives)

        if not available_objectives:
            raise ValueError(
                "no common objective values available for optimization"
            )

        remaining = list(candidates)

        for objective_name in available_objectives:
            if len(remaining) <= 1:
                break

            specification = self.objective_configuration.get(
                objective_name
            )

            if specification is None:
                raise ValueError(
                    f"no objective specification exists for "
                    f"'{objective_name}'"
                )

            values = [
                candidate.objective_values[objective_name]
                for candidate in remaining
            ]

            if specification.direction == "maximize":
                best_value = max(values)
            elif specification.direction == "minimize":
                best_value = min(values)
            else:
                raise ValueError(
                    f"unsupported objective direction: "
                    f"{specification.direction}"
                )

            remaining = [
                candidate
                for candidate in remaining
                if candidate.objective_values[objective_name]
                == best_value
            ]

        preferred = remaining[0]

        return OptimizationResult(
            preferred_candidate=preferred,
            frontier_candidates=candidates,
            comparison_order=available_objectives,
        )
