"""Dominance filtering for ORCA-LIVING.

The dominance filter removes safe candidates that are strictly
inferior to another safe candidate across all configured objectives.

Safety must already have been evaluated before this engine runs.

This module does not evaluate scientific safety and does not
select the final recommendation.
"""

from __future__ import annotations

from dataclasses import dataclass

from orca_living.models.candidate import CandidateAction


@dataclass(frozen=True)
class DominanceResult:
    """Result of Pareto dominance filtering."""

    non_dominated_candidates: tuple[CandidateAction, ...]

    dominated_candidates: tuple[CandidateAction, ...]

    domination_reasons: dict[str, str]


class DominanceFilter:
    """Deterministic multi-objective dominance filter."""

    def __init__(
        self,
        maximize: tuple[str, ...] = (
            "opportunity",
        ),
        minimize: tuple[str, ...] = (
            "distance",
            "uncertainty",
        ),
    ) -> None:
        self.maximize = maximize
        self.minimize = minimize

    def _dominates(
        self,
        first: CandidateAction,
        second: CandidateAction,
    ) -> bool:
        """Return True when first strictly dominates second."""

        first_values = first.objective_values
        second_values = second.objective_values

        objectives = self.maximize + self.minimize

        if not all(
            objective in first_values
            and objective in second_values
            for objective in objectives
        ):
            return False

        first_no_worse = True
        first_strictly_better = False

        for objective in self.maximize:
            first_value = first_values[objective]
            second_value = second_values[objective]

            if first_value < second_value:
                first_no_worse = False
                break

            if first_value > second_value:
                first_strictly_better = True

        if not first_no_worse:
            return False

        for objective in self.minimize:
            first_value = first_values[objective]
            second_value = second_values[objective]

            if first_value > second_value:
                first_no_worse = False
                break

            if first_value < second_value:
                first_strictly_better = True

        return first_no_worse and first_strictly_better

    def filter(
        self,
        candidates: tuple[CandidateAction, ...],
    ) -> DominanceResult:
        """Return non-dominated and dominated safe candidates."""

        dominated_ids: set[str] = set()
        domination_reasons: dict[str, str] = {}

        for candidate in candidates:
            for other in candidates:
                if candidate.id == other.id:
                    continue

                if self._dominates(other, candidate):
                    dominated_ids.add(candidate.id)

                    domination_reasons[candidate.id] = (
                        f"{other.id} dominates {candidate.id} "
                        "across the configured objectives."
                    )

                    break

        non_dominated = tuple(
            candidate
            for candidate in candidates
            if candidate.id not in dominated_ids
        )

        dominated = tuple(
            candidate
            for candidate in candidates
            if candidate.id in dominated_ids
        )

        return DominanceResult(
            non_dominated_candidates=non_dominated,
            dominated_candidates=dominated,
            domination_reasons=domination_reasons,
        )
