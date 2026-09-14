def assess_uncertainty(confidence):
    """
    Convert confidence into an uncertainty level.
    Higher confidence means lower uncertainty.
    """

    if confidence is None:
        return {
            "level": "HIGH",
            "reason": "Confidence data is unavailable"
        }

    if confidence >= 0.85:
        return {
            "level": "LOW",
            "reason": "Marine data confidence is high"
        }

    if confidence >= 0.70:
        return {
            "level": "MEDIUM",
            "reason": "Marine data confidence is moderate"
        }

    return {
        "level": "HIGH",
        "reason": "Marine data confidence is low"
    }
