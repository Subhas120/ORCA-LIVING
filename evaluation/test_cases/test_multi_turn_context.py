import unittest

from agents.context.context_manager import ConversationContext
from agents.orchestrator.orchestrator import run_query


class TestMultiTurnContext(unittest.TestCase):

    def test_context_is_reused_between_queries(self):
        context = ConversationContext()

        first = run_query(
            "Is it safe to fish near Kochi tomorrow?",
            context=context,
        )

        self.assertEqual(
            first["entities"]["location"],
            "Kochi",
        )

        self.assertEqual(
            first["entities"]["date"],
            "tomorrow",
        )

        self.assertEqual(
            first["entities"]["activity"],
            "fishing",
        )

        second = run_query(
            "What about the waves?",
            context=context,
        )

        self.assertEqual(
            second["intent"],
            "MARINE_CONDITION",
        )

        self.assertEqual(
            second["entities"]["location"],
            "Kochi",
        )

        self.assertEqual(
            second["entities"]["date"],
            "tomorrow",
        )

        self.assertEqual(
            second["entities"]["activity"],
            "fishing",
        )

    def test_new_query_overrides_remembered_location(self):
        context = ConversationContext()

        run_query(
            "Is it safe to fish near Kochi?",
            context=context,
        )

        result = run_query(
            "What about the waves near Mumbai?",
            context=context,
        )

        self.assertEqual(
            result["entities"]["location"],
            "Mumbai",
        )

        self.assertEqual(
            result["entities"]["activity"],
            "fishing",
        )


if __name__ == "__main__":
    unittest.main()
