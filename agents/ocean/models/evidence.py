from dataclasses import dataclass
from typing import Optional


@dataclass
class Evidence:
    """
    Represents the source and reliability information
    for an ORCA marine observation.
    """

    source: str
    timestamp: str
    confidence: float
    parameter: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "parameter": self.parameter,
            "source": self.source,
            "timestamp": self.timestamp,
            "confidence": self.confidence,
        }