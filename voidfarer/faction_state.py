"""Dynamic faction leaders, behaviors, war resolution, and elimination."""

from __future__ import annotations

import random
from dataclasses import replace
from typing import Any, Sequence

from voidfarer.factions import CANONICAL_FACTIONS
from voidfarer.models import FactionLeader, StarSystem, WarState

LEADER_ARCHETYPES: dict[str, dict[str, Any]] = {
    "militarist": {"aggression": 0.85, "diplomacy": 0.25, "ambition": 0.75},
    "merchant": {"aggression": 0.30, "diplomacy": 0.75, "ambition": 0.55},
    "isolationist": {"aggression": 0.20, "diplomacy": 0.45, "ambition": 0.25},
    "opportunist": {"aggression": 0.60, "diplomacy": 0.55, "ambition": 0.85},
    "visionary": {"aggression": 0.35, "diplomacy": 0.70, "ambition": 0.65},
}

LEADER_NAMES: tuple[str, ...] = (
    "Admiral Vance", "Director Sable", "Archon Ilsa", "Warlord Kaez", "Magister Orun",
    "Consul Mira", "Captain Voss", "Prime HALCYON", "Prefect Dain", "Envoy Tessa",
)

LEADER_TITLES: tuple[str, ...] = (
    "High Admiral", "Trade Director", "Archon", "Warlord", "Magister",
    "First Consul", "Fleet Marshal", "Prime Intelligence", "Prefect", "Chief Envoy",
)


def generate_faction_leaders(seed: int) -> tuple[FactionLeader, ...]:
    """Create one deterministic leader per canonical sovereign faction."""
    rng = random.Random(int(seed) * 104_729 + 17)
    archetypes = list(LEADER_ARCHETYPES)
    leaders: list[FactionLeader] = []
    for index, (faction_id, faction) in enumerate(CANONICAL_FACTIONS.items()):
        archetype = archetypes[index % len(archetypes)]
        profile = LEADER_ARCHETYPES[archetype]
        leaders.append(FactionLeader(
            id=f"leader_{faction_id}",
            faction_id=faction_id,
            name=LEADER_NAMES[index % len(LEADER_NAMES)],
            title=LEADER_TITLES[index % len(LEADER_TITLES)],
            behavior=archetype,
            aggression=profile["aggression"],
            diplomacy=profile["diplomacy"],
            ambition=profile["ambition"],
        ))
    return tuple(leaders)


def _faction_systems(faction_id: str, systems: dict[str, StarSystem]) -> list[str]:
    target = CANONICAL_FACTIONS.get(faction_id)
    name = target.name if target else faction_id
    return [sid for sid, system in systems.items() if system.faction == name]


def faction_strength(faction_id: str, systems: dict[str, StarSystem]) -> float:
    owned = _faction_systems(faction_id, systems)
    population = sum(
        body.population
        for sid in owned
        for body in systems[sid].bodies
    )
    return len(owned) * 100.0 + population / 1_000_000.0


def resolve_wars(
    wars: Sequence[WarState],
    systems: dict[str, StarSystem],
    rng: random.Random,
    current_tick: int,
    eliminated: tuple[str, ...],
) -> tuple[tuple[WarState, ...], dict[str, StarSystem], tuple[str, ...], list[str]]:
    """Advance wars, transfer territory, and eliminate factions that lose all systems."""
    logs: list[str] = []
    updated_wars: list[WarState] = []
    updated_systems = dict(systems)
    removed = set(eliminated)
    for war in wars:
        if not war.active:
            updated_wars.append(war)
            continue
        attacker_name = CANONICAL_FACTIONS[war.attacker_id].name if war.attacker_id in CANONICAL_FACTIONS else war.attacker_id
        defender_name = CANONICAL_FACTIONS[war.defender_id].name if war.defender_id in CANONICAL_FACTIONS else war.defender_id
        score_delta = rng.uniform(-3.0, 5.0)
        new_score = war.war_score + score_delta
        if abs(new_score) >= 12.0:
            winner = war.attacker_id if new_score > 0 else war.defender_id
            loser = war.defender_id if winner == war.attacker_id else war.attacker_id
            loser_name = CANONICAL_FACTIONS[loser].name if loser in CANONICAL_FACTIONS else loser
            loser_systems = _faction_systems(loser, updated_systems)
            if loser_systems:
                captured = rng.choice(loser_systems)
                winner_name = CANONICAL_FACTIONS[winner].name if winner in CANONICAL_FACTIONS else winner
                old = updated_systems[captured]
                updated_systems[captured] = replace(old, faction=winner_name)
                logs.append(f"WAR: {winner_name} captured {old.name} from {loser_name}.")
            else:
                new_score = 0.0
        loser_now = _faction_systems(war.defender_id if new_score > 0 else war.attacker_id, updated_systems)
        if not loser_now:
            gone = war.defender_id if new_score > 0 else war.attacker_id
            if gone not in removed:
                removed.add(gone)
                logs.append(f"FACTION ELIMINATED: {gone} has no remaining territory.")
            updated_wars.append(replace(war, war_score=new_score, active=False))
        else:
            updated_wars.append(replace(war, war_score=round(new_score, 2)))
    return tuple(updated_wars), updated_systems, tuple(sorted(removed)), logs


def simulate_faction_behaviors(
    leaders: Sequence[FactionLeader],
    wars: Sequence[WarState],
    systems: dict[str, StarSystem],
    rng: random.Random,
    current_tick: int,
    eliminated: tuple[str, ...],
    num_ticks: int = 1,
) -> tuple[tuple[WarState, ...], dict[str, StarSystem], tuple[str, ...], list[str]]:
    """Apply leader archetypes: declare wars, then resolve active fronts."""
    logs: list[str] = []
    active_pairs = {frozenset((w.attacker_id, w.defender_id)) for w in wars if w.active}
    new_wars = list(wars)
    living = [
        fid for fid in CANONICAL_FACTIONS
        if fid not in eliminated and _faction_systems(fid, systems)
    ]
    if len(living) >= 2 and rng.random() < min(0.40, 0.06 * num_ticks):
        for leader in leaders:
            if leader.faction_id not in living or leader.aggression < 0.55:
                continue
            targets = [fid for fid in living if fid != leader.faction_id]
            if not targets:
                continue
            weakest = min(targets, key=lambda fid: faction_strength(fid, systems))
            pair = frozenset((leader.faction_id, weakest))
            if pair in active_pairs:
                continue
            if rng.random() > leader.aggression * 0.45:
                continue
            war = WarState(
                id=f"war_{current_tick}_{leader.faction_id}_{weakest}",
                attacker_id=leader.faction_id,
                defender_id=weakest,
                started_tick=current_tick,
            )
            new_wars.append(war)
            active_pairs.add(pair)
            attacker_name = CANONICAL_FACTIONS[leader.faction_id].name
            defender_name = CANONICAL_FACTIONS[weakest].name if weakest in CANONICAL_FACTIONS else weakest
            logs.append(f"WAR DECLARED: {attacker_name} ({leader.name}) moves against {defender_name}.")
            break

    resolved_wars, systems, eliminated_now, war_logs = resolve_wars(
        new_wars, systems, rng, current_tick, eliminated
    )
    logs.extend(war_logs)
    return resolved_wars, systems, eliminated_now, logs


def leader_for(leaders: Sequence[FactionLeader], faction_id: str) -> FactionLeader | None:
    return next((l for l in leaders if l.faction_id == faction_id), None)
