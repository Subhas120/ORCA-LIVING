import asyncio
import time
import unittest

from agents.common.agent_contract import AgentResponse
from agents.orchestrator.orchestrator import run_query


async def weather_handler(request):
    await asyncio.sleep(0.2)
    return AgentResponse(
        agent="weather",
        status="success",
        data={"wind_speed": 18},
        source="test-weather",
        location=request.location,
        confidence=0.9,
    )


async def ocean_handler(request):
    await asyncio.sleep(0.2)
    return AgentResponse(
        agent="ocean",
        status="success",
        data={"wave_height": 2.1},
        source="test-ocean",
        location=request.location,
        confidence=0.9,
    )


async def alert_handler(request):
    await asyncio.sleep(0.2)
    return AgentResponse(
        agent="alert",
        status="success",
        data={"warning": None},
        source="test-alert",
        location=request.location,
        confidence=0.9,
    )


class TestIntegratedParallelExecution(unittest.TestCase):

    def test_run_query_dispatches_handlers_in_parallel(self):
        query = "Is it safe to fish tomorrow near Kochi?"

        handlers = {
            "weather": weather_handler,
            "ocean": ocean_handler,
            "alert": alert_handler,
        }

        start = time.perf_counter()

        result = run_query(
            query,
            handlers=handlers,
        )

        elapsed = time.perf_counter() - start

        self.assertEqual(result["intent"], "SAFETY_CHECK")

        self.assertEqual(
            result["agents"],
            ["weather", "ocean", "alert", "gis", "risk"],
        )

        self.assertEqual(
            result["responses"]["total"],
            5,
        )

        self.assertEqual(
            result["responses"]["successful_count"],
            3,
        )

        self.assertEqual(
            result["responses"]["unavailable_count"],
            2,
        )

        self.assertLess(elapsed, 0.5)


if __name__ == "__main__":
    unittest.main()
