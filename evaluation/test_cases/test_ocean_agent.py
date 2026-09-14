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
from agents.ocean.recommendation import (
    rank_pfz_candidates,
    get_pfz_recommendation,
)


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
        }

        self.assertFalse(validate_observation(observation))

    def test_marine_data_loading(self):
        data = get_marine_data()

        self.assertGreater(len(data), 0)

    def test_pfz_data_loading(self):
        pfz_data = get_pfz_data()

        self.assertGreater(len(pfz_data), 0)
        self.assertIn("pfz_id", pfz_data[0])

    def test_ocean_agent_returns_agent_response(self):
        request = AgentRequest(
            query="What are the marine conditions near Kochi?",
            location="Kochi",
        )

        response = handle_ocean(request)

        self.assertIsInstance(response, AgentResponse)
        self.assertEqual(response.agent, "ocean")
        self.assertEqual(response.status, "success")

    def test_marine_safety_safe(self):
        result = assess_marine_safety(1.2, 0.6)

        self.assertEqual(result["status"], "SAFE")

    def test_marine_safety_unsafe(self):
        result = assess_marine_safety(3.0, 2.0)

        self.assertEqual(result["status"], "UNSAFE")

    def test_marine_safety_insufficient_evidence(self):
        result = assess_marine_safety(None, 0.6)

        self.assertEqual(
            result["status"],
            "INSUFFICIENT_EVIDENCE",
        )

    def test_pfz_ranking(self):
        pfz_data = get_pfz_data()

        ranked = rank_pfz_candidates(pfz_data)

        self.assertEqual(
            ranked[0]["pfz_id"],
            "PFZ_KOCHI_02",
        )

    def test_pfz_recommendation(self):
        pfz_data = get_pfz_data()

        recommendation = get_pfz_recommendation(
            pfz_data
        )

        self.assertEqual(
            recommendation["recommended"]["pfz_id"],
            "PFZ_KOCHI_02",
        )

        self.assertEqual(
            recommendation["alternatives"][0]["pfz_id"],
            "PFZ_KOCHI_01",
        )

    def test_ocean_agent_contains_recommendation(self):
        request = AgentRequest(
            query="Where should I fish near Kochi?",
            location="Kochi",
        )

        response = handle_ocean(request)

        self.assertIn(
            "pfz_recommendation",
            response.data,
        )

        recommendation = response.data[
            "pfz_recommendation"
        ]

        self.assertIsNotNone(
            recommendation["recommended"]
        )

        self.assertEqual(
            recommendation["recommended"]["pfz_id"],
            "PFZ_KOCHI_02",
        )

    def test_confidence_range(self):
        request = AgentRequest(
            query="What are the marine conditions near Kochi?",
            location="Kochi",
        )

        response = handle_ocean(request)

        self.assertGreaterEqual(
            response.confidence,
            0.0,
        )

        self.assertLessEqual(
            response.confidence,
            1.0,
        )


if __name__ == "__main__":
    unittest.main()