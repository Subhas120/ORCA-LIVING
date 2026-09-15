from orca_living.engines.value_of_information import (
    InformationScenario,
    ValueOfInformationAnalyzer,
)
from orca_living.models.decision import Decision


baseline = Decision(
    id="decision_baseline",
    status="RECOMMENDED",
    recommended_candidate_id="candidate_A",
)


wind_plus_10 = Decision(
    id="decision_wind_10",
    status="RECOMMENDED",
    recommended_candidate_id="candidate_A",
)


wind_plus_20 = Decision(
    id="decision_wind_20",
    status="RECOMMENDED",
    recommended_candidate_id="candidate_B",
)


wave_plus_10 = Decision(
    id="decision_wave_10",
    status="RECOMMENDED",
    recommended_candidate_id="candidate_A",
)


scenarios = (
    InformationScenario(
        scenario_id="wind_plus_10",
        variable="wind_speed",
        decision=wind_plus_10,
    ),
    InformationScenario(
        scenario_id="wind_plus_20",
        variable="wind_speed",
        decision=wind_plus_20,
    ),
    InformationScenario(
        scenario_id="wave_plus_10",
        variable="wave_height",
        decision=wave_plus_10,
    ),
)


analyzer = ValueOfInformationAnalyzer()

result = analyzer.analyze(
    baseline_decision=baseline,
    uncertain_variables=(
        ("wind_speed", ("uncertainty_wind_001",)),
        ("wave_height", ("uncertainty_wave_001",)),
    ),
    scenarios=scenarios,
)


print("M1-16 VALUE OF INFORMATION COMPLETE")
print()
print("BASELINE:", result.baseline_decision_id)
print("HIGH VALUE INFORMATION:", result.high_value_information)
print("MEDIUM VALUE INFORMATION:", result.medium_value_information)
print("LOW VALUE INFORMATION:", result.low_value_information)
print("EXPLANATION:", result.explanation)
print()

for request in result.information_requests:
    print(
        request.variable,
        "| priority =", request.priority,
        "| scenarios =", request.scenario_ids,
        "| uncertainty =", request.current_uncertainty_refs,
    )

assert result.baseline_decision_id == "decision_baseline"

assert result.high_value_information == ("wind_speed",)
assert result.medium_value_information == ()
assert result.low_value_information == ("wave_height",)

wind_request = result.information_requests[0]
wave_request = result.information_requests[1]

assert wind_request.priority == "HIGH"
assert wave_request.priority == "LOW"

assert wind_request.scenario_ids == (
    "wind_plus_10",
    "wind_plus_20",
)

assert wind_request.current_uncertainty_refs == (
    "uncertainty_wind_001",
)

assert wave_request.scenario_ids == ("wave_plus_10",)

print()
print("M1-16 TEST PASSED")
