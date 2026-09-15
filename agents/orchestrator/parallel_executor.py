"""
ORCA Parallel Agent Executor

Runs specialized agent handlers concurrently.
M1 owns the coordination; specialized agents remain
implemented by their respective modules.
"""

import asyncio
import inspect
from typing import Callable

from agents.common.agent_contract import AgentRequest, AgentResponse


async def _execute_handler(
    agent: str,
    request: AgentRequest,
    handler: Callable,
) -> AgentResponse:
    """
    Execute one specialized agent handler.

    Supports both async and normal synchronous handlers.
    """

    try:
        result = handler(request)

        if inspect.isawaitable(result):
            result = await result

        if not isinstance(result, AgentResponse):
            raise TypeError(
                f"{agent} handler must return AgentResponse"
            )

        return result

    except Exception as exc:
        return AgentResponse(
            agent=agent,
            status="error",
            error=str(exc),
        )


async def execute_agents(
    agent_requests: list[AgentRequest],
    agent_names: list[str],
    handlers: dict[str, Callable],
) -> list[AgentResponse]:
    """
    Execute multiple specialized agents concurrently.

    Each request is paired with the corresponding agent name.
    """

    if len(agent_requests) != len(agent_names):
        raise ValueError(
            "agent_requests and agent_names must have the same length"
        )

    tasks = []

    for agent, request in zip(agent_names, agent_requests):
        handler = handlers.get(agent)

        if handler is None:
            tasks.append(
                asyncio.create_task(
                    _missing_handler(agent)
                )
            )
        else:
            tasks.append(
                asyncio.create_task(
                    _execute_handler(agent, request, handler)
                )
            )

    return await asyncio.gather(*tasks)


async def _missing_handler(agent: str) -> AgentResponse:
    """
    Return a standardized unavailable response when an
    expected specialized agent has not been connected yet.
    """

    return AgentResponse(
        agent=agent,
        status="unavailable",
        error=f"{agent} agent handler is not connected",
    )


def execute_agents_sync(
    agent_requests: list[AgentRequest],
    agent_names: list[str],
    handlers: dict[str, Callable],
) -> list[AgentResponse]:
    """
    Synchronous wrapper for callers that are not already
    running inside an asyncio event loop.
    """

    return asyncio.run(
        execute_agents(
            agent_requests,
            agent_names,
            handlers,
        )
    )
