import unittest

from agents.common.agent_contract import AgentRequest, AgentResponse
from agents.ocean.ocean_agent import (
    get_marine_data,
    get_pfz_data,
    handle_ocean,
    normalize_observation,
    validate_observation,
)
from agents.ocean.safety import assess_marine_safety


class TestOceanAgent(unittest.TestCase):

    def test_normalize_observation(self):
        observation = {
            "parameter": "wave_height",
            "value": 1.2,
            "unit": "meters",
            "latitude": 9.9312,
            "longitude": 76.2673,
            "timestamp": "2026-09-10T10:00:00",
            "source": "Test Source",
            "confidence": 0.9,
        }

        result = normalize_observation(observation)

        self.assertEqual(result["parameter"], "wave_height")
        self.assertEqual(result["value"], 1.2)
        self.assertEqual(result["unit"], "meters")
        self.assertEqual(result["source"], "Test Source")
        self.assertEqual(result["confidence"], 0.9)

    def test_valid_observation(self):
        observation = {
            "parameter": "wave_height",
            "value": 1.2,
            "unit": "meters",
            "latitude": 9.9312,
            "longitude": 76.2673,
            "timestamp": "2026-09-10T10:00:00",
            "source": "Test Source",
            "confidence": 0.9,
        }

        self.assertTrue(validate_observation(observation))

    def test_invalid_observation(self):
        observation = {
            "parameter": "wave_height",
            "value": 1.2,
            "unit": "meters",
            "latitude": 9.9312,
            "longitude": 76.2673,
            "timestamp": "2026-09-10T10:00:00",
            "source": "Test Source",
        }

        self.assertFalse(validate_observation(observation))

    def test_marine_data_loading(self):
        data = get_marine_data()

        self.assertGreater(len(data), 0)

        for observation in data:
            self.assertTrue(validate_observation(observation))

    def test_pfz_data_loading(self):
        pfz_data = get_pfz_data()

        self.assertGreater(len(pfz_data), 0)
        self.assertIn("pfz_id", pfz_data[0])
        self.assertIn("latitude", pfz_data[0])
        self.assertIn("longitude", pfz_data[0])

    def test_ocean_agent_returns_agent_response(self):
        request = AgentRequest(
            query="What are the marine conditions near Kochi?",
            location="Kochi",
            date="tomorrow",
            time="morning",
            activity="fishing",
        )

        response = handle_ocean(request)

        self.assertIsInstance(response, AgentResponse)
        self.assertEqual(response.agent, "ocean")
        self.assertEqual(response.status, "success")
        self.assertEqual(response.location, "Kochi")

    def test_ocean_agent_contains_marine_parameters(self):
        request = AgentRequest(
            query="What are the marine conditions near Kochi?",
            location="Kochi",
        )

        response = handle_ocean(request)

        self.assertIn("sst", response.data)
        self.assertIn("chlorophyll", response.data)
        self.assertIn("wave_height", response.data)
        self.assertIn("wave_period", response.data)
        self.assertIn("current_speed", response.data)
        self.assertIn("marine_safety", response.data)
        self.assertIn("pfz", response.data)

    def test_marine_safety_safe(self):
        result = assess_marine_safety(1.2, 0.6)

        self.assertEqual(result["status"], "SAFE")
        self.assertEqual(result["hazards"], [])

    def test_marine_safety_unsafe(self):
        result = assess_marine_safety(3.0, 2.0)

        self.assertEqual(result["status"], "UNSAFE")
        self.assertIn("HIGH_WAVE_HEIGHT", result["hazards"])
        self.assertIn("STRONG_OCEAN_CURRENT", result["hazards"])

    def test_marine_safety_insufficient_evidence(self):
        result = assess_marine_safety(None, 0.6)

        self.assertEqual(
            result["status"],
            "INSUFFICIENT_EVIDENCE",
        )

    def test_ocean_agent_contains_safety_result(self):
        request = AgentRequest(
            query="Is it safe to fish near Kochi?",
            location="Kochi",
        )

        response = handle_ocean(request)

        safety = response.data["marine_safety"]

        self.assertIn("status", safety)
        self.assertIn("hazards", safety)
        self.assertIn("reasons", safety)
        self.assertEqual(safety["status"], "SAFE")

    def test_confidence_range(self):
        request = AgentRequest(
            query="What are the marine conditions near Kochi?",
            location="Kochi",
        )

        response = handle_ocean(request)

        self.assertIsNotNone(response.confidence)
        self.assertGreaterEqual(response.confidence, 0.0)
        self.assertLessEqual(response.confidence, 1.0)


if __name__ == "__main__":
    unittest.main()