"""GeoJSON-compatible geofencing utilities for ORCA M4."""

from __future__ import annotations

from pathlib import Path
import json
from typing import Any, Dict, Iterable, Tuple

from shapely.geometry import Point, shape

Coordinate = Tuple[float, float]  # (latitude, longitude)


def coordinate_to_point(coordinate: Coordinate) -> Point:
    """Convert (latitude, longitude) to a Shapely point.

    GeoJSON uses [longitude, latitude], so the order is reversed here.
    """
    lat, lon = coordinate
    return Point(lon, lat)


def load_geojson(path: str | Path) -> Dict[str, Any]:
    """Load a GeoJSON FeatureCollection."""
    with open(path, "r", encoding="utf-8-sig") as file:
        data = json.load(file)

    if data.get("type") != "FeatureCollection":
        raise ValueError("Expected a GeoJSON FeatureCollection")

    return data


def point_in_feature(coordinate: Coordinate, feature: Dict[str, Any]) -> bool:
    """Return True when a coordinate lies inside a GeoJSON feature."""
    point = coordinate_to_point(coordinate)
    geometry = shape(feature["geometry"])
    return geometry.contains(point) or geometry.touches(point)


def find_containing_zones(
    coordinate: Coordinate,
    features: Iterable[Dict[str, Any]],
) -> list[str]:
    """Return names of zones containing the coordinate."""
    matches = []

    for feature in features:
        if point_in_feature(coordinate, feature):
            properties = feature.get("properties", {})
            name = properties.get("name", "unnamed-zone")
            matches.append(name)

    return matches


def is_location_restricted(
    coordinate: Coordinate,
    features: Iterable[Dict[str, Any]],
) -> bool:
    """Return True when a coordinate lies in a restricted zone."""
    return bool(find_containing_zones(coordinate, features))

