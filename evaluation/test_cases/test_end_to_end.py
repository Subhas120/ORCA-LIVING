import unittest

from agents.common.agent_contract import AgentResponse
from agents.orchestrator.orchestrator import run_query


class TestEndToEndCoordinator(unittest.TestCase):

    def test_safety_query_with_agent_responses(self):
        query = "Is it safe to fish tomorrow near Kochi?"

        responses = [
            AgentResponse(
                agent="weather",
                status="success",
                data={"wind_speed": 18},
                source="Weather API",
                location="Kochi",
                confidence=0.90,
            ),
            AgentResponse(
                agent="ocean",
                status="success",
                data={"wave_height": 2.1},
                source="INCOIS",
                location="Kochi",
                confidence=0.95,
            ),
            AgentResponse(
                agent="alert",
                status="unavailable",
                error="Alert service unavailable",
            ),
        ]

        result = run_query(query, responses)

        self.assertEqual(result["intent"], "SAFETY_CHECK")
        self.assertEqual(result["entities"]["location"], "Kochi")
        self.assertEqual(result["entities"]["date"], "tomorrow")
        self.assertEqual(result["entities"]["activity"], "fishing")

        self.assertEqual(len(result["agent_requests"]), 5)

        self.assertEqual(
            result["responses"]["successful_count"],
            2,
        )

        self.assertEqual(
            result["responses"]["unavailable_count"],
            1,
        )

        self.assertEqual(
            result["responses"]["failed_count"],
            0,
        )

    def test_query_without_responses(self):
        result = run_query(
            "What is the weather tomorrow in Mumbai?"
        )

        self.assertEqual(result["intent"], "WEATHER")
        self.assertEqual(result["agents"], ["weather"])
        self.assertEqual(len(result["agent_requests"]), 1)
        self.assertEqual(result["responses"]["total"], 0)


if __name__ == "__main__":
    unittest.main()
