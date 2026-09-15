import unittest

from agents.context.context_manager import ConversationContext


class TestConversationContext(unittest.TestCase):

    def test_update_and_get(self):

        context = ConversationContext()

        context.update({
            "location": "Kochi",
            "destination": "Alappuzha",
            "date": "tomorrow",
            "time": None,
            "activity": "fishing",
        })

        self.assertEqual(
            context.get(),
            {
                "location": "Kochi",
                "destination": "Alappuzha",
                "date": "tomorrow",
                "time": None,
                "activity": "fishing",
            },
        )

    def test_fill_missing_entities(self):

        context = ConversationContext()

        context.update({
            "location": "Kochi",
            "destination": "Alappuzha",
            "date": "tomorrow",
            "time": "morning",
            "activity": "fishing",
        })

        result = context.fill_missing({
            "location": None,
            "destination": None,
            "date": None,
            "time": "evening",
            "activity": None,
        })

        self.assertEqual(
            result,
            {
                "location": "Kochi",
                "destination": "Alappuzha",
                "date": "tomorrow",
                "time": "evening",
                "activity": "fishing",
            },
        )

    def test_current_query_overrides_context(self):

        context = ConversationContext()

        context.update({
            "location": "Kochi",
            "destination": "Alappuzha",
            "date": "tomorrow",
            "time": "morning",
            "activity": "fishing",
        })

        result = context.fill_missing({
            "location": "Mangalore",
            "destination": "Goa",
            "date": "today",
            "time": None,
            "activity": "boating",
        })

        self.assertEqual(
            result,
            {
                "location": "Mangalore",
                "destination": "Goa",
                "date": "today",
                "time": "morning",
                "activity": "boating",
            },
        )

    def test_clear(self):

        context = ConversationContext()

        context.update({
            "location": "Kochi",
            "destination": "Alappuzha",
            "date": "tomorrow",
            "time": "morning",
            "activity": "fishing",
        })

        context.clear()

        self.assertEqual(
            context.get(),
            {
                "location": None,
                "destination": None,
                "date": None,
                "time": None,
                "activity": None,
            },
        )


if __name__ == "__main__":
    unittest.main()
