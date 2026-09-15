"""End-to-end M1 Decision Intelligence pipeline."""

from __future__ import annotations

from dataclasses import dataclass

from orca_living.engines.candidate_generator import CandidateGenerator
from orca_living.engines.decision_engine import DecisionEngine
from orca_living.engines.decision_intelligence import (
    DecisionIntelligenceAssembler,
)
from orca_living.engines.explanation_engine import ExplanationEngine
from orca_living.models.candidate import CandidateAction
from orca_living.models.marine_world_state import MarineWorldState
from orca_living.models.objective import UserObjective
from orca_living.models.safety import SafetyEvaluation


@dataclass(frozen=True)
class DecisionPipelineInput:
    """Inputs required to execute the M1 decision pipeline."""

    world_state: MarineWorldState
    proposals: tuple
    safety_evaluations: tuple[SafetyEvaluation, ...]
    objective: UserObjective
    decision_id: str


class DecisionIntelligencePipeline:
    """Coordinates the deterministic M1 decision flow."""

    def __init__(
        self,
        candidate_generator: CandidateGenerator | None = None,
        decision_engine: DecisionEngine | None = None,
        explanation_engine: ExplanationEngine | None = None,
        assembler: DecisionIntelligenceAssembler | None = None,
    ) -> None:
        self.candidate_generator = (
            candidate_generator
            if candidate_generator is not None
            else CandidateGenerator()
        )

        self.decision_engine = (
            decision_engine
            if decision_engine is not None
            else DecisionEngine()
        )

        self.explanation_engine = (
            explanation_engine
            if explanation_engine is not None
            else ExplanationEngine()
        )

        self.assembler = (
            assembler
            if assembler is not None
            else DecisionIntelligenceAssembler()
        )

    def generate_candidates(
        self,
        world_state: MarineWorldState,
        proposals: tuple,
    ) -> tuple[CandidateAction, ...]:
        """Transform validated proposals into canonical candidates."""

        return self.candidate_generator.generate(
            world_state=world_state,
            proposals=proposals,
        )

    def decide(
        self,
        candidates: tuple[CandidateAction, ...],
        safety_evaluations: tuple[SafetyEvaluation, ...],
        objective: UserObjective,
        decision_id: str,
    ):
        """Run safety, dominance, and optimization."""

        return self.decision_engine.decide(
            candidates=candidates,
            evaluations=safety_evaluations,
            objective=objective,
            decision_id=decision_id,
        )

    def run(
        self,
        pipeline_input: DecisionPipelineInput,
    ):
        """Execute candidate generation through final explanation."""

        if not pipeline_input.decision_id.strip():
            raise ValueError("decision_id cannot be empty.")

        candidates = self.generate_candidates(
            world_state=pipeline_input.world_state,
            proposals=pipeline_input.proposals,
        )

        decision = self.decide(
            candidates=candidates,
            safety_evaluations=pipeline_input.safety_evaluations,
            objective=pipeline_input.objective,
            decision_id=pipeline_input.decision_id,
        )

        candidate_ids = tuple(
            candidate.id
            for candidate in candidates
        )

        rejected_ids = set(
            decision.rejected_candidate_ids
        )

        safe_candidate_ids = tuple(
            candidate.id
            for candidate in candidates
            if candidate.id not in rejected_ids
        )

        trace = self.explanation_engine.build_trace(
            decision=decision,
            candidate_ids=candidate_ids,
            safe_candidate_ids=safe_candidate_ids,
            optimization_objectives=decision.optimization_objectives,
        )

        explanation = self.explanation_engine.build_explanation(
            trace=trace,
            decision=decision,
        )

        return self.assembler.assemble(
            decision,
            decision_trace=trace,
            explanation=explanation,
        )
