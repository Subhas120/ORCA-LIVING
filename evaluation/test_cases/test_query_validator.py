import unittest

from agents.validation.query_validator import (
    validate_query,
    get_clarification_message,
)


class TestQueryValidator(unittest.TestCase):

    def test_safety_check_with_location_is_valid(self):
        result = validate_query(
            "SAFETY_CHECK",
            {"location": "Kochi"},
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["missing"], [])

    def test_safety_check_without_location_is_invalid(self):
        result = validate_query(
            "SAFETY_CHECK",
            {"location": None},
        )

        self.assertFalse(result["valid"])
        self.assertEqual(result["missing"], ["location"])

    def test_weather_requires_location(self):
        result = validate_query(
            "WEATHER",
            {},
        )

        self.assertFalse(result["valid"])
        self.assertEqual(result["missing"], ["location"])

    def test_general_query_requires_nothing(self):
        result = validate_query(
            "GENERAL_QUERY",
            {},
        )

        self.assertTrue(result["valid"])
        self.assertEqual(result["missing"], [])

    def test_route_requires_destination(self):
        result = validate_query(
            "ROUTE",
            {"location": "Kochi"},
        )

        self.assertFalse(result["valid"])
        self.assertEqual(result["missing"], ["destination"])

    def test_unknown_intent_is_invalid(self):
        result = validate_query(
            "UNKNOWN",
            {},
        )

        self.assertFalse(result["valid"])

    def test_location_clarification_message(self):
        message = get_clarification_message(
            "SAFETY_CHECK",
            ["location"],
        )

        self.assertIn("location", message.lower())

    def test_destination_clarification_message(self):
        message = get_clarification_message(
            "ROUTE",
            ["destination"],
        )

        self.assertIn("destination", message.lower())


if __name__ == "__main__":
    unittest.main()
