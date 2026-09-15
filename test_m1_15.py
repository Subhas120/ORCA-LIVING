from orca_living.engines.sensitivity import (
    SensitivityAnalyzer,
    SensitivityScenario,
)
from orca_living.models.decision import Decision


def make_decision(
    decision_id: str,
    candidate_id: str | None,
) -> Decision:
    return Decision(
        id=decision_id,
        status=(
            "RECOMMENDED"
            if candidate_id is not None
            else "NO_SAFE_ACTION"
        ),
        recommended_candidate_id=candidate_id,
        alternative_candidate_ids=(),
        rejected_candidate_ids=(),
        rejection_reasons={},
        pareto_candidate_ids=(
            (candidate_id,)
            if candidate_id is not None
            else ()
        ),
        tradeoffs=(),
        evidence_refs=(),
        uncertainty_refs=(),
        sensitivity_summary=None,
        confidence=None,
        reason=None,
    )


baseline = make_decision(
    "decision_baseline",
    "candidate_A",
)

scenarios = (
    SensitivityScenario(
        scenario_id="wind_plus_10",
        variable="wind_speed",
        decision=make_decision(
            "decision_wind_10",
            "candidate_A",
        ),
    ),
    SensitivityScenario(
        scenario_id="wind_plus_20",
        variable="wind_speed",
        decision=make_decision(
            "decision_wind_20",
            "candidate_B",
        ),
    ),
    SensitivityScenario(
        scenario_id="wave_plus_10",
        variable="wave_height",
        decision=make_decision(
            "decision_wave_10",
            "candidate_A",
        ),
    ),
)


analyzer = SensitivityAnalyzer()

result = analyzer.analyze(
    baseline_decision=baseline,
    scenarios=scenarios,
)


print("M1-15 SENSITIVITY ANALYSIS COMPLETE")
print()
print("BASELINE:", result.baseline_decision_id)
print(
    "SENSITIVE VARIABLES:",
    result.sensitive_variables,
)
print(
    "INSENSITIVE VARIABLES:",
    result.insensitive_variables,
)
print("EXPLANATION:", result.explanation)
print()

for variable in result.variables:
    print(
        variable.variable,
        "| tested =",
        variable.scenarios_tested,
        "| changed =",
        variable.changed_scenario_ids,
        "| sensitive =",
        variable.materially_affects_decision,
    )


assert result.baseline_decision_id == "decision_baseline"

assert result.sensitive_variables == (
    "wind_speed",
)

assert result.insensitive_variables == (
    "wave_height",
)

wind_result = result.variables[0]

assert wind_result.changed_scenario_ids == (
    "wind_plus_20",
)

assert wind_result.materially_affects_decision is True

wave_result = result.variables[1]

assert wave_result.changed_scenario_ids == ()

assert wave_result.materially_affects_decision is False

print()
print("M1-15 TEST PASSED")
