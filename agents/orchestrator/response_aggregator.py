"""
ORCA Agent Response Aggregator

Collects and organizes responses from specialized ORCA agents.
The aggregator does not make safety decisions or calculate risk.
"""

from agents.common.agent_contract import AgentResponse


def aggregate_responses(responses: list[AgentResponse]) -> dict:
    """
    Aggregate specialized-agent responses into a single evidence context.
    """

    successful = []
    failed = []
    unavailable = []

    for response in responses:
        if not isinstance(response, AgentResponse):
            raise TypeError("All responses must be AgentResponse objects")

        if response.status == "success":
            successful.append(response)
        elif response.status == "error":
            failed.append(response)
        elif response.status == "unavailable":
            unavailable.append(response)

    return {
        "responses": responses.copy(),
        "successful": successful,
        "failed": failed,
        "unavailable": unavailable,
        "total": len(responses),
        "successful_count": len(successful),
        "failed_count": len(failed),
        "unavailable_count": len(unavailable),
    }


def get_evidence(aggregated: dict) -> list[dict]:
    """
    Extract evidence from successful agent responses.

    The original response data is preserved so downstream components
    can use source, timestamp, location, and confidence information.
    """

    evidence = []

    for response in aggregated["successful"]:
        evidence.append({
            "agent": response.agent,
            "data": response.data,
            "source": response.source,
            "timestamp": response.timestamp,
            "location": response.location,
            "confidence": response.confidence,
        })

    return evidence
