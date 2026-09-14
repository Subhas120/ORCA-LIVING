"""M4 Response Adapter."""

from orca_living.models.decision_intelligence import DecisionIntelligence
from backend.models.response import DecisionResponse, StatusEnum, Candidate, EvidenceItem, Objective

class ResponseAdapter:
    @staticmethod
    def adapt(decision_intel: DecisionIntelligence, status: StatusEnum) -> DecisionResponse:
        
        recommended_candidate = None
        if decision_intel.recommended_candidate_id:
            # Need to get details from pipeline output.
            pass
            
        return DecisionResponse(
            status=status,
            decisionSummary=decision_intel.summary
        )
