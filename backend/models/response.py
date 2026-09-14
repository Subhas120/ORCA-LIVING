"""M4 Backend Response Models."""

from typing import List, Optional
from pydantic import BaseModel
from enum import Enum

class StatusEnum(str, Enum):
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NO_SAFE_CANDIDATES = "NO_SAFE_CANDIDATES"
    DECISION_AVAILABLE = "DECISION_AVAILABLE"

class Uncertainty(BaseModel):
    level: str
    score: int
    explanation: str

class EvidenceItem(BaseModel):
    id: str
    category: str
    observation: str
    source: str
    timestamp: str

class Sensitivity(BaseModel):
    variable: str
    current: str
    threshold: str
    explanation: str

class Candidate(BaseModel):
    id: str
    name: str
    status: str
    safety: Optional[int] = None
    opportunity: Optional[int] = None
    uncertainty: Optional[int] = None
    distance: Optional[int] = None
    confidence: Optional[str] = None
    lat: float
    lng: float
    reason: Optional[str] = None

class Objective(BaseModel):
    text: str
    vessel: Optional[str]
    time: str

class DecisionResponse(BaseModel):
    status: StatusEnum
    objective: Optional[Objective] = None
    recommendedCandidate: Optional[Candidate] = None
    alternativeCandidates: Optional[List[Candidate]] = []
    rejectedCandidates: Optional[List[Candidate]] = []
    decisionSummary: Optional[str] = None
    tradeoffs: Optional[List[str]] = []
    uncertainty: Optional[Uncertainty] = None
    evidence: Optional[List[EvidenceItem]] = []
    sensitivity: Optional[Sensitivity] = None
    dataMode: str = "LIVE"
