"""M4 Adapter for M2 Marine Agent."""

from orca_living.models.marine_world_state import (
    MarineWorldState, OceanState, WeatherState, HazardState,
    GeospatialState, EcologicalState, VesselState, DecisionState
)
from orca_living.models.safety import SafetyEvaluation
from agents.common.agent_contract import AgentRequest
from agents.ocean.ocean_agent import handle_ocean
from backend.models.request import DecisionRequest

class M2AdapterError(Exception):
    pass

class InsufficientEvidenceError(Exception):
    pass

class M2Adapter:
    """Adapts M2 agent responses to M1 pipeline inputs."""
    
    @staticmethod
    def get_marine_state_and_safety(request: DecisionRequest) -> tuple[MarineWorldState, tuple, tuple[SafetyEvaluation, ...]]:
        """Call M2 and convert its data to M1 MarineWorldState and SafetyEvaluation."""
        
        m2_request = AgentRequest(
            query=request.query,
            location=request.location,
            destination=None,
            date=request.date,
            time=request.time,
            activity=request.activity
        )
        
        m2_response = handle_ocean(m2_request)
        
        if m2_response.status == "unavailable" or m2_response.status == "error":
            raise M2AdapterError(m2_response.error or "M2 service unavailable")
            
        data = m2_response.data
        if not data:
            raise InsufficientEvidenceError("M2 returned no data")
            
        # M2 currently does NOT provide safety evaluation logic.
        # CRITICAL SAFETY RULE: M4 must NOT invent safety thresholds.
        # Therefore, we cannot construct a valid SafetyEvaluation(status="SAFE").
        # We must raise InsufficientEvidenceError to ensure safety invariants.
        
        raise InsufficientEvidenceError("M2 lacks safety capability. Cannot generate valid SafetyEvaluation.")
