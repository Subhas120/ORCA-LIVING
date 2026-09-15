"""
ORCA Query Validation

Validates whether an ORCA query contains enough information
to proceed with the planned agent workflow.
"""


REQUIRED_ENTITIES = {
    "SAFETY_CHECK": ["location"],
    "FISHING_ZONE": ["location"],
    "WEATHER": ["location"],
    "ROUTE": ["destination"],
    "MARINE_CONDITION": ["location"],
    "ALERT": ["location"],
    "GENERAL_QUERY": [],
}


def validate_query(intent: str, entities: dict) -> dict:
    """
    Validate required entities for an intent.

    Returns:
        {
            "valid": bool,
            "missing": list[str],
            "message": str | None
        }
    """

    normalized_intent = intent.upper().strip()

    if normalized_intent not in REQUIRED_ENTITIES:
        return {
            "valid": False,
            "missing": [],
            "message": f"Unsupported intent: {intent}",
        }

    required = REQUIRED_ENTITIES[normalized_intent]

    missing = []

    for entity in required:
        value = entities.get(entity)

        if value is None or value == "":
            missing.append(entity)

    if missing:
        labels = ", ".join(missing)

        return {
            "valid": False,
            "missing": missing,
            "message": f"Missing required information: {labels}",
        }

    return {
        "valid": True,
        "missing": [],
        "message": None,
    }


def get_clarification_message(intent: str, missing: list[str]) -> str:
    """
    Generate a user-facing clarification request.
    """

    if not missing:
        return ""

    if "location" in missing:
        return (
            "I need a coastal location to answer this safely. "
            "Which location are you planning to visit?"
        )

    if "destination" in missing:
        return (
            "I need a destination to plan the route. "
            "Where are you trying to go?"
        )

    return (
        "I need some additional information before I can "
        "answer your request."
    )
