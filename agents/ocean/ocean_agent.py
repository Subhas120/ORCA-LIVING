import json
import os
from copy import deepcopy
from datetime import datetime

from agents.ocean.normalizer import normalize_observation
from agents.ocean.validator import validate_observation

from agents.common.agent_contract import AgentRequest, AgentResponse
from agents.ocean.safety import assess_marine_safety
from agents.ocean.recommendation import get_pfz_recommendation
from agents.ocean.uncertainty import assess_uncertainty
from agents.ocean.models.evidence import Evidence


DEFAULT_SCENARIO = "PFZ_KOCHI_DEMO"
UNSAFE_WEATHER_SCENARIO = "UNSAFE_WEATHER"
INSUFFICIENT_EVIDENCE_SCENARIO = "INSUFFICIENT_EVIDENCE"


def get_marine_data() -> list[dict]:
    """Load and validate prototype marine observations."""

    base_dir = os.path.dirname(os.path.abspath(__file__))

    data_path = os.path.join(
        base_dir,
        "../../data/sample/marine_data.json",
    )

    with open(data_path, "r", encoding="utf-8") as file:
        raw_data = json.load(file)

    marine_data = []

    for observation in raw_data:
        normalized = normalize_observation(observation)

        if validate_observation(normalized):
            marine_data.append(normalized)

    return marine_data


def get_pfz_data() -> list[dict]:
    """Load prototype Potential Fishing Zone data."""

    base_dir = os.path.dirname(os.path.abspath(__file__))

    data_path = os.path.join(
        base_dir,
        "../../data/sample/pfz_data.json",
    )

    with open(data_path, "r", encoding="utf-8") as file:
        return json.load(file)


def apply_demo_scenario(
    marine_data: list[dict],
    scenario_id: str | None,
) -> list[dict]:
    """
    Apply a deterministic demo scenario to M2 prototype data.

    Scenario selection belongs to M2. The actual marine safety
    decision continues to be performed by assess_marine_safety().
    """

    scenario = (
        scenario_id or DEFAULT_SCENARIO
    ).strip().upper()

    data = deepcopy(marine_data)

    if scenario in {
        DEFAULT_SCENARIO,
        "NORMAL",
    }:
        return data

    if scenario == UNSAFE_WEATHER_SCENARIO:

        for observation in data:

            if observation["parameter"] == "wave_height":
                observation["value"] = 3.5

            elif observation["parameter"] == "ocean_current":
                observation["value"] = 0.6

        return data

    if scenario == INSUFFICIENT_EVIDENCE_SCENARIO:

        for observation in data:

            if observation["parameter"] == "wave_height":
                observation["value"] = None

        return data

    # Unknown scenario:
    # preserve deterministic normal demo data rather than
    # inventing a marine state.
    return data


def get_parameter_value(
    marine_data: list[dict],
    parameter: str,
):
    """Get the value for a requested marine parameter."""

    for observation in marine_data:

        if observation["parameter"] == parameter:
            return observation["value"]

    return None


def build_evidence(
    marine_data: list[dict],
) -> dict:
    """Build evidence metadata for marine observations."""

    evidence = {}

    for observation in marine_data:

        item = Evidence(
            parameter=observation["parameter"],
            source=observation["source"],
            timestamp=observation["timestamp"],
            confidence=observation["confidence"],
        )

        evidence[observation["parameter"]] = item.to_dict()

    return evidence


def handle_ocean(request: AgentRequest) -> AgentResponse:
    """
    M2 Ocean Agent entry point.

    M2 owns:
    - marine observations
    - marine safety assessment
    - hazards
    - evidence
    - uncertainty
    """

    try:

        # ---------------------------------------------------------
        # 1. Load M2 prototype data
        # ---------------------------------------------------------
        marine_data = get_marine_data()
        pfz_data = get_pfz_data()

        if not marine_data:

            return AgentResponse(
                agent="ocean",
                status="unavailable",
                data={},
                location=request.location,
                confidence=0.0,
                error="No valid marine observations available",
            )

        # ---------------------------------------------------------
        # 2. Apply deterministic scenario inside M2
        # ---------------------------------------------------------
        marine_data = apply_demo_scenario(
            marine_data,
            request.scenario_id,
        )

        # ---------------------------------------------------------
        # 3. Read safety-critical marine values
        # ---------------------------------------------------------
        wave_height = get_parameter_value(
            marine_data,
            "wave_height",
        )

        current_speed = get_parameter_value(
            marine_data,
            "ocean_current",
        )

        # ---------------------------------------------------------
        # 4. M2 authoritative safety evaluation
        # ---------------------------------------------------------
        marine_safety = assess_marine_safety(
            wave_height,
            current_speed,
        )

        # ---------------------------------------------------------
        # 5. PFZ recommendation
        # ---------------------------------------------------------
        pfz_recommendation = get_pfz_recommendation(
            pfz_data
        )

        # ---------------------------------------------------------
        # 6. Evidence
        # ---------------------------------------------------------
        evidence = build_evidence(
            marine_data
        )

        # ---------------------------------------------------------
        # 7. Confidence / uncertainty
        # ---------------------------------------------------------
        confidence_values = [
            observation["confidence"]
            for observation in marine_data
            if observation.get("value") is not None
        ]

        confidence = (
            min(confidence_values)
            if confidence_values
            else 0.0
        )

        uncertainty = assess_uncertainty(
            confidence
        )

        # ---------------------------------------------------------
        # 8. Assemble M2 response
        # ---------------------------------------------------------
        data = {

            "sst": get_parameter_value(
                marine_data,
                "sea_surface_temperature",
            ),

            "chlorophyll": get_parameter_value(
                marine_data,
                "chlorophyll",
            ),

            "wave_height": wave_height,

            "wave_period": get_parameter_value(
                marine_data,
                "wave_period",
            ),

            "current_speed": current_speed,

            "marine_safety": marine_safety,

            "uncertainty": uncertainty,

            "pfz": pfz_data,

            "pfz_recommendation": pfz_recommendation,

            "evidence": evidence,
        }

        sources = sorted(
            {
                observation["source"]
                for observation in marine_data
            }
        )

        return AgentResponse(
            agent="ocean",
            status="success",
            data=data,
            location=request.location,
            confidence=confidence,
        )

    except FileNotFoundError as exc:

        return AgentResponse(
            agent="ocean",
            status="unavailable",
            data={},
            location=request.location,
            confidence=0.0,
            error=f"Marine data source unavailable: {exc}",
        )

    except (
        json.JSONDecodeError,
        KeyError,
        TypeError,
    ) as exc:

        return AgentResponse(
            agent="ocean",
            status="error",
            data={},
            location=request.location,
            confidence=0.0,
            error=f"Invalid marine data: {exc}",
        )

    except Exception as exc:

        return AgentResponse(
            agent="ocean",
            status="error",
            data={},
            location=request.location,
            confidence=0.0,
            error=str(exc),
        )


if __name__ == "__main__":

    request = AgentRequest(
        query="What are the marine conditions near Kochi?",
        location="Kochi",
        destination=None,
        date="tomorrow",
        time="morning",
        activity="fishing",
        scenario_id=DEFAULT_SCENARIO,
    )

    response = handle_ocean(request)

    print("\nORCA OCEAN AGENT")
    print("----------------")
    print("Agent:", response.agent)
    print("Status:", response.status)
    print("Location:", response.location)
    print("Confidence:", response.confidence)
    print("Source:", response.data)

    if response.error:
        print("Error:", response.error)