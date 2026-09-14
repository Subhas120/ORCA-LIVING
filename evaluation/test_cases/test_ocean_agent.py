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
    get_pfz_recommendation,
    rank_pfz_candidates,
)
from agents.ocean.uncertainty import assess_uncertainty


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

        self.assertEqual(
            result["parameter"],
            "wave_height",
        )
        self.assertEqual(result["value"], 1.2)
        self.assertEqual(result["unit"], "meters")
        self.assertEqual(
            result["source"],
            "Test Source",
        )
        self.assertEqual(
            result["confidence"],
            0.9,
        )

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

        self.assertTrue(
            validate_observation(observation)
        )

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

        self.assertFalse(
            validate_observation(observation)
        )

    def test_marine_data_loading(self):
        data = get_marine_data()

        self.assertGreater(len(data), 0)

        for observation in data:
            self.assertTrue(
                validate_observation(observation)
            )

    def test_pfz_data_loading(self):
        pfz_data = get_pfz_data()

        self.assertGreater(len(pfz_data), 0)

        self.assertIn(
            "pfz_id",
            pfz_data[0],
        )

        self.assertIn(
            "latitude",
            pfz_data[0],
        )

        self.assertIn(
            "longitude",
            pfz_data[0],
        )

    def test_ocean_agent_returns_agent_response(self):
        request = AgentRequest(
            query="What are the marine conditions near Kochi?",
            location="Kochi",
            date="tomorrow",
            time="morning",
            activity="fishing",
        )

        response = handle_ocean(request)

        self.assertIsInstance(
            response,
            AgentResponse,
        )

        self.assertEqual(
            response.agent,
            "ocean",
        )

        self.assertEqual(
            response.status,
            "success",
        )

        self.assertEqual(
            response.location,
            "Kochi",
        )

    def test_confidence_range(self):
        request = AgentRequest(
            query="What are the marine conditions near Kochi?",
            location="Kochi",
        )

        response = handle_ocean(request)

        self.assertIsNotNone(
            response.confidence
        )

        self.assertGreaterEqual(
            response.confidence,
            0.0,
        )

        self.assertLessEqual(
            response.confidence,
            1.0,
        )

    def test_marine_safety_safe(self):
        result = assess_marine_safety(
            1.2,
            0.6,
        )

        self.assertEqual(
            result["status"],
            "SAFE",
        )

    def test_marine_safety_unsafe(self):
        result = assess_marine_safety(
            3.0,
            2.0,
        )

        self.assertEqual(
            result["status"],
            "UNSAFE",
        )

        self.assertIn(
            "HIGH_WAVE_HEIGHT",
            result["hazards"],
        )

        self.assertIn(
            "STRONG_OCEAN_CURRENT",
            result["hazards"],
        )

    def test_marine_safety_insufficient_evidence(self):
        result = assess_marine_safety(
            None,
            0.6,
        )

        self.assertEqual(
            result["status"],
            "INSUFFICIENT_EVIDENCE",
        )

    def test_pfz_ranking(self):
        pfz_data = get_pfz_data()

        ranked = rank_pfz_candidates(pfz_data)

        self.assertGreater(
            len(ranked),
            0,
        )

        self.assertEqual(
            ranked[0]["pfz_id"],
            "PFZ_KOCHI_02",
        )

    def test_pfz_recommendation(self):
        pfz_data = get_pfz_data()

        result = get_pfz_recommendation(
            pfz_data
        )

        self.assertIn(
            "recommended",
            result,
        )

        self.assertIn(
            "alternatives",
            result,
        )

        self.assertIn(
            "rejected",
            result,
        )

        self.assertEqual(
            result["recommended"]["pfz_id"],
            "PFZ_KOCHI_02",
        )

    def test_ocean_agent_contains_recommendation(self):
        request = AgentRequest(
            query="Find a fishing zone near Kochi",
            location="Kochi",
            activity="fishing",
        )

        response = handle_ocean(request)

        self.assertIn(
            "pfz_recommendation",
            response.data,
        )

        recommendation = response.data[
            "pfz_recommendation"
        ]

        self.assertIn(
            "recommended",
            recommendation,
        )

    def test_uncertainty_low(self):
        result = assess_uncertainty(0.9)

        self.assertEqual(
            result["level"],
            "LOW",
        )

    def test_uncertainty_medium(self):
        result = assess_uncertainty(0.75)

        self.assertEqual(
            result["level"],
            "MEDIUM",
        )

    def test_uncertainty_high(self):
        result = assess_uncertainty(0.5)

        self.assertEqual(
            result["level"],
            "HIGH",
        )

    def test_ocean_agent_contains_uncertainty(self):
        request = AgentRequest(
            query="What are the marine conditions near Kochi?",
            location="Kochi",
        )

        response = handle_ocean(request)

        self.assertIn(
            "uncertainty",
            response.data,
        )

        uncertainty = response.data[
            "uncertainty"
        ]

        self.assertIn(
            "level",
            uncertainty,
        )

        self.assertIn(
            "reason",
            uncertainty,
        )

    def test_m2_response_contract(self):
        request = AgentRequest(
            query="What are the marine conditions near Kochi?",
            location="Kochi",
            date="tomorrow",
            time="morning",
            activity="fishing",
        )

        response = handle_ocean(request)

        # Top-level contract
        self.assertEqual(
            response.agent,
            "ocean",
        )

        self.assertIn(
            response.status,
            [
                "success",
                "error",
                "unavailable",
            ],
        )

        self.assertIsNotNone(
            response.location
        )

        self.assertIsNotNone(
            response.timestamp
        )

        self.assertIsNotNone(
            response.confidence
        )

        # Successful response contract
        if response.status == "success":

            self.assertIn(
                "marine_safety",
                response.data,
            )

            self.assertIn(
                "uncertainty",
                response.data,
            )

            self.assertIn(
                "pfz",
                response.data,
            )

            self.assertIn(
                "pfz_recommendation",
                response.data,
            )

            self.assertIn(
                "evidence",
                response.data,
            )

            # Safety contract
            safety = response.data[
                "marine_safety"
            ]

            self.assertIn(
                "status",
                safety,
            )

            self.assertIn(
                "hazards",
                safety,
            )

            self.assertIn(
                "reasons",
                safety,
            )

            # Uncertainty contract
            uncertainty = response.data[
                "uncertainty"
            ]

            self.assertIn(
                "level",
                uncertainty,
            )

            self.assertIn(
                "reason",
                uncertainty,
            )

            # Recommendation contract
            recommendation = response.data[
                "pfz_recommendation"
            ]

            self.assertIn(
                "recommended",
                recommendation,
            )

            self.assertIn(
                "alternatives",
                recommendation,
            )

            self.assertIn(
                "rejected",
                recommendation,
            )

            self.assertIn(
                "reason",
                recommendation,
            )

    def test_recommended_candidate_contract(self):
        request = AgentRequest(
            query="Find a fishing zone near Kochi",
            location="Kochi",
            activity="fishing",
        )

        response = handle_ocean(request)

        recommended = response.data[
            "pfz_recommendation"
        ]["recommended"]

        self.assertIsNotNone(
            recommended
        )

        required_fields = [
            "pfz_id",
            "latitude",
            "longitude",
            "distance_km",
            "status",
            "source",
            "confidence",
        ]

        for field in required_fields:
            self.assertIn(
                field,
                recommended,
            )


if __name__ == "__main__":
    unittest.main()