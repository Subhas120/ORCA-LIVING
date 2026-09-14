def normalize_observation(observation: dict) -> dict:
    """
    Convert a marine observation into ORCA's standard format.
    """

    return {
        "parameter": observation["parameter"],
        "value": observation["value"],
        "unit": observation["unit"],
        "latitude": observation["latitude"],
        "longitude": observation["longitude"],
        "timestamp": observation["timestamp"],
        "source": observation["source"],
        "confidence": observation["confidence"],
    }