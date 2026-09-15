"""Focused M4 contract tests for the shared decision orchestration."""

from types import SimpleNamespace

from backend.models.request import DecisionRequest
from backend.models.response import StatusEnum
from backend.services.decision_service import DecisionService
from orca_living.engines.candidate_generator import CandidateProposal
from orca_living.models.decision_intelligence import DecisionIntelligence


class FakeM2:
    def __init__(self, safety_status="SAFE"):
        self.safety_status = safety_status

    def get_marine_state_and_safety(self, request):
        proposal = CandidateProposal(
            id="PFZ_TEST_01",
            action_type=request.activity,
            latitude=9.85,
            longitude=76.15,
            name="PFZ_TEST_01",
            expected_opportunity=0.9,
            distance=10.0,
            objective_values={
                "opportunity": 0.9,
                "distance": 10.0,
                "uncertainty": 0.1,
            },
            evidence_refs=("m2:pfz:PFZ_TEST_01",),
            uncertainty_refs=("m2:confidence:PFZ_TEST_01",),
        )
        safety = SimpleNamespace(
            status=self.safety_status,
            reason="test safety result",
        )
        return SimpleNamespace(), (proposal,), (safety,)


class FakeM1:
    def __init__(self, recommendation="PFZ_TEST_01", fail=False):
        self.recommendation = recommendation
        self.fail = fail

    def run_decision_pipeline(self, world_state, proposals, safety_evaluations, request):
        if self.fail:
            raise RuntimeError("test M1 failure")
        return DecisionIntelligence(
            decision_id="test-decision",
            status="DECISION_AVAILABLE" if self.recommendation else "NO_SAFE_CANDIDATES",
            recommended_candidate_id=self.recommendation,
            summary="test decision",
        )


def request():
    return DecisionRequest(
        query="Find the best fishing zone",
        location="Kochi",
        date="tomorrow",
        time="morning",
        activity="fishing",
        vessel_type="small_vessel",
    )


def test_safe_request_returns_decision():
    result = DecisionService(
        m2_adapter=FakeM2("SAFE"),
        m1_service=FakeM1("PFZ_TEST_01"),
    ).run(request())

    assert result.status == StatusEnum.DECISION_AVAILABLE
    assert result.recommendedCandidate is not None
    assert result.marineSafetyStatus == "SAFE"


def test_unsafe_request_cannot_return_recommendation():
    result = DecisionService(
        m2_adapter=FakeM2("UNSAFE"),
        m1_service=FakeM1(None),
    ).run(request())

    assert result.status == StatusEnum.NO_SAFE_CANDIDATES
    assert result.recommendedCandidate is None
    assert result.marineSafetyStatus == "UNSAFE"


def test_unsafe_m1_violation_fails_closed():
    result = DecisionService(
        m2_adapter=FakeM2("UNSAFE"),
        m1_service=FakeM1("PFZ_TEST_01"),
    ).run(request())

    assert result.status == StatusEnum.SERVICE_UNAVAILABLE
    assert result.recommendedCandidate is None
    assert result.marineSafetyStatus == "UNSAFE"


def test_missing_safety_status_never_becomes_safe():
    result = DecisionService(
        m2_adapter=FakeM2(None),
        m1_service=FakeM1("PFZ_TEST_01"),
    ).run(request())

    assert result.status == StatusEnum.INSUFFICIENT_EVIDENCE
    assert result.recommendedCandidate is None
    assert result.marineSafetyStatus == "INSUFFICIENT_EVIDENCE"


def test_m1_failure_is_service_unavailable():
    result = DecisionService(
        m2_adapter=FakeM2("SAFE"),
        m1_service=FakeM1(fail=True),
    ).run(request())

    assert result.status == StatusEnum.SERVICE_UNAVAILABLE
    assert result.recommendedCandidate is None
    assert result.marineSafetyStatus == "SAFE"
