import unittest

from agents.explanation.explanation_engine import build_explanation


class TestExplanationSafetyBoundaries(unittest.TestCase):

    def test_missing_risk_level_is_unknown(self):
        explanation = build_explanation(
            {
                "score": None,
                "reasons": [],
            },
            [],
        )

        self.assertEqual(
            explanation["risk_level"],
            "UNKNOWN",
        )

    def test_invalid_risk_level_is_unknown(self):
        explanation = build_explanation(
            {
                "score": 20,
                "level": "SAFE",
                "reasons": [],
            },
            [],
        )

        self.assertEqual(
            explanation["risk_level"],
            "UNKNOWN",
        )

    def test_extreme_risk_is_preserved(self):
        explanation = build_explanation(
            {
                "score": 95,
                "level": "EXTREME",
                "reasons": [
                    "Severe cyclone warning",
                ],
            },
            [],
        )

        self.assertEqual(
            explanation["risk_level"],
            "EXTREME",
        )

        self.assertEqual(
            explanation["risk_score"],
            95,
        )

        self.assertEqual(
            explanation["reasons"],
            ["Severe cyclone warning"],
        )


if __name__ == "__main__":
    unittest.main()
