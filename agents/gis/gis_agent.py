"""ORCA M4 GIS Agent.

Provides geographic reasoning, PFZ lookup, geofencing, and route optimization
through the shared M1 AgentRequest/AgentResponse contract.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from shapely.geometry import shape

from agents.common.agent_contract import AgentRequest, AgentResponse
from geospatial.geo_utils.geo_utils import Coordinate
from geospatial.routes.pfz import load_pfz, nearest_pfz
from geospatial.routes.safest_route import safest_route
from geospatial.zones.geofencing import load_geojson, find_containing_zones


BASE_DIR = Path(__file__).resolve().parents[2]
PFZ_PATH = BASE_DIR / "data" / "pfz_demo.json"
ZONES_PATH = BASE_DIR / "geospatial" / "zones" / "prototype_zones.geojson"


# Prototype locations for the demo layer.
# These are not claimed as live geocoded positions.
LOCATIONS: dict[str, Coordinate] = {
    "kochi": (9.9312, 76.2673),
    "alappuzha": (9.4981, 76.3388),
    "mangalore": (12.9141, 74.8560),
    "goa": (15.4909, 73.8278),
}


def resolve_location(value: str | None) -> Coordinate | None:
    """Resolve a supported demo location to coordinates."""
    if not value:
        return None

    return LOCATIONS.get(value.strip().lower())


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_zones() -> list[Any]:
    data = load_geojson(ZONES_PATH)
    return [shape(feature["geometry"]) for feature in data["features"]]


def handle(request: AgentRequest) -> AgentResponse:
    """Handle an M4 GIS request."""
    intent = getattr(request, "intent", None)
    location = getattr(request, "location", None)
    destination = getattr(request, "destination", None)

    if intent is None and destination is not None:
        intent = "ROUTE"

    if intent == "ROUTE":
        origin = resolve_location(location)
        target = resolve_location(destination)

        if origin is None or target is None:
            return AgentResponse(
                agent="gis",
                status="error",
                data={},
                source="ORCA GIS prototype",
                timestamp=_timestamp(),
                location=location,
                confidence=0.0,
                error="Unsupported route location. Prototype supports Kochi, Alappuzha, Mangalore and Goa.",
            )

        route_result = safest_route(
            origin,
            target,
            restricted_zones=_load_zones(),
        )

        if route_result["status"] != "success":
            return AgentResponse(
                agent="gis",
                status="unavailable",
                data=route_result,
                source="ORCA GIS prototype",
                timestamp=_timestamp(),
                location=location,
                confidence=0.0,
                error=str(route_result.get("error", "No safe route found")),
            )

        return AgentResponse(
            agent="gis",
            status="success",
            data={
                "origin": {
                    "name": location,
                    "latitude": origin[0],
                    "longitude": origin[1],
                },
                "destination": {
                    "name": destination,
                    "latitude": target[0],
                    "longitude": target[1],
                },
                "route": route_result["route"],
                "distance_km": route_result["distance_km"],
                "algorithm": route_result["algorithm"],
                "blocked_cells": route_result["blocked_cells"],
                "restricted_zone_policy": "blocked",
                "cost_model": route_result["cost_model"],
            },
            source="ORCA GIS prototype",
            timestamp=_timestamp(),
            location=location,
            confidence=0.85,
            error=None,
        )

    if intent in {"PFZ", "FISHING"}:
        coordinate = resolve_location(location)

        if coordinate is None:
            return AgentResponse(
                agent="gis",
                status="error",
                data={},
                source="ORCA GIS prototype",
                timestamp=_timestamp(),
                location=location,
                confidence=0.0,
                error="Unsupported PFZ location.",
            )

        pfz = nearest_pfz(coordinate, load_pfz(PFZ_PATH))

        return AgentResponse(
            agent="gis",
            status="success",
            data={"nearest_pfz": pfz},
            source="ORCA prototype PFZ data",
            timestamp=_timestamp(),
            location=location,
            confidence=float(pfz["confidence"]) if pfz else 0.0,
            error=None,
        )

    return AgentResponse(
        agent="gis",
        status="unavailable",
        data={},
        source="ORCA GIS prototype",
        timestamp=_timestamp(),
        location=location,
        confidence=0.0,
        error=f"GIS agent does not support intent: {intent}",
    )
