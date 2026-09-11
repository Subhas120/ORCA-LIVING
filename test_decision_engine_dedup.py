from orca_living.engines.decision_engine import DecisionEngine
from orca_living.models.candidate import CandidateAction, CandidateLocation
from orca_living.models.objective import UserObjective
from orca_living.models.safety import SafetyEvaluation


candidate = CandidateAction(
    id="candidate_unsafe",
    action_type="fishing",
    location=CandidateLocation(
        latitude=10.0,
        longitude=75.0,
    ),
    expected_opportunity=0.8,
    distance=10.0,
    environmental_suitability=0.7,
    hazard_exposure=0.9,
    safety_status="INSUFFICIENT_EVIDENCE",
    evidence_refs=("evidence_001",),
    uncertainty_refs=("uncertainty_wave_001",),
    objective_values={
        "opportunity": 0.8,
        "distance": 10.0,
        "uncertainty": 0.8,
    },
)


evaluation = SafetyEvaluation(
    candidate_id="candidate_unsafe",
    status="INSUFFICIENT_EVIDENCE",
    evidence_refs=(
        "evidence_001",
        "evidence_001",
    ),
    uncertainty_refs=(
        "uncertainty_wave_001",
        "uncertainty_wave_001",
    ),
    reason="Critical wave evidence is insufficient.",
)


objective = UserObjective(
    operation="fishing",
    primary_objective="maximize fishing opportunity",
    original_query="Find a safe fishing opportunity.",
)


decision = DecisionEngine().decide(
    candidates=(candidate,),
    evaluations=(evaluation,),
    objective=objective,
    decision_id="decision_dedup_test",
)


print("DEDUPLICATION REGRESSION TEST")
print("STATUS:", decision.status)
print("EVIDENCE:", decision.evidence_refs)
print("UNCERTAINTY:", decision.uncertainty_refs)


assert decision.status == "INSUFFICIENT_EVIDENCE"
assert decision.evidence_refs == ("evidence_001",)
assert decision.uncertainty_refs == ("uncertainty_wave_001",)


print("DEDUPLICATION TEST PASSED")
