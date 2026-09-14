"""M4 Voice Intent Extractor.

Extracts structured fields from normalized text to build
a DecisionRequest for the M4 backend.

SAFETY INVARIANT: This module performs ONLY linguistic parsing.
It MUST NOT:
  - perform marine safety reasoning
  - invent marine thresholds or constraints
  - fabricate geographic or temporal data
  - guess decision-critical fields when ambiguous

When a decision-critical field is ambiguous or missing,
the extractor returns a ClarificationRequired result
instead of guessing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ClarificationRequired:
    """Indicates the voice input needs clarification before proceeding."""

    missing_fields: tuple[str, ...]
    message: str
    original_text: str


@dataclass(frozen=True)
class ExtractedIntent:
    """Structured intent extracted from normalized voice text."""

    query: str
    location: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    activity: Optional[str] = None
    vessel_type: Optional[str] = None


KNOWN_ACTIVITIES = {
    "fishing",
    "sailing",
    "diving",
    "snorkeling",
    "surfing",
    "shipping",
    "navigation",
    "transport",
    "recreational",
    "trawling",
    "netting",
}


KNOWN_LOCATIONS = {
    "kochi",
    "cochin",
    "mumbai",
    "chennai",
    "visakhapatnam",
    "vizag",
    "goa",
    "mangalore",
    "tuticorin",
    "puducherry",
    "pondicherry",
    "paradip",
    "haldia",
    "kandla",
    "porbandar",
    "veraval",
    "ratnagiri",
    "karwar",
    "kollam",
    "alappuzha",
    "kozhikode",
    "calicut",
    "trivandrum",
    "thiruvananthapuram",
    "kakinada",
    "machilipatnam",
    "rameswaram",
    "nagapattinam",
    "cuddalore",
}


TIME_KEYWORDS = {
    "morning": "morning",
    "evening": "evening",
    "afternoon": "afternoon",
    "night": "night",
    "dawn": "dawn",
    "dusk": "dusk",
    "sunrise": "morning",
    "sunset": "evening",
    "subah": "morning",
    "sham": "evening",
    "dopahar": "afternoon",
    "raat": "night",
}


DATE_KEYWORDS = {
    "today": "today",
    "tomorrow": "tomorrow",
    "aaj": "today",
    "kal": "tomorrow",
    "next week": "next week",
    "this week": "this week",
}


VESSEL_KEYWORDS = {
    "small": "Small",
    "large": "Large",
    "medium": "Medium",
    "trawler": "Trawler",
    "boat": "Small",
    "ship": "Large",
    "canoe": "Small",
    "yacht": "Medium",
    "dinghy": "Small",
    "catamaran": "Medium",
    "motorboat": "Medium",
}


def extract_intent(text: str) -> ExtractedIntent | ClarificationRequired:
    """Extract structured intent from normalized voice text.

    Decision-critical fields are activity, location, date, and time.
    If any required field is missing, clarification is requested
    instead of fabricating a value.
    """

    if not text or not text.strip():
        return ClarificationRequired(
            missing_fields=("query",),
            message="No speech was recognized. Please try again.",
            original_text="",
        )

    text_lower = text.lower().strip()

    # Extract activity
    activity = None

    for keyword in KNOWN_ACTIVITIES:
        if keyword in text_lower:
            activity = keyword
            break

    # Extract location
    location = None

    for loc in KNOWN_LOCATIONS:
        if loc in text_lower:
            location = loc.title()
            break

    # Extract date
    date = None

    for keyword, normalized in DATE_KEYWORDS.items():
        if keyword in text_lower:
            date = normalized
            break

    # Extract time
    time_val = None

    for keyword, normalized in TIME_KEYWORDS.items():
        if keyword in text_lower:
            time_val = normalized
            break

    # Extract vessel type
    vessel_type = None

    for keyword, normalized in VESSEL_KEYWORDS.items():
        if keyword in text_lower:
            vessel_type = normalized
            break

    # Decision-critical field validation.
    # Activity, location, date, and time are REQUIRED.
    # Never guess or fabricate missing decision-critical fields.
    missing = []

    if not activity:
        missing.append("activity")

    if not location:
        missing.append("location")

    if not date:
        missing.append("date")

    if not time_val:
        missing.append("time")

    if missing:
        suggestions = []

        if "activity" in missing:
            suggestions.append(
                "What activity are you planning? "
                "(e.g., fishing, sailing, diving)"
            )

        if "location" in missing:
            suggestions.append(
                "Which coastal location? "
                "(e.g., Kochi, Mumbai, Chennai)"
            )

        if "date" in missing:
            suggestions.append(
                "What date are you planning for? "
                "(e.g., today or tomorrow)"
            )

        if "time" in missing:
            suggestions.append(
                "What time are you planning for? "
                "(e.g., morning or evening)"
            )

        return ClarificationRequired(
            missing_fields=tuple(missing),
            message=" ".join(suggestions),
            original_text=text,
        )

    return ExtractedIntent(
        query=text,
        location=location,
        date=date,
        time=time_val,
        activity=activity,
        vessel_type=vessel_type,
    )