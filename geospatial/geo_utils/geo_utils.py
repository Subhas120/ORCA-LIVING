"""Core geographic utilities for ORCA M4."""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt
from typing import Tuple

Coordinate = Tuple[float, float]  # (latitude, longitude)


def validate_coordinate(point: Coordinate) -> Coordinate:
    """Validate and return a latitude/longitude coordinate."""
    lat, lon = point

    if not -90 <= lat <= 90:
        raise ValueError(f"Invalid latitude: {lat}")
    if not -180 <= lon <= 180:
        raise ValueError(f"Invalid longitude: {lon}")

    return float(lat), float(lon)


def haversine_km(a: Coordinate, b: Coordinate) -> float:
    """Return great-circle distance between two coordinates in kilometres."""
    lat1, lon1 = validate_coordinate(a)
    lat2, lon2 = validate_coordinate(b)

    earth_radius_km = 6371.008

    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)

    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)

    h = (
        sin(d_lat / 2) ** 2
        + cos(lat1_rad) * cos(lat2_rad) * sin(d_lon / 2) ** 2
    )

    return 2 * earth_radius_km * asin(sqrt(h))


def midpoint(a: Coordinate, b: Coordinate) -> Coordinate:
    """Return a simple geographic midpoint."""
    lat1, lon1 = validate_coordinate(a)
    lat2, lon2 = validate_coordinate(b)

    return ((lat1 + lat2) / 2, (lon1 + lon2) / 2)
