import unittest

from agents.explanation.explanation_engine import (
    build_explanation,
    render_explanation,
)


class TestExplanationEngine(unittest.TestCase):

    def test_high_risk_explanation(self):
        risk = {
            "score": 67,
            "level": "HIGH",
            "reasons": [
                "High wave conditions",
                "Strong wind",
            ],
        }

        evidence = [
            {
                "agent": "weather",
                "data": {
                    "wind_speed": 18,
                },
                "source": "Weather API",
                "timestamp": "2026-09-10T10:00:00",
                "location": "Kochi",
                "confidence": 0.90,
            },
            {
                "agent": "ocean",
                "data": {
                    "wave_height": 2.1,
                },
                "source": "INCOIS",
                "timestamp": "2026-09-10T09:30:00",
                "location": "Kochi",
                "confidence": 0.95,
            },
        ]

        explanation = build_explanation(
            risk,
            evidence,
        )

        self.assertEqual(
            explanation["risk_level"],
            "HIGH",
        )

        self.assertEqual(
            explanation["risk_score"],
            67,
        )

        self.assertEqual(
            len(explanation["reasons"]),
            2,
        )

        self.assertEqual(
            len(explanation["evidence"]),
            2,
        )

    def test_risk_decision_is_not_changed(self):
        risk = {
            "score": 85,
            "level": "EXTREME",
            "reasons": [
                "Severe weather warning",
            ],
        }

        explanation = build_explanation(
            risk,
            [],
        )

        self.assertEqual(
            explanation["risk_level"],
            "EXTREME",
        )

        self.assertEqual(
            explanation["risk_score"],
            85,
        )

    def test_evidence_metadata_is_preserved(self):
        risk = {
            "score": 40,
            "level": "MODERATE",
            "reasons": [],
        }

        evidence = [
            {
                "agent": "ocean",
                "data": {
                    "wave_height": 1.4,
                },
                "source": "INCOIS",
                "timestamp": "2026-09-10T09:30:00",
                "location": "Kochi",
                "confidence": 0.95,
            },
        ]

        explanation = build_explanation(
            risk,
            evidence,
        )

        item = explanation["evidence"][0]

        self.assertEqual(
            item["source"],
            "INCOIS",
        )

        self.assertEqual(
            item["timestamp"],
            "2026-09-10T09:30:00",
        )

        self.assertEqual(
            item["location"],
            "Kochi",
        )

        self.assertEqual(
            item["confidence"],
            0.95,
        )

    def test_render_contains_risk_and_evidence(self):
        explanation = build_explanation(
            {
                "score": 67,
                "level": "HIGH",
                "reasons": ["High waves"],
            },
            [
                {
                    "agent": "ocean",
                    "data": {
                        "wave_height": 2.1,
                    },
                    "source": "INCOIS",
                    "confidence": 0.95,
                },
            ],
        )

        rendered = render_explanation(
            explanation
        )

        self.assertIn(
            "HIGH RISK",
            rendered,
        )

        self.assertIn(
            "67/100",
            rendered,
        )

        self.assertIn(
            "High waves",
            rendered,
        )

        self.assertIn(
            "2.1 m",
            rendered,
        )

        self.assertIn(
            "INCOIS",
            rendered,
        )


if __name__ == "__main__":
    unittest.main()
