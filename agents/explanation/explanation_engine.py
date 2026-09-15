"""
ORCA Evidence-Based Explanation Engine

Converts structured agent and risk-engine results into
human-readable explanations.

This module explains authoritative results. It does not
change or override safety decisions.
"""

from typing import Any


VALID_RISK_LEVELS = {
    "LOW",
    "MODERATE",
    "HIGH",
    "EXTREME",
}


def _format_value(value: Any, unit: str | None = None) -> str:
    """
    Format a value for human-readable evidence.
    """

    if value is None:
        return "unknown"

    if unit:
        return f"{value} {unit}"

    return str(value)


def _format_evidence_item(
    agent: str,
    data: dict,
) -> str | None:
    """
    Convert one agent's data into a concise evidence statement.
    """

    if not data:
        return None

    if "wind_speed" in data:
        return (
            f"Wind speed is "
            f"{_format_value(data['wind_speed'], 'km/h')}."
        )

    if "wave_height" in data:
        return (
            f"Wave height is "
            f"{_format_value(data['wave_height'], 'm')}."
        )

    if "rain_probability" in data:
        return (
            f"Rain probability is "
            f"{_format_value(data['rain_probability'], '%')}."
        )

    if "visibility" in data:
        return (
            f"Visibility is "
            f"{_format_value(data['visibility'], 'km')}."
        )

    if "warning" in data and data["warning"]:
        return f"Official warning: {data['warning']}."

    return None


def build_explanation(
    risk: dict,
    evidence: list[dict],
) -> dict:
    """
    Build an evidence-based explanation from an authoritative
    risk result and supporting agent evidence.

    The risk level and score are copied from the risk engine.
    They are never recalculated or changed here.
    """

    risk_level = str(
        risk.get("level", "UNKNOWN")
    ).upper()

    score = risk.get("score")

    if risk_level not in VALID_RISK_LEVELS:
        risk_level = "UNKNOWN"

    reasons = []

    for reason in risk.get("reasons", []):
        if reason:
            reasons.append(str(reason))

    evidence_items = []

    for item in evidence:
        statement = _format_evidence_item(
            item.get("agent", "unknown"),
            item.get("data", {}),
        )

        if statement:
            evidence_items.append({
                "agent": item.get("agent"),
                "statement": statement,
                "source": item.get("source"),
                "timestamp": item.get("timestamp"),
                "location": item.get("location"),
                "confidence": item.get("confidence"),
            })

    if risk_level == "LOW":
        headline = "LOW RISK"
    elif risk_level == "MODERATE":
        headline = "MODERATE RISK"
    elif risk_level == "HIGH":
        headline = "HIGH RISK"
    elif risk_level == "EXTREME":
        headline = "EXTREME RISK"
    else:
        headline = "RISK LEVEL UNKNOWN"

    return {
        "headline": headline,
        "risk_level": risk_level,
        "risk_score": score,
        "reasons": reasons,
        "evidence": evidence_items,
    }


def render_explanation(explanation: dict) -> str:
    """
    Render a structured explanation into user-facing text.
    """

    if explanation["risk_level"] in {"HIGH", "EXTREME"}:
        prefix = "WARNING:"
    else:
        prefix = "INFO:"

    lines = [
        f"{prefix} {explanation['headline']}"
    ]

    if explanation["risk_score"] is not None:
        lines.append(
            f"Risk score: {explanation['risk_score']}/100"
        )

    if explanation["reasons"]:
        lines.append("")
        lines.append("Reasons:")

        for reason in explanation["reasons"]:
            lines.append(f"- {reason}")

    if explanation["evidence"]:
        lines.append("")
        lines.append("Evidence:")

        for item in explanation["evidence"]:
            line = f"- {item['statement']}"

            if item["source"]:
                line += f" Source: {item['source']}."

            if item["confidence"] is not None:
                line += (
                    f" Confidence: "
                    f"{item['confidence']:.2f}."
                )

            lines.append(line)

    return "\n".join(lines)
