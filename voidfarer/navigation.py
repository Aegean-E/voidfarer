"""Navigation routing, jump planning, and black-hole hazard helpers."""

from __future__ import annotations

import math
from collections import deque
from typing import Any

from voidfarer.models import StarSystem

BLACK_HOLE_HAZARD = {
    "fuel_mult": 1.25,
    "encounter_mult": 1.15,
    "scan_mult": 1.40,
    "relic_find": 0.10,
}


def shortest_route(systems: dict[str, StarSystem], start_id: str, target_id: str) -> list[str]:
    if start_id == target_id:
        return [start_id]
    if start_id not in systems or target_id not in systems:
        return []
    queue: deque[list[str]] = deque([[start_id]])
    visited = {start_id}
    while queue:
        path = queue.popleft()
        current = path[-1]
        for neighbor in systems[current].connections:
            if neighbor in visited or neighbor not in systems:
                continue
            next_path = path + [neighbor]
            if neighbor == target_id:
                return next_path
            visited.add(neighbor)
            queue.append(next_path)
    return []


def route_plan(systems: dict[str, StarSystem], start_id: str, target_id: str, base_jump_fuel: int = 8) -> dict[str, Any]:
    path = shortest_route(systems, start_id, target_id)
    if not path:
        return {"reachable": False, "path": [], "jumps": 0, "distance_ly": 0.0, "fuel_estimate": 0}
    distance = 0.0
    for first, second in zip(path, path[1:]):
        a = systems[first]
        b = systems[second]
        distance += math.hypot(a.x - b.x, a.y - b.y)
    jumps = max(0, len(path) - 1)
    hazard_mult = 1.0
    if any(any(body.body_type == "black_hole" for body in systems[sid].bodies) for sid in path):
        hazard_mult = BLACK_HOLE_HAZARD["fuel_mult"]
    return {
        "reachable": True,
        "path": path,
        "jumps": jumps,
        "distance_ly": round(distance, 2),
        "fuel_estimate": max(1, int(round(base_jump_fuel * jumps * hazard_mult))),
        "black_hole_hazard": hazard_mult > 1.0,
    }


def system_has_black_hole(system: StarSystem) -> bool:
    return any(body.body_type == "black_hole" for body in system.bodies)
