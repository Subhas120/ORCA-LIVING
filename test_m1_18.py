from datetime import datetime, timezone

from orca_living.engines.candidate_generator import CandidateProposal
from orca_living.engines.decision_pipeline import (
    DecisionIntelligencePipeline,
    DecisionPipelineInput,
)
from orca_living.models.marine_world_state import (
    MarineWorldState,
    StateRegion,
)
from orca_living.models.objective import UserObjective
from orca_living.models.safety import SafetyEvaluation


objective = UserObjective(
    operation="fishing",
    primary_objective="opportunity",
    original_query=(
        "Find the best fishing opportunity tomorrow morning. "
        "Safety first."
    ),
)


now = datetime.now(timezone.utc)


world_state = MarineWorldState(
    state_id="demo_state_001",
    schema_version="1.0",
    generated_at=now,
    time=now,
    region=StateRegion(
        name="Demo Marine Region",
        latitude=10.0,
        longitude=75.0,
    ),
    user_objective=objective,
)


proposals = (
    CandidateProposal(
        id="candidate_A",
        action_type="fishing",
        latitude=10.0,
        longitude=75.0,
        expected_opportunity=0.90,
        distance=10.0,
        environmental_suitability=0.85,
        hazard_exposure=0.20,
        objective_values={
            "opportunity": 0.90,
            "distance": 10.0,
            "uncertainty": 0.20,
        },
        evidence_refs=("evidence_A",),
        uncertainty_refs=("uncertainty_A",),
    ),
    CandidateProposal(
        id="candidate_B",
        action_type="fishing",
        latitude=10.1,
        longitude=75.1,
        expected_opportunity=0.95,
        distance=8.0,
        environmental_suitability=0.90,
        hazard_exposure=0.90,
        objective_values={
            "opportunity": 0.95,
            "distance": 8.0,
            "uncertainty": 0.20,
        },
        evidence_refs=("evidence_B",),
        uncertainty_refs=("uncertainty_B",),
    ),
    CandidateProposal(
        id="candidate_C",
        action_type="fishing",
        latitude=10.2,
        longitude=75.2,
        expected_opportunity=0.75,
        distance=15.0,
        environmental_suitability=0.80,
        hazard_exposure=0.15,
        objective_values={
            "opportunity": 0.75,
            "distance": 15.0,
            "uncertainty": 0.15,
        },
        evidence_refs=("evidence_C",),
        uncertainty_refs=("uncertainty_C",),
    ),
)


safety_evaluations = (
    SafetyEvaluation(
        candidate_id="candidate_A",
        status="SAFE",
        reason="Candidate satisfies all supplied safety constraints.",
        evidence_refs=("evidence_A",),
    ),
    SafetyEvaluation(
        candidate_id="candidate_B",
        status="UNSAFE",
        reason="Hazard exposure exceeds the permitted safety threshold.",
        evidence_refs=("evidence_B",),
    ),
    SafetyEvaluation(
        candidate_id="candidate_C",
        status="SAFE",
        reason="Candidate satisfies all supplied safety constraints.",
        evidence_refs=("evidence_C",),
    ),
)


pipeline = DecisionIntelligencePipeline()


result = pipeline.run(
    DecisionPipelineInput(
        world_state=world_state,
        proposals=proposals,
        safety_evaluations=safety_evaluations,
        objective=objective,
        decision_id="pipeline_decision_001",
    )
)


print("M1-18 END-TO-END PIPELINE COMPLETE")
print()
print("STATUS:", result.status)
print("RECOMMENDED:", result.recommended_candidate_id)
print("ALTERNATIVES:", result.alternative_candidate_ids)
print("REJECTED:", result.rejected_candidate_ids)
print("PARETO:", result.pareto_candidate_ids)
print("EVIDENCE:", result.evidence_refs)
print("UNCERTAINTY:", result.uncertainty_refs)
print("SUMMARY:", result.summary)
print()


assert result.decision_id == "pipeline_decision_001"
assert result.status == "RECOMMENDED"
assert result.recommended_candidate_id is not None

assert "candidate_B" in result.rejected_candidate_ids

assert result.recommended_candidate_id != "candidate_B"

assert result.decision_trace is not None
assert result.explanation is not None

print("M1-18 TEST PASSED")
