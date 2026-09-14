def normalize_observation(
    parameter,
    value,
    unit,
    latitude,
    longitude,
    timestamp,
    source,
    confidence
):

    observation = {
        "parameter": parameter,
        "value": value,
        "unit": unit,
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": timestamp,
        "source": source,
        "confidence": confidence
    }

    return observation
