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
