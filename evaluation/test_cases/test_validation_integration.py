import unittest

from agents.context.context_manager import ConversationContext
from agents.orchestrator.orchestrator import run_query


class TestValidationIntegration(unittest.TestCase):

    def test_missing_location_returns_clarification(self):
        result = run_query(
            "Is it safe to fish tomorrow?"
        )

        self.assertEqual(
            result["intent"],
            "SAFETY_CHECK",
        )

        self.assertFalse(
            result["validation"]["valid"]
        )

        self.assertEqual(
            result["validation"]["missing"],
            ["location"],
        )

        self.assertEqual(
            result["agents"],
            [],
        )

        self.assertEqual(
            result["agent_requests"],
            [],
        )

        self.assertIsNotNone(
            result["clarification"]
        )

    def test_valid_query_proceeds_to_agents(self):
        result = run_query(
            "Is it safe to fish near Kochi tomorrow?"
        )

        self.assertTrue(
            result["validation"]["valid"]
        )

        self.assertEqual(
            result["agents"],
            ["weather", "ocean", "alert", "gis", "risk"],
        )

        self.assertEqual(
            len(result["agent_requests"]),
            5,
        )

        self.assertIsNone(
            result["clarification"]
        )

    def test_context_can_supply_missing_location(self):
        context = ConversationContext()

        run_query(
            "Is it safe to fish near Kochi?",
            context=context,
        )

        result = run_query(
            "What about the waves?",
            context=context,
        )

        self.assertTrue(
            result["validation"]["valid"]
        )

        self.assertEqual(
            result["entities"]["location"],
            "Kochi",
        )

        self.assertEqual(
            result["agents"],
            ["ocean"],
        )


if __name__ == "__main__":
    unittest.main()
