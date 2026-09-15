"""Risk-aware A* route optimization for ORCA M4."""

from __future__ import annotations

import heapq
from math import hypot
from typing import Callable, Dict, Iterable, List, Optional, Set, Tuple

from shapely.geometry import Point, Polygon

from geospatial.geo_utils.geo_utils import Coordinate, haversine_km


RiskFunction = Callable[[Coordinate], float]


def _key(point: Coordinate) -> Tuple[float, float]:
    return (round(point[0], 6), round(point[1], 6))


def _grid(
    start: Coordinate,
    goal: Coordinate,
    rows: int = 15,
    cols: int = 15,
) -> Dict[Tuple[int, int], Coordinate]:
    """Create a deterministic lat/lon grid between start and goal."""
    lat1, lon1 = start
    lat2, lon2 = goal

    grid = {}

    for r in range(rows):
        for c in range(cols):
            lat = lat1 + (lat2 - lat1) * r / (rows - 1)
            lon = lon1 + (lon2 - lon1) * c / (cols - 1)
            grid[(r, c)] = (lat, lon)

    return grid


def _neighbors(
    node: Tuple[int, int],
    rows: int,
    cols: int,
) -> Iterable[Tuple[int, int]]:
    r, c = node

    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue

            nr, nc = r + dr, c + dc

            if 0 <= nr < rows and 0 <= nc < cols:
                yield nr, nc


def _blocked(
    coordinate: Coordinate,
    restricted_zones: Iterable[Polygon],
) -> bool:
    point = Point(coordinate[1], coordinate[0])
    return any(zone.contains(point) or zone.touches(point) for zone in restricted_zones)


def safest_route(
    start: Coordinate,
    goal: Coordinate,
    restricted_zones: Optional[Iterable[Polygon]] = None,
    weather_risk: Optional[RiskFunction] = None,
    wave_risk: Optional[RiskFunction] = None,
    hazard_penalty: Optional[RiskFunction] = None,
    rows: int = 15,
    cols: int = 15,
) -> Dict[str, object]:
    """Find a route using A* with distance and safety penalties.

    Cost =
        distance
        + weather risk
        + wave risk
        + hazard penalty

    Restricted-zone cells are blocked completely.
    """
    restricted = list(restricted_zones or [])

    weather_risk = weather_risk or (lambda _: 0.0)
    wave_risk = wave_risk or (lambda _: 0.0)
    hazard_penalty = hazard_penalty or (lambda _: 0.0)

    grid = _grid(start, goal, rows, cols)

    start_node = (0, 0)
    goal_node = (rows - 1, cols - 1)

    blocked_nodes: Set[Tuple[int, int]] = {
        node
        for node, coordinate in grid.items()
        if node not in (start_node, goal_node)
        and _blocked(coordinate, restricted)
    }

    open_set = [(0.0, start_node)]
    came_from: Dict[Tuple[int, int], Tuple[int, int]] = {}
    g_score = {start_node: 0.0}

    def heuristic(node: Tuple[int, int]) -> float:
        return haversine_km(grid[node], grid[goal_node])

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal_node:
            path_nodes = [current]

            while current in came_from:
                current = came_from[current]
                path_nodes.append(current)

            path_nodes.reverse()

            route = [grid[node] for node in path_nodes]

            return {
                "status": "success",
                "route": route,
                "distance_km": round(
                    sum(
                        haversine_km(route[i], route[i + 1])
                        for i in range(len(route) - 1)
                    ),
                    3,
                ),
                "blocked_cells": len(blocked_nodes),
                "algorithm": "A*",
                "cost_model": [
                    "distance",
                    "weather_risk",
                    "wave_risk",
                    "hazard_penalty",
                    "restricted_zone_block",
                ],
            }

        for neighbor in _neighbors(current, rows, cols):
            if neighbor in blocked_nodes:
                continue

            current_point = grid[current]
            neighbor_point = grid[neighbor]

            distance_cost = haversine_km(current_point, neighbor_point)
            weather_cost = max(0.0, float(weather_risk(neighbor_point)))
            wave_cost = max(0.0, float(wave_risk(neighbor_point)))
            hazard_cost = max(0.0, float(hazard_penalty(neighbor_point)))

            step_cost = (
                distance_cost
                + weather_cost
                + wave_cost
                + hazard_cost
            )

            tentative = g_score[current] + step_cost

            if tentative < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative

                f_score = tentative + heuristic(neighbor)
                heapq.heappush(open_set, (f_score, neighbor))

    return {
        "status": "unavailable",
        "route": [],
        "distance_km": None,
        "blocked_cells": len(blocked_nodes),
        "algorithm": "A*",
        "error": "No safe route found",
    }
