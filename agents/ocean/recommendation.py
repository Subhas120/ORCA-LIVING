STATUS_SCORE = {
    "highly_suitable": 2,
    "suitable": 1,
}


def rank_pfz_candidates(pfz_data: list[dict]) -> list[dict]:
    """Rank PFZ candidates by suitability and distance."""

    valid_candidates = []

    for candidate in pfz_data:

        status = candidate.get("status")
        distance = candidate.get("distance_km")

        if status not in STATUS_SCORE:
            continue

        if distance is None:
            continue

        candidate_copy = candidate.copy()

        candidate_copy["opportunity_score"] = STATUS_SCORE[status]

        valid_candidates.append(candidate_copy)

    return sorted(
        valid_candidates,
        key=lambda candidate: (
            -candidate["opportunity_score"],
            candidate["distance_km"],
        ),
    )


def get_pfz_recommendation(pfz_data: list[dict]) -> dict:
    """Return recommended and alternative PFZ candidates."""

    ranked_candidates = rank_pfz_candidates(pfz_data)

    if not ranked_candidates:
        return {
            "recommended": None,
            "alternatives": [],
            "rejected": [],
            "reason": "No valid PFZ candidates available",
        }

    recommended = ranked_candidates[0]

    alternatives = ranked_candidates[1:]

    rejected = []

    return {
        "recommended": recommended,
        "alternatives": alternatives,
        "rejected": rejected,
        "reason": (
            "Candidate ranked highest based on "
            "PFZ suitability and distance"
        ),
    }
