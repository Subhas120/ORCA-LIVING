REQUIRED_FIELDS = [
    "parameter",
    "value",
    "unit",
    "latitude",
    "longitude",
    "timestamp",
    "source",
    "confidence"
]


def validate_observation(observation):

    for field in REQUIRED_FIELDS:

        if field not in observation:
            return False

        if observation[field] is None:
            return False

    return True
