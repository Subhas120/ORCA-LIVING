WAVE_HEIGHT_LIMIT = 2.5
CURRENT_SPEED_LIMIT = 1.5


def assess_marine_safety(
    wave_height,
    current_speed,
):
    """
    Assess marine safety using prototype thresholds.

    Returns:
        dict containing status, hazards and reasons.
    """

    if wave_height is None or current_speed is None:
        return {
            "status": "INSUFFICIENT_EVIDENCE",
            "hazards": [],
            "reasons": [
                "Critical marine safety data is missing"
            ],
        }

    hazards = []
    reasons = []

    if wave_height > WAVE_HEIGHT_LIMIT:
        hazards.append("HIGH_WAVE_HEIGHT")

        reasons.append(
            f"Wave height {wave_height}m exceeds "
            f"the safe prototype limit of "
            f"{WAVE_HEIGHT_LIMIT}m"
        )

    if current_speed > CURRENT_SPEED_LIMIT:
        hazards.append("STRONG_OCEAN_CURRENT")

        reasons.append(
            f"Current speed {current_speed}m/s exceeds "
            f"the safe prototype limit of "
            f"{CURRENT_SPEED_LIMIT}m/s"
        )

    if hazards:
        return {
            "status": "UNSAFE",
            "hazards": hazards,
            "reasons": reasons,
        }

    return {
        "status": "SAFE",
        "hazards": [],
        "reasons": [
            "Wave height and ocean current are within "
            "prototype safety limits"
        ],
    }