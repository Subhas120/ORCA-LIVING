"""Safety firewall for ORCA-LIVING.

The safety firewall enforces the architectural invariant that only
candidates explicitly classified as SAFE can reach downstream
decision optimization.

M1 does not calculate scientific safety here.
M2 supplies the SafetyEvaluation results.

UNSAFE and INSUFFICIENT_EVIDENCE candidates are removed from the
optimization set and cannot be resurrected downstream.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from orca_living.models.candidate import CandidateAction
from orca_living.models.safety import SafetyEvaluation


@dataclass(frozen=True)
class SafetyFilterResult:
    """Result of applying the safety firewall."""

    safe_candidates: tuple[CandidateAction, ...]
    rejected_candidates: tuple[CandidateAction, ...]
    evaluations: tuple[SafetyEvaluation, ...]


class SafetyFirewall:
    """Deterministic safety boundary before optimization."""

    def filter(
        self,
        candidates: tuple[CandidateAction, ...],
        evaluations: tuple[SafetyEvaluation, ...],
    ) -> SafetyFilterResult:
        """Allow only explicitly SAFE candidates downstream."""

        evaluation_by_candidate: Mapping[str, SafetyEvaluation] = {
            evaluation.candidate_id: evaluation
            for evaluation in evaluations
        }

        safe: list[CandidateAction] = []
        rejected: list[CandidateAction] = []

        for candidate in candidates:
            evaluation = evaluation_by_candidate.get(candidate.id)

            if evaluation is None:
                rejected.append(candidate)
                continue

            if evaluation.status == "SAFE":
                safe.append(candidate)
            else:
                rejected.append(candidate)

        return SafetyFilterResult(
            safe_candidates=tuple(safe),
            rejected_candidates=tuple(rejected),
            evaluations=evaluations,
        )
