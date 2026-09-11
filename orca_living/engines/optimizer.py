"""Multi-objective optimizer for ORCA-LIVING.

The optimizer operates only on candidates that have already passed
the safety firewall and dominance filtering.

It uses explicit objective priorities rather than hidden arbitrary
weights.

This module does not evaluate scientific safety.
"""

from __future__ import annotations

from dataclasses import dataclass

from orca_living.models.candidate import CandidateAction
from orca_living.models.objective import UserObjective


@dataclass(frozen=True)
class OptimizationResult:
    """Result of transparent multi-objective candidate selection."""

    preferred_candidate: CandidateAction

    frontier_candidates: tuple[CandidateAction, ...]

    comparison_order: tuple[str, ...]


class MultiObjectiveOptimizer:
    """Transparent preference-based optimizer."""

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

        available_objectives = tuple(
            name
            for name in objective_order
            if all(
                name in candidate.objective_values
                for candidate in candidates
            )
        )

        if not available_objectives:
            raise ValueError(
                "no common objective values available for optimization"
            )

        remaining = list(candidates)

        for objective_name in available_objectives:
            if len(remaining) <= 1:
                break

            values = [
                candidate.objective_values[objective_name]
                for candidate in remaining
            ]

            if objective_name in {
                "distance",
                "uncertainty",
                "hazard_exposure",
            }:
                best_value = min(values)
            else:
                best_value = max(values)

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
