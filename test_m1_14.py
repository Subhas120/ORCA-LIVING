from orca_living.engines.explanation_engine import ExplanationEngine
from orca_living.models.decision import Decision, DecisionTradeoff


decision = Decision(
    id="decision_001",
    status="RECOMMENDED",
    recommended_candidate_id="candidate_A",
    alternative_candidate_ids=("candidate_C",),
    rejected_candidate_ids=("candidate_B",),
    rejection_reasons={
        "candidate_B": "wind constraint failed",
    },
    pareto_candidate_ids=(
        "candidate_A",
        "candidate_C",
    ),
    tradeoffs=(
        DecisionTradeoff(
            objective_a="opportunity",
            objective_b="distance",
            relationship="trades against",
            candidate_a="candidate_A",
            candidate_b="candidate_C",
        ),
    ),
    evidence_refs=(
        "evidence_wind_001",
        "evidence_wave_001",
    ),
    uncertainty_refs=(
        "uncertainty_wave_001",
    ),
    sensitivity_summary="wind materially affects the decision",
    confidence=0.82,
    reason="Candidate A provides the preferred safe tradeoff.",
)


engine = ExplanationEngine()

trace = engine.build_trace(
    decision=decision,
    candidate_ids=(
        "candidate_A",
        "candidate_B",
        "candidate_C",
    ),
    safe_candidate_ids=(
        "candidate_A",
        "candidate_C",
    ),
    optimization_objectives=(
        "opportunity",
        "distance",
        "uncertainty",
    ),
)

explanation = engine.build_explanation(
    trace=trace,
    decision=decision,
)

print("M1-14 DECISION TRACE COMPLETE")
print()
print("DECISION:", trace.decision_id)
print("RECOMMENDED:", trace.recommended_candidate_id)
print("SAFE:", trace.safe_candidate_ids)
print("REJECTED:", trace.rejected_candidate_ids)
print("PARETO:", trace.pareto_candidate_ids)
print("OBJECTIVES:", trace.optimization_objectives)
print("EVIDENCE:", trace.evidence_refs)
print("UNCERTAINTY:", trace.uncertainty_refs)
print()
print("EXPLANATION")
print("SUMMARY:", explanation.summary)
print("SAFETY:", explanation.safety_reason)
print("PREFERENCE:", explanation.preference_reason)
print("TRADEOFFS:", explanation.tradeoffs)
print("REJECTED:", explanation.rejected_candidates)
print("EVIDENCE:", explanation.evidence_refs)
print("UNCERTAINTY:", explanation.uncertainty_refs)

assert trace.decision_id == "decision_001"
assert trace.recommended_candidate_id == "candidate_A"
assert trace.safe_candidate_ids == (
    "candidate_A",
    "candidate_C",
)
assert trace.rejected_candidate_ids == (
    "candidate_B",
)
assert trace.pareto_candidate_ids == (
    "candidate_A",
    "candidate_C",
)
assert trace.evidence_refs == (
    "evidence_wind_001",
    "evidence_wave_001",
)
assert explanation.decision_id == decision.id
assert "candidate_A" in explanation.summary
assert explanation.rejected_candidates == (
    "candidate_B",
)

print()
print("M1-14 TEST PASSED")
