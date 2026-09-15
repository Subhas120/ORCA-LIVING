"""
ORCA Agent Orchestrator

Coordinates specialized ORCA agents according to the execution
plan produced by the Planner.
"""

from agents.intent.intent_extractor import analyze_query
from agents.planner.planner import create_plan
from agents.common.agent_contract import AgentRequest, AgentResponse
from agents.context.context_manager import ConversationContext
from agents.validation.query_validator import (
    validate_query,
    get_clarification_message,
)
from agents.orchestrator.response_aggregator import aggregate_responses
from agents.orchestrator.response_aggregator import get_evidence
from agents.orchestrator.parallel_executor import execute_agents_sync
from agents.explanation.explanation_engine import (
    build_explanation,
    render_explanation,
)


def build_execution_context(
    query: str,
    context: ConversationContext | None = None,
) -> dict:

    analysis = analyze_query(query)

    entities = {
        "location": analysis["location"],
        "destination": analysis["destination"],
        "date": analysis["date"],
        "time": analysis["time"],
        "activity": analysis["activity"],
    }

    if context is not None:
        entities = context.fill_missing(entities)

    plan = create_plan(analysis["intent"])

    return {
        "query": query,
        "intent": analysis["intent"],
        "entities": entities,
        "agents": plan["agents"],
        "parallel": plan["parallel"],
    }


def get_agent_tasks(execution_context: dict) -> list:

    tasks = []

    for agent in execution_context["agents"]:

        tasks.append({
            "agent": agent,
            "query": execution_context["query"],
            "entities": execution_context["entities"].copy(),
        })

    return tasks


def create_agent_requests(
    execution_context: dict,
) -> list[AgentRequest]:

    requests = []

    entities = execution_context["entities"]

    for agent in execution_context["agents"]:

        requests.append(
            AgentRequest(
                query=execution_context["query"],
                location=entities["location"],
                destination=entities["destination"],
                date=entities["date"],
                time=entities["time"],
                activity=entities["activity"],
            )
        )

    return requests


def run_query(
    query: str,
    responses: list[AgentResponse] | None = None,
    handlers: dict | None = None,
    context: ConversationContext | None = None,
    risk: dict | None = None,
) -> dict:

    execution_context = build_execution_context(
        query,
        context=context,
    )

    validation = validate_query(
        execution_context["intent"],
        execution_context["entities"],
    )

    if not validation["valid"]:

        return {
            "query": query,
            "intent": execution_context["intent"],
            "entities": execution_context["entities"],
            "agents": [],
            "parallel": False,
            "agent_requests": [],
            "responses": aggregate_responses([]),
            "evidence": [],
            "risk": risk,
            "explanation": None,
            "rendered_explanation": None,
            "validation": validation,
            "clarification": get_clarification_message(
                execution_context["intent"],
                validation["missing"],
            ),
        }

    if context is not None:
        context.update(
            execution_context["entities"]
        )

    agent_requests = create_agent_requests(
        execution_context
    )

    if handlers is not None:

        responses = execute_agents_sync(
            agent_requests=agent_requests,
            agent_names=execution_context["agents"],
            handlers=handlers,
        )

    elif responses is None:

        responses = []

    aggregated = aggregate_responses(
        responses
    )

    evidence = get_evidence(
        aggregated
    )

    explanation = None
    rendered_explanation = None

    if risk is not None:

        explanation = build_explanation(
            risk,
            evidence,
        )

        rendered_explanation = render_explanation(
            explanation,
        )

    return {
        "query": query,
        "intent": execution_context["intent"],
        "entities": execution_context["entities"],
        "agents": execution_context["agents"],
        "parallel": execution_context["parallel"],
        "agent_requests": agent_requests,
        "responses": aggregated,
        "evidence": evidence,
        "risk": risk,
        "explanation": explanation,
        "rendered_explanation": rendered_explanation,
        "validation": validation,
        "clarification": None,
    }


if __name__ == "__main__":

    query = "Is it safe to fish tomorrow near Kochi?"

    result = run_query(query)

    print("ORCA Execution Result:")
    print(result)
