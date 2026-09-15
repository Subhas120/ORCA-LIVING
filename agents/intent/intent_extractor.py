import re

INTENTS = {
    "SAFETY_CHECK": [
        "is it safe",
        "is this safe",
        "safe to",
        "safety",
        "dangerous",
        "danger",
        "risk",
        "can i go",
        "should i go",
    ],
    "FISHING_ZONE": [
        "fishing zone",
        "pfz",
        "where should i fish",
        "where to fish",
        "best place to fish",
    ],
    "WEATHER": [
        "weather",
        "rain",
        "wind",
        "temperature",
        "forecast",
    ],
    "ROUTE": [
        "route",
        "safest route",
        "safe route",
        "how do i reach",
        "how to reach",
        "reach",
        "path",
    ],
    "MARINE_CONDITION": [
        "wave",
        "waves",
        "sea condition",
        "ocean condition",
        "sea state",
        "current",
        "swell",
    ],
    "ALERT": [
        "alert",
        "warning",
        "cyclone",
        "storm",
        "lightning",
    ],
}

COASTAL_LOCATIONS = [
    "kochi",
    "mumbai",
    "chennai",
    "mangalore",
    "goa",
    "visakhapatnam",
    "tuticorin",
    "kollam",
    "alappuzha",
]

TIME_WORDS = [
    "morning",
    "afternoon",
    "evening",
    "night",
]

DATE_WORDS = [
    "today",
    "tomorrow",
    "day after tomorrow",
]

ACTIVITY_PATTERNS = {
    "fishing": ["fishing", "fish"],
    "travel": ["travel", "travelling", "traveling"],
    "boating": ["boating", "boat"],
    "sailing": ["sailing", "sail"],
}


def classify_intent(query: str) -> str:
    text = query.lower().strip()

    priority_order = [
        "ROUTE",
        "FISHING_ZONE",
        "ALERT",
        "MARINE_CONDITION",
        "WEATHER",
        "SAFETY_CHECK",
    ]

    for intent in priority_order:
        for keyword in INTENTS[intent]:
            if keyword in text:
                return intent

    return "GENERAL_QUERY"


def extract_location(query: str):
    text = query.lower()

    for location in COASTAL_LOCATIONS:
        if re.search(
            r"\b" + re.escape(location) + r"\b",
            text,
        ):
            return location.title()

    return None


def extract_destination(query: str):
    text = query.lower()

    # Explicit "from X to Y" route
    match = re.search(
        r"\bfrom\s+([a-z]+)\s+to\s+([a-z]+)\b",
        text,
    )

    if match:
        destination = match.group(2)

        if destination in COASTAL_LOCATIONS:
            return destination.title()

    # Explicit "to X" or "towards X"
    patterns = [
        r"\bto\s+([a-z]+)\b",
        r"\btowards\s+([a-z]+)\b",
        r"\bdestination\s+([a-z]+)\b",
        r"\breach\s+([a-z]+)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            destination = match.group(1)

            if destination in COASTAL_LOCATIONS:
                return destination.title()

    return None


def extract_date(query: str):
    text = query.lower()

    if "day after tomorrow" in text:
        return "day after tomorrow"

    for date_word in DATE_WORDS:
        if date_word in text:
            return date_word

    return None


def extract_time(query: str):
    text = query.lower()

    for time_word in TIME_WORDS:
        if time_word in text:
            return time_word

    return None


def extract_activity(query: str):
    text = query.lower()

    for activity, patterns in ACTIVITY_PATTERNS.items():
        for pattern in patterns:
            if re.search(
                r"\b" + re.escape(pattern) + r"\b",
                text,
            ):
                return activity

    return None


def extract_entities(query: str):
    intent = classify_intent(query)

    location = extract_location(query)
    destination = extract_destination(query)

    # For a route query containing only one location,
    # treat that location as the destination.
    if intent == "ROUTE" and destination is None and location is not None:
        destination = location
        location = None

    return {
        "location": location,
        "destination": destination,
        "date": extract_date(query),
        "time": extract_time(query),
        "activity": extract_activity(query),
    }


def analyze_query(query: str):
    return {
        "intent": classify_intent(query),
        **extract_entities(query),
    }


if __name__ == "__main__":

    queries = [
        "Can I go fishing near Kochi tomorrow morning?",
        "What is the safest route from Kochi to Alappuzha?",
        "How do I reach Mangalore?",
        "What is the safest route to Goa?",
    ]

    for query in queries:
        print(analyze_query(query))
