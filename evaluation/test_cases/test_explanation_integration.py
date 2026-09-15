import unittest

from agents.orchestrator.orchestrator import run_query
from agents.common.agent_contract import AgentResponse


class TestExplanationIntegration(unittest.TestCase):

    def test_orchestrator_builds_explanation_from_risk_and_evidence(self):

        responses = [
            AgentResponse(
                agent="weather",
                status="success",
                data={
                    "wind_speed": 18,
                },
                source="Weather API",
                timestamp="2026-09-10T10:00:00",
                location="Kochi",
                confidence=0.90,
            ),
            AgentResponse(
                agent="ocean",
                status="success",
                data={
                    "wave_height": 2.1,
                },
                source="INCOIS",
                timestamp="2026-09-10T09:30:00",
                location="Kochi",
                confidence=0.95,
            ),
        ]

        risk = {
            "score": 67,
            "level": "HIGH",
            "reasons": [
                "High wave conditions",
                "Strong wind",
            ],
        }

        result = run_query(
            "Is it safe to fish tomorrow near Kochi?",
            responses=responses,
            risk=risk,
        )

        self.assertEqual(
            result["risk"]["level"],
            "HIGH",
        )

        self.assertEqual(
            result["explanation"]["risk_level"],
            "HIGH",
        )

        self.assertEqual(
            result["explanation"]["risk_score"],
            67,
        )

        self.assertEqual(
            len(result["evidence"]),
            2,
        )

        self.assertIn(
            "HIGH RISK",
            result["rendered_explanation"],
        )

        self.assertIn(
            "2.1 m",
            result["rendered_explanation"],
        )

        self.assertIn(
            "INCOIS",
            result["rendered_explanation"],
        )

    def test_orchestrator_does_not_create_explanation_without_risk(self):

        responses = [
            AgentResponse(
                agent="weather",
                status="success",
                data={
                    "wind_speed": 12,
                },
                source="Weather API",
                confidence=0.90,
            ),
        ]

        result = run_query(
            "What is the weather near Kochi?",
            responses=responses,
        )

        self.assertIsNone(
            result["risk"]
        )

        self.assertIsNone(
            result["explanation"]
        )

        self.assertIsNone(
            result["rendered_explanation"]
        )


if __name__ == "__main__":
    unittest.main()
