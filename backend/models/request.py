"""M4 Backend Request Models."""

from typing import Optional
from pydantic import BaseModel

class DecisionRequest(BaseModel):
    query: str
    location: str
    date: str
    time: str
    activity: str
    vessel_type: Optional[str] = None
    scenario_id: Optional[str] = None
