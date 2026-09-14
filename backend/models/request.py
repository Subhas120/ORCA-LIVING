"""M4 Backend Request Models.

These fields are decision-critical input supplied by REST or voice.
M4 validates presence/format but does not infer missing marine facts.
"""

from typing import Optional

from pydantic import BaseModel, field_validator


class DecisionRequest(BaseModel):
    query: str
    location: str
    date: str
    time: str
    activity: str
    vessel_type: Optional[str] = None
    scenario_id: Optional[str] = None

    @field_validator(
        "query",
        "location",
        "date",
        "time",
        "activity",
        mode="before",
    )
    @classmethod
    def require_non_empty_text(cls, value: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("decision-critical fields cannot be empty")
        return value.strip()

    @field_validator("vessel_type", "scenario_id", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            raise ValueError("optional text fields must be strings")
        value = value.strip()
        return value or None
