import unittest

from agents.common.agent_contract import AgentRequest, AgentResponse


class TestAgentRequest(unittest.TestCase):

    def test_valid_request(self):
        request = AgentRequest(
            query="Is it safe to fish near Kochi?",
            location="Kochi",
            date="tomorrow",
            activity="fishing",
        )

        self.assertEqual(request.query, "Is it safe to fish near Kochi?")
        self.assertEqual(request.location, "Kochi")
        self.assertEqual(request.activity, "fishing")

    def test_empty_query_rejected(self):
        with self.assertRaises(ValueError):
            AgentRequest(query="")


class TestAgentResponse(unittest.TestCase):

    def test_valid_success_response(self):
        response = AgentResponse(
            agent="ocean",
            status="success",
            data={"wave_height": 1.2},
            source="INCOIS",
            location="Kochi",
            confidence=0.95,
        )

        self.assertEqual(response.agent, "ocean")
        self.assertEqual(response.status, "success")
        self.assertEqual(response.data["wave_height"], 1.2)
        self.assertEqual(response.confidence, 0.95)

    def test_valid_unavailable_response(self):
        response = AgentResponse(
            agent="weather",
            status="unavailable",
            error="API unavailable",
        )

        self.assertEqual(response.status, "unavailable")
        self.assertEqual(response.error, "API unavailable")

    def test_empty_agent_rejected(self):
        with self.assertRaises(ValueError):
            AgentResponse(agent="", status="success")

    def test_invalid_status_rejected(self):
        with self.assertRaises(ValueError):
            AgentResponse(agent="ocean", status="invalid")

    def test_invalid_confidence_rejected(self):
        with self.assertRaises(ValueError):
            AgentResponse(
                agent="ocean",
                status="success",
                confidence=1.5,
            )

    def test_negative_confidence_rejected(self):
        with self.assertRaises(ValueError):
            AgentResponse(
                agent="ocean",
                status="success",
                confidence=-0.1,
            )

    def test_missing_error_rejected(self):
        with self.assertRaises(ValueError):
            AgentResponse(
                agent="ocean",
                status="error",
            )


if __name__ == "__main__":
    unittest.main()
