"""M4 Backend Response Models.

This module defines the stable API contract exposed by M4.

M4 is an integration layer:
- M2 remains authoritative for marine science and safety.
- M1 remains authoritative for decision intelligence.
- M3 consumes this response for visualization.
- Voice consumes this same contract.

Do not infer or invent scientific values in these models.
"""

from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class StatusEnum(str, Enum):
    """Top-level decision lifecycle status."""

    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NO_SAFE_CANDIDATES = "NO_SAFE_CANDIDATES"
    DECISION_AVAILABLE = "DECISION_AVAILABLE"


class Uncertainty(BaseModel):
    """Structured uncertainty information."""

    level: str
    score: Optional[int] = None
    explanation: str


class EvidenceItem(BaseModel):
    """Evidence metadata exposed by the API.

    Values are only included when supplied by the authoritative
    upstream source. M4 must not fabricate scientific observations.
    """

    id: str
    category: str
    observation: str
    source: str
    timestamp: str


class Sensitivity(BaseModel):
    """Sensitivity analysis result."""

    variable: str
    current: str
    threshold: str
    explanation: str


class Candidate(BaseModel):
    """Decision candidate returned to the frontend/voice layer."""

    id: str
    name: str
    status: str

    # M2/M1-derived values. Optional because not every upstream
    # contract necessarily supplies every value.
    safety: Optional[int] = None
    opportunity: Optional[int] = None
    uncertainty: Optional[int] = None
    distance: Optional[int] = None
    confidence: Optional[str] = None

    lat: float
    lng: float

    # M1/M2 rejection or recommendation explanation.
    reason: Optional[str] = None


class Objective(BaseModel):
    """The user objective used for the decision request."""

    text: str
    vessel: Optional[str] = None
    time: str


class DecisionResponse(BaseModel):
    """Stable M4 decision API response.

    This preserves the important M1 decision-intelligence fields
    instead of reducing the result to only a recommendation.
    """

    # ---------------------------------------------------------
    # Overall status
    # ---------------------------------------------------------

    status: StatusEnum

    # ---------------------------------------------------------
    # User objective
    # ---------------------------------------------------------

    objective: Optional[Objective] = None

    # ---------------------------------------------------------
    # Candidate classification
    # ---------------------------------------------------------

    recommendedCandidate: Optional[Candidate] = None

    alternativeCandidates: List[Candidate] = Field(
        default_factory=list
    )

    rejectedCandidates: List[Candidate] = Field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Decision summary / explanation
    # ---------------------------------------------------------

    decisionSummary: Optional[str] = None

    tradeoffs: List[str] = Field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Scientific uncertainty / evidence
    # ---------------------------------------------------------

    uncertainty: Optional[Uncertainty] = None

    evidence: List[EvidenceItem] = Field(
        default_factory=list
    )

    sensitivity: Optional[Sensitivity] = None

    # ---------------------------------------------------------
    # M1 decision-intelligence outputs
    # ---------------------------------------------------------

    paretoCandidateIds: List[str] = Field(
        default_factory=list
    )

    robustness: Any = None

    valueOfInformation: Any = None

    counterfactuals: List[Any] = Field(
        default_factory=list
    )

    explanation: Any = None

    decisionTrace: Any = None

    confidence: Optional[str] = None

    # ---------------------------------------------------------
    # M2 authoritative marine safety
    # ---------------------------------------------------------

    marineSafetyStatus: Optional[str] = None

    marineSafetyReasons: List[str] = Field(
        default_factory=list
    )

    # ---------------------------------------------------------
    # Demo/live provenance
    # ---------------------------------------------------------

    dataMode: str = "DEMO"