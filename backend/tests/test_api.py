"""Integration tests for M4 Backend."""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_decision_endpoint_insufficient_evidence():
    response = client.post(
        "/api/v1/decision",
        json={
            "query": "Find safe fishing",
            "location": "Kochi",
            "date": "tomorrow",
            "time": "morning",
            "activity": "fishing",
            "vessel_type": "Small"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "INSUFFICIENT_EVIDENCE"

def test_decision_endpoint_valid_fixture(monkeypatch):
    """Proves M4 reaches actual M1 pipeline when M2 contract is valid."""
    from backend.services.m2_adapter import M2Adapter
    from orca_living.models.marine_world_state import MarineWorldState, StateRegion
    from orca_living.models.safety import SafetyEvaluation
    import datetime

    def mock_get_marine_state_and_safety(self, request):
        # Provide a valid dummy world state to bypass M2's current limitation
        world_state = MarineWorldState(
            state_id="test-state-1",
            schema_version="1.0",
            generated_at=datetime.datetime.now(),
            time=datetime.datetime.now(),
            region=StateRegion(name="Kochi", latitude=9.9, longitude=76.2)
        )

        from orca_living.engines.candidate_generator import CandidateProposal
        proposals = (CandidateProposal(id="mock-1", action_type="fishing", latitude=9.9, longitude=76.2, expected_opportunity=0.8, distance=5.0, objective_values={"Find safe opportunity": 0.8}),)
        safety_evals = (SafetyEvaluation(
            candidate_id="mock-1",
            status="SAFE",
            constraint_results={"wave_height": True},
            failed_constraints=tuple(),
            evidence_refs=tuple(),
            uncertainty_refs=tuple(),
            reason="Wave height is within safe bounds",
            safety_margin=1.0
        ),)
        return world_state, proposals, safety_evals

    monkeypatch.setattr(M2Adapter, "get_marine_state_and_safety", mock_get_marine_state_and_safety)

    response = client.post(
        "/api/v1/decision",
        json={
            "query": "Find safe fishing",
            "location": "Kochi",
            "date": "tomorrow",
            "time": "morning",
            "activity": "fishing",
            "vessel_type": "Small"
        }
    )
    print(response.json())
    assert response.status_code == 200

    data = response.json()
    # If it hits M1 and M1 runs successfully without safe candidates among proposals, it returns NO_SAFE_CANDIDATES
    assert data["status"] in ["NO_SAFE_CANDIDATES", "DECISION_AVAILABLE"]
