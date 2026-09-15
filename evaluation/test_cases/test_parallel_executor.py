import asyncio
import time
import unittest

from agents.common.agent_contract import AgentRequest, AgentResponse
from agents.orchestrator.parallel_executor import execute_agents


async def slow_weather(request):
    await asyncio.sleep(0.2)

    return AgentResponse(
        agent="weather",
        status="success",
        data={"wind_speed": 18},
        source="test-weather",
        location=request.location,
        confidence=0.9,
    )


async def slow_ocean(request):
    await asyncio.sleep(0.2)

    return AgentResponse(
        agent="ocean",
        status="success",
        data={"wave_height": 2.1},
        source="test-ocean",
        location=request.location,
        confidence=0.9,
    )


async def slow_alert(request):
    await asyncio.sleep(0.2)

    return AgentResponse(
        agent="alert",
        status="success",
        data={"warning": None},
        source="test-alert",
        location=request.location,
        confidence=0.9,
    )


class TestParallelExecutor(unittest.TestCase):

    def test_agents_execute_in_parallel(self):
        requests = [
            AgentRequest(
                query="Is it safe to fish near Kochi?",
                location="Kochi",
                activity="fishing",
            ),
            AgentRequest(
                query="Is it safe to fish near Kochi?",
                location="Kochi",
                activity="fishing",
            ),
            AgentRequest(
                query="Is it safe to fish near Kochi?",
                location="Kochi",
                activity="fishing",
            ),
        ]

        agents = [
            "weather",
            "ocean",
            "alert",
        ]

        handlers = {
            "weather": slow_weather,
            "ocean": slow_ocean,
            "alert": slow_alert,
        }

        start = time.perf_counter()

        responses = asyncio.run(
            execute_agents(
                requests,
                agents,
                handlers,
            )
        )

        elapsed = time.perf_counter() - start

        self.assertEqual(len(responses), 3)

        self.assertEqual(
            [response.agent for response in responses],
            ["weather", "ocean", "alert"],
        )

        self.assertTrue(
            all(
                response.status == "success"
                for response in responses
            )
        )

        # Three 0.2 second tasks should complete close to
        # 0.2 seconds rather than approximately 0.6 seconds.
        self.assertLess(elapsed, 0.5)

    def test_missing_handler_returns_unavailable(self):
        request = AgentRequest(
            query="Is it safe near Kochi?",
            location="Kochi",
        )

        responses = asyncio.run(
            execute_agents(
                [request],
                ["weather"],
                {},
            )
        )

        self.assertEqual(len(responses), 1)
        self.assertEqual(responses[0].agent, "weather")
        self.assertEqual(responses[0].status, "unavailable")

    def test_handler_error_returns_error_response(self):
        async def broken_handler(request):
            raise RuntimeError("test failure")

        request = AgentRequest(
            query="Is it safe near Kochi?",
            location="Kochi",
        )

        responses = asyncio.run(
            execute_agents(
                [request],
                ["weather"],
                {"weather": broken_handler},
            )
        )

        self.assertEqual(len(responses), 1)
        self.assertEqual(responses[0].agent, "weather")
        self.assertEqual(responses[0].status, "error")
        self.assertEqual(responses[0].error, "test failure")


if __name__ == "__main__":
    unittest.main()
