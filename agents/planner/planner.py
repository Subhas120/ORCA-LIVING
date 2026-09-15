"""
ORCA Planner

Maps user intents to the specialized agents required to answer
or execute the request.
"""

INTENT_AGENT_MAP = {
    "SAFETY_CHECK": [
        "weather",
        "ocean",
        "alert",
        "gis",
        "risk",
    ],
    "FISHING_ZONE": [
        "ocean",
        "gis",
    ],
    "WEATHER": [
        "weather",
    ],
    "ROUTE": [
        "gis",
        "weather",
        "ocean",
        "risk",
    ],
    "MARINE_CONDITION": [
        "ocean",
    ],
    "ALERT": [
        "alert",
    ],
    "GENERAL_QUERY": [],
}


def create_plan(intent: str) -> dict:
    """
    Create an execution plan for a recognized ORCA intent.

    Returns a structured plan containing the intent, agents required,
    and whether the agents can be executed in parallel.
    """

    normalized_intent = intent.upper().strip()

    if normalized_intent not in INTENT_AGENT_MAP:
        raise ValueError(f"Unsupported intent: {intent}")

    agents = INTENT_AGENT_MAP[normalized_intent]

    return {
        "intent": normalized_intent,
        "agents": agents.copy(),
        "parallel": len(agents) > 1,
    }


def get_required_agents(intent: str) -> list:
    """Return the agents required for an intent."""

    return create_plan(intent)["agents"]


if __name__ == "__main__":
    print(create_plan("SAFETY_CHECK"))
