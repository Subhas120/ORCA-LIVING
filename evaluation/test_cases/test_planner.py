import unittest

from agents.planner.planner import create_plan


class TestPlanner(unittest.TestCase):

    def test_safety_check_plan(self):
        result = create_plan("SAFETY_CHECK")

        self.assertEqual(result["intent"], "SAFETY_CHECK")
        self.assertEqual(
            result["agents"],
            ["weather", "ocean", "alert", "gis", "risk"]
        )
        self.assertTrue(result["parallel"])

    def test_fishing_zone_plan(self):
        result = create_plan("FISHING_ZONE")

        self.assertEqual(result["agents"], ["ocean", "gis"])
        self.assertTrue(result["parallel"])

    def test_weather_plan(self):
        result = create_plan("WEATHER")

        self.assertEqual(result["agents"], ["weather"])
        self.assertFalse(result["parallel"])

    def test_route_plan(self):
        result = create_plan("ROUTE")

        self.assertEqual(
            result["agents"],
            ["gis", "weather", "ocean", "risk"]
        )
        self.assertTrue(result["parallel"])

    def test_general_query_plan(self):
        result = create_plan("GENERAL_QUERY")

        self.assertEqual(result["agents"], [])
        self.assertFalse(result["parallel"])

    def test_lowercase_intent(self):
        result = create_plan("weather")

        self.assertEqual(result["intent"], "WEATHER")
        self.assertEqual(result["agents"], ["weather"])

    def test_invalid_intent(self):
        with self.assertRaises(ValueError):
            create_plan("INVALID_INTENT")


if __name__ == "__main__":
    unittest.main()
