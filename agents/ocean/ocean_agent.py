import json
import os
from datetime import datetime

from agents.common.agent_contract import AgentRequest, AgentResponse
from agents.ocean.safety import assess_marine_safety
from agents.ocean.recommendation import get_pfz_recommendation
from agents.ocean.uncertainty import assess_uncertainty
from agents.ocean.models.evidence import Evidence


REQUIRED_FIELDS = [
    "parameter",
    "value",
    "unit",
    "latitude",
    "longitude",
    "timestamp",
    "source",
    "confidence",
]


def normalize_observation(observation: dict) -> dict:
    """Convert a marine observation to ORCA's standard format."""
    return {
        "parameter": observation["parameter"],
        "value": observation["value"],
        "unit": observation["unit"],
        "latitude": observation["latitude"],
        "longitude": observation["longitude"],
        "timestamp": observation["timestamp"],
        "source": observation["source"],
        "confidence": observation["confidence"],
    }


def validate_observation(observation: dict) -> bool:
    """Return False when required observation fields are missing."""

    for field in REQUIRED_FIELDS:

        if field not in observation:
            return False

        if observation[field] is None:
            return False

    return True


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

    Accepts M1's AgentRequest and returns the
    shared AgentResponse contract.
    """

    try:
        marine_data = get_marine_data()
        pfz_data = get_pfz_data()

        if not marine_data:

            return AgentResponse(
                agent="ocean",
                status="unavailable",
                data={},
                source="Sample Marine Dataset",
                timestamp=datetime.now().isoformat(),
                location=request.location,
                confidence=0.0,
                error="No valid marine observations available",
            )

        wave_height = get_parameter_value(
            marine_data,
            "wave_height",
        )

        current_speed = get_parameter_value(
            marine_data,
            "ocean_current",
        )

        marine_safety = assess_marine_safety(
            wave_height,
            current_speed,
        )

        pfz_recommendation = get_pfz_recommendation(
            pfz_data
        )

        evidence = build_evidence(
            marine_data
        )

        confidence_values = [
            observation["confidence"]
            for observation in marine_data
        ]

        confidence = min(confidence_values)

        uncertainty = assess_uncertainty(
            confidence
        )

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
            source=", ".join(sources),
            timestamp=datetime.now().isoformat(),
            location=request.location,
            confidence=confidence,
        )

    except FileNotFoundError as exc:

        return AgentResponse(
            agent="ocean",
            status="unavailable",
            data={},
            timestamp=datetime.now().isoformat(),
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
            timestamp=datetime.now().isoformat(),
            location=request.location,
            confidence=0.0,
            error=f"Invalid marine data: {exc}",
        )

    except Exception as exc:

        return AgentResponse(
            agent="ocean",
            status="error",
            data={},
            timestamp=datetime.now().isoformat(),
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
    )

    response = handle_ocean(request)

    print("\nORCA OCEAN AGENT")
    print("----------------")
    print("Agent:", response.agent)
    print("Status:", response.status)
    print("Location:", response.location)
    print("Confidence:", response.confidence)
    print("Source:", response.source)
    print("Data:", response.data)

    if response.error:
        print("Error:", response.error)