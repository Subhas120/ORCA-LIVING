import unittest

from agents.common.agent_contract import AgentResponse
from agents.orchestrator.response_aggregator import (
    aggregate_responses,
    get_evidence,
)


class TestResponseAggregator(unittest.TestCase):

    def test_all_successful(self):
        responses = [
            AgentResponse(
                agent="weather",
                status="success",
                data={"wind_speed": 18},
                source="Weather API",
                location="Kochi",
                confidence=0.9,
            ),
            AgentResponse(
                agent="ocean",
                status="success",
                data={"wave_height": 2.1},
                source="INCOIS",
                location="Kochi",
                confidence=0.95,
            ),
        ]

        result = aggregate_responses(responses)

        self.assertEqual(result["total"], 2)
        self.assertEqual(result["successful_count"], 2)
        self.assertEqual(result["failed_count"], 0)
        self.assertEqual(result["unavailable_count"], 0)

    def test_unavailable_agent(self):
        responses = [
            AgentResponse(
                agent="weather",
                status="success",
                data={"wind_speed": 18},
            ),
            AgentResponse(
                agent="alert",
                status="unavailable",
                error="Alert service unavailable",
            ),
        ]

        result = aggregate_responses(responses)

        self.assertEqual(result["total"], 2)
        self.assertEqual(result["successful_count"], 1)
        self.assertEqual(result["unavailable_count"], 1)
        self.assertEqual(result["failed_count"], 0)

    def test_failed_agent(self):
        responses = [
            AgentResponse(
                agent="ocean",
                status="error",
                error="Invalid marine data",
            ),
        ]

        result = aggregate_responses(responses)

        self.assertEqual(result["total"], 1)
        self.assertEqual(result["successful_count"], 0)
        self.assertEqual(result["failed_count"], 1)
        self.assertEqual(result["unavailable_count"], 0)

    def test_evidence_extraction(self):
        responses = [
            AgentResponse(
                agent="ocean",
                status="success",
                data={"wave_height": 2.1},
                source="INCOIS",
                timestamp="2026-09-10T20:00:00",
                location="Kochi",
                confidence=0.95,
            ),
            AgentResponse(
                agent="alert",
                status="unavailable",
                error="Service unavailable",
            ),
        ]

        result = aggregate_responses(responses)
        evidence = get_evidence(result)

        self.assertEqual(len(evidence), 1)
        self.assertEqual(evidence[0]["agent"], "ocean")
        self.assertEqual(evidence[0]["data"]["wave_height"], 2.1)
        self.assertEqual(evidence[0]["source"], "INCOIS")
        self.assertEqual(evidence[0]["location"], "Kochi")
        self.assertEqual(evidence[0]["confidence"], 0.95)

    def test_invalid_response_rejected(self):
        with self.assertRaises(TypeError):
            aggregate_responses(["not an AgentResponse"])


if __name__ == "__main__":
    unittest.main()
