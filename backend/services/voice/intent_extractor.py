# backend/services/voice/intent_extractor.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import re


@dataclass(frozen=True)
class ClarificationRequired:
    missing_fields: tuple[str, ...]
    message: str
    original_text: str


@dataclass(frozen=True)
class ExtractedIntent:
    query: str
    location: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    activity: Optional[str] = None
    vessel_type: Optional[str] = None


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


DATE_KEYWORDS = {
    "next week": "next week",
    "this week": "this week",
    "tomorrow": "tomorrow",
    "today": "today",
    "aaj": "today",
    "kal": "tomorrow",
}


TIME_KEYWORDS = {
    "morning": "morning",
    "afternoon": "afternoon",
    "evening": "evening",
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


VESSEL_KEYWORDS = {
    "small boat": "Small",
    "large boat": "Large",
    "medium boat": "Medium",
    "motorboat": "Medium",
    "catamaran": "Medium",
    "trawler": "Trawler",
    "canoe": "Small",
    "dinghy": "Small",
    "yacht": "Medium",
    "boat": "Small",
    "ship": "Large",
    "small": "Small",
    "medium": "Medium",
    "large": "Large",
}


def _contains_word(text: str, phrase: str) -> bool:
    phrase = phrase.strip().lower()

    if not phrase:
        return False

    pattern = rf"(?<!\w){re.escape(phrase)}(?!\w)"

    return re.search(
        pattern,
        text.lower(),
        flags=re.IGNORECASE,
    ) is not None


def _extract_activity(text: str) -> Optional[str]:
    text_lower = text.lower()

    fishing_phrases = (
        "catching fish",
        "catch fish",
        "go fishing",
        "to fish",
        "fishing",
        "angling",
        "fishes",
        "fished",
        "fish",
    )

    for phrase in fishing_phrases:
        if _contains_word(text_lower, phrase):
            return "fishing"

    other_activities = (
        "snorkeling",
        "sailing",
        "diving",
        "surfing",
        "shipping",
        "navigation",
        "transport",
        "recreational",
        "trawling",
        "netting",
    )

    for activity in other_activities:
        if _contains_word(text_lower, activity):
            return activity

    return None


def _extract_location(text: str) -> Optional[str]:
    text_lower = text.lower()

    aliases = {
        "cochin": "Kochi",
        "vizag": "Visakhapatnam",
        "pondicherry": "Puducherry",
        "calicut": "Kozhikode",
        "trivandrum": "Thiruvananthapuram",
    }

    for location in sorted(
        KNOWN_LOCATIONS,
        key=lambda value: (-len(value), value),
    ):
        if _contains_word(text_lower, location):
            return aliases.get(
                location,
                location.title(),
            )

    return None


def _extract_date(text: str) -> Optional[str]:
    text_lower = text.lower()

    for keyword, normalized in sorted(
        DATE_KEYWORDS.items(),
        key=lambda item: (-len(item[0]), item[0]),
    ):
        if _contains_word(text_lower, keyword):
            return normalized

    return None


def _extract_time(text: str) -> Optional[str]:
    text_lower = text.lower()

    for keyword, normalized in sorted(
        TIME_KEYWORDS.items(),
        key=lambda item: (-len(item[0]), item[0]),
    ):
        if _contains_word(text_lower, keyword):
            return normalized

    return None


def _extract_vessel_type(text: str) -> Optional[str]:
    text_lower = text.lower()

    for keyword, normalized in sorted(
        VESSEL_KEYWORDS.items(),
        key=lambda item: (-len(item[0]), item[0]),
    ):
        if _contains_word(text_lower, keyword):
            return normalized

    return None


def extract_intent(
    text: str,
) -> ExtractedIntent | ClarificationRequired:

    if not text or not text.strip():
        return ClarificationRequired(
            missing_fields=("query",),
            message="No speech was recognized. Please try again.",
            original_text="",
        )

    original_text = text.strip()

    activity = _extract_activity(original_text)
    location = _extract_location(original_text)
    date = _extract_date(original_text)
    time_val = _extract_time(original_text)
    vessel_type = _extract_vessel_type(original_text)

    missing: list[str] = []

    if activity is None:
        missing.append("activity")

    if location is None:
        missing.append("location")

    if date is None:
        missing.append("date")

    if time_val is None:
        missing.append("time")

    if missing:
        suggestions: list[str] = []

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
            original_text=original_text,
        )

    return ExtractedIntent(
        query=original_text,
        location=location,
        date=date,
        time=time_val,
        activity=activity,
        vessel_type=vessel_type,
    )