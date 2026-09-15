import unittest

from agents.orchestrator.orchestrator import run_query


class TestRouteDataFlow(unittest.TestCase):

    def test_route_destination_reaches_agent_requests(self):

        result = run_query(
            "What is the safest route from Kochi to Alappuzha?"
        )

        self.assertEqual(
            result["intent"],
            "ROUTE",
        )

        self.assertEqual(
            result["entities"]["location"],
            "Kochi",
        )

        self.assertEqual(
            result["entities"]["destination"],
            "Alappuzha",
        )

        self.assertEqual(
            len(result["agent_requests"]),
            4,
        )

        for request in result["agent_requests"]:

            self.assertEqual(
                request.location,
                "Kochi",
            )

            self.assertEqual(
                request.destination,
                "Alappuzha",
            )


if __name__ == "__main__":
    unittest.main()
