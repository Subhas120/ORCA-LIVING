import unittest

from agents.orchestrator.orchestrator import (
    build_execution_context,
    get_agent_tasks,
)


class TestOrchestrator(unittest.TestCase):

    def test_safety_check_context(self):
        query = "Is it safe to fish tomorrow near Kochi?"

        result = build_execution_context(query)

        self.assertEqual(result["intent"], "SAFETY_CHECK")
        self.assertEqual(result["entities"]["location"], "Kochi")
        self.assertEqual(result["entities"]["date"], "tomorrow")
        self.assertEqual(result["entities"]["activity"], "fishing")

        self.assertEqual(
            result["agents"],
            ["weather", "ocean", "alert", "gis", "risk"]
        )

        self.assertTrue(result["parallel"])

    def test_safety_check_agent_tasks(self):
        query = "Is it safe to fish tomorrow near Kochi?"

        context = build_execution_context(query)
        tasks = get_agent_tasks(context)

        self.assertEqual(len(tasks), 5)

        agents = [task["agent"] for task in tasks]

        self.assertEqual(
            agents,
            ["weather", "ocean", "alert", "gis", "risk"]
        )

        for task in tasks:
            self.assertEqual(task["query"], query)
            self.assertEqual(task["entities"]["location"], "Kochi")
            self.assertEqual(task["entities"]["activity"], "fishing")

    def test_weather_context(self):
        result = build_execution_context(
            "What is the weather tomorrow in Mumbai?"
        )

        self.assertEqual(result["intent"], "WEATHER")
        self.assertEqual(result["entities"]["location"], "Mumbai")
        self.assertEqual(result["entities"]["date"], "tomorrow")
        self.assertEqual(result["agents"], ["weather"])
        self.assertFalse(result["parallel"])

    def test_fishing_zone_context(self):
        result = build_execution_context(
            "Where should I fish near Kochi?"
        )

        self.assertEqual(result["intent"], "FISHING_ZONE")
        self.assertEqual(result["entities"]["location"], "Kochi")
        self.assertEqual(result["entities"]["activity"], "fishing")
        self.assertEqual(result["agents"], ["ocean", "gis"])
        self.assertTrue(result["parallel"])


if __name__ == "__main__":
    unittest.main()
