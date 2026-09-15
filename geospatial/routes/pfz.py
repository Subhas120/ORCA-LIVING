"""Potential Fishing Zone utilities for ORCA M4."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Tuple

from geospatial.geo_utils.geo_utils import Coordinate, haversine_km


def load_pfz(path: str | Path) -> list[Dict[str, Any]]:
    """Load PFZ records from a JSON file."""
    with open(path, "r", encoding="utf-8-sig") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("PFZ data must be a JSON list")

    return data


def nearest_pfz(
    location: Coordinate,
    pfz_records: list[Dict[str, Any]],
) -> Dict[str, Any] | None:
    """Return the nearest PFZ and its distance from the location."""
    if not pfz_records:
        return None

    candidates = []

    for record in pfz_records:
        coordinate = (
            float(record["latitude"]),
            float(record["longitude"]),
        )

        distance = haversine_km(location, coordinate)

        candidates.append(
            {
                **record,
                "distance_km": round(distance, 3),
            }
        )

    return min(candidates, key=lambda item: item["distance_km"])
