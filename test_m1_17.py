from orca_living.engines.decision_intelligence import (
    DecisionIntelligenceAssembler,
)
from orca_living.models.decision import Decision


class DummyTrace:
    name = "decision_trace"


class DummyExplanation:
    name = "decision_explanation"


class DummyRobustness:
    level = "MEDIUM"


class DummySensitivity:
    sensitive_variables = ("wind_speed",)


class DummyValueOfInformation:
    high_value_information = ("wind_speed",)


class DummyCounterfactual:
    scenario_id = "wind_plus_20"


baseline = Decision(
    id="decision_001",
    status="RECOMMENDED",
    recommended_candidate_id="candidate_A",
    alternative_candidate_ids=(
        "candidate_C",
    ),
    rejected_candidate_ids=(
        "candidate_B",
    ),
    rejection_reasons={
        "candidate_B": "Unsafe wave conditions.",
    },
    pareto_candidate_ids=(
        "candidate_A",
        "candidate_C",
    ),
    tradeoffs=(
        "candidate_A vs candidate_C: opportunity trades against distance",
    ),
    evidence_refs=(
        "evidence_wind_001",
        "evidence_wave_001",
    ),
    uncertainty_refs=(
        "uncertainty_wave_001",
    ),
    confidence=0.75,
    reason="Candidate A provides the preferred objective tradeoff.",
)


assembler = DecisionIntelligenceAssembler()

result = assembler.assemble(
    baseline,
    decision_trace=DummyTrace(),
    explanation=DummyExplanation(),
    robustness=DummyRobustness(),
    sensitivity=DummySensitivity(),
    value_of_information=DummyValueOfInformation(),
    counterfactuals=(
        DummyCounterfactual(),
    ),
)


print("M1-17 DECISION INTELLIGENCE INTEGRATION COMPLETE")
print()
print("DECISION:", result.decision_id)
print("STATUS:", result.status)
print("RECOMMENDED:", result.recommended_candidate_id)
print("ALTERNATIVES:", result.alternative_candidate_ids)
print("REJECTED:", result.rejected_candidate_ids)
print("PARETO:", result.pareto_candidate_ids)
print("TRADEOFFS:", result.tradeoffs)
print("EVIDENCE:", result.evidence_refs)
print("UNCERTAINTY:", result.uncertainty_refs)
print("ROBUSTNESS:", result.robustness.level)
print("SENSITIVITY:", result.sensitivity.sensitive_variables)
print("HIGH VOI:", result.value_of_information.high_value_information)
print(
    "COUNTERFACTUALS:",
    tuple(cf.scenario_id for cf in result.counterfactuals),
)
print("SUMMARY:", result.summary)
print()


assert result.decision_id == "decision_001"
assert result.status == "RECOMMENDED"

assert result.recommended_candidate_id == "candidate_A"

assert result.alternative_candidate_ids == (
    "candidate_C",
)

assert result.rejected_candidate_ids == (
    "candidate_B",
)

assert result.rejection_reasons == (
    "candidate_B: Unsafe wave conditions.",
)

assert result.pareto_candidate_ids == (
    "candidate_A",
    "candidate_C",
)

assert result.tradeoffs == (
    "candidate_A vs candidate_C: opportunity trades against distance",
)

assert result.evidence_refs == (
    "evidence_wind_001",
    "evidence_wave_001",
)

assert result.uncertainty_refs == (
    "uncertainty_wave_001",
)

assert result.robustness.level == "MEDIUM"

assert result.sensitivity.sensitive_variables == (
    "wind_speed",
)

assert result.value_of_information.high_value_information == (
    "wind_speed",
)

assert tuple(
    cf.scenario_id for cf in result.counterfactuals
) == (
    "wind_plus_20",
)

assert result.decision_trace is not None
assert result.explanation is not None

assert result.recommended_candidate_id not in (
    result.rejected_candidate_ids
)

print("M1-17 TEST PASSED")
