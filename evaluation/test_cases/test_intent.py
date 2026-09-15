import unittest

from agents.intent.intent_extractor import analyze_query


class TestIntentExtractor(unittest.TestCase):

    def test_safety_check(self):
        result = analyze_query("Is it safe to fish tomorrow near Kochi?")

        self.assertEqual(result["intent"], "SAFETY_CHECK")
        self.assertEqual(result["location"], "Kochi")
        self.assertEqual(result["date"], "tomorrow")
        self.assertEqual(result["activity"], "fishing")

    def test_fishing_zone(self):
        result = analyze_query("Where should I fish near Kochi?")

        self.assertEqual(result["intent"], "FISHING_ZONE")
        self.assertEqual(result["location"], "Kochi")
        self.assertEqual(result["activity"], "fishing")

    def test_weather(self):
        result = analyze_query("What is the weather tomorrow in Mumbai?")

        self.assertEqual(result["intent"], "WEATHER")
        self.assertEqual(result["location"], "Mumbai")
        self.assertEqual(result["date"], "tomorrow")

    def test_route(self):
        result = analyze_query("Show me the safest route to the fishing zone.")

        self.assertEqual(result["intent"], "ROUTE")
        self.assertEqual(result["activity"], "fishing")

    def test_marine_condition(self):
        result = analyze_query("What are the wave conditions near Kochi?")

        self.assertEqual(result["intent"], "MARINE_CONDITION")
        self.assertEqual(result["location"], "Kochi")

    def test_alert(self):
        result = analyze_query("Is there any cyclone warning near Chennai?")

        self.assertEqual(result["intent"], "ALERT")
        self.assertEqual(result["location"], "Chennai")

    def test_general_query(self):
        result = analyze_query("Tell me about the ocean.")

        self.assertEqual(result["intent"], "GENERAL_QUERY")


if __name__ == "__main__":
    unittest.main()
