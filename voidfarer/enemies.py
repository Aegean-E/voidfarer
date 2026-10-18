"""Hostile Enemy Archetypes, Tactical Combat AI, and Procedural Intercept Generation."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from voidfarer.models import CombatEncounter


@dataclass(frozen=True)
class EnemyArchetype:
    """Blueprint for procedural hostile intercepts across galactic territories."""

    id: str
    name: str
    enemy_class: str
    faction_id: str
    base_hull: int
    base_shield: int
    base_damage: int
    special_ability: str  # 'none', 'emp_overload', 'shield_drain', 'nanite_regen', 'tachyon_lance'
    ability_desc: str
    bounty_credits: int
    salvage_commodity: str
    rep_rewards: dict[str, int]


ENEMY_ARCHETYPES: dict[str, EnemyArchetype] = {
    "corsair_interceptor": EnemyArchetype(
        id="corsair_interceptor",
        name="Corsair Interceptor",
        enemy_class="Light Raider",
        faction_id="outlaw_corsairs",
        base_hull=60,
        base_shield=20,
        base_damage=15,
        special_ability="none",
        ability_desc="High sub-light agility with rapid kinetic projectile barrages.",
        bounty_credits=450,
        salvage_commodity="fuel_cells",
        rep_rewards={"sol_coalition": 4, "outlaw_corsairs": -6},
    ),
    "syndicate_marauder": EnemyArchetype(
        id="syndicate_marauder",
        name="Syndicate Marauder",
        enemy_class="Assault Frigate",
        faction_id="vanguard_syndicate",
        base_hull=90,
        base_shield=45,
        base_damage=22,
        special_ability="shield_drain",
        ability_desc="Siphons 15 MW energy from player shields to reinforce its own deflector grid.",
        bounty_credits=750,
        salvage_commodity="titanium",
        rep_rewards={"sol_coalition": 6, "vanguard_syndicate": -8},
    ),
    "corporate_enforcer": EnemyArchetype(
        id="corporate_enforcer",
        name="Hyperion Tactical Enforcer",
        enemy_class="Security Cruiser",
        faction_id="hyperion_dynamics",
        base_hull=110,
        base_shield=60,
        base_damage=26,
        special_ability="emp_overload",
        ability_desc="Emits an electro-magnetic burst that drains laser power and strains weapon systems.",
        bounty_credits=900,
        salvage_commodity="microchips",
        rep_rewards={"outlaw_corsairs": 6, "hyperion_dynamics": -10},
    ),
    "precursor_sentinel": EnemyArchetype(
        id="precursor_sentinel",
        name="Archon Automated Sentinel",
        enemy_class="Alien Automaton",
        faction_id="precursor_watch",
        base_hull=130,
        base_shield=80,
        base_damage=30,
        special_ability="tachyon_lance",
        ability_desc="Fires a high-frequency tachyon beam that bypasses shields directly into ship hull.",
        bounty_credits=1200,
        salvage_commodity="xenoliths",
        rep_rewards={"precursor_watch": 8, "outlaw_corsairs": 4},
    ),
    "warlord_dreadnought": EnemyArchetype(
        id="warlord_dreadnought",
        name="Void Warlord Flagship",
        enemy_class="Capital Dreadnought",
        faction_id="outlaw_corsairs",
        base_hull=200,
        base_shield=100,
        base_damage=36,
        special_ability="nanite_regen",
        ability_desc="Autonomous nanite swarms rapidly repair 20 hull damage while shields stay online.",
        bounty_credits=2500,
        salvage_commodity="xenoliths",
        rep_rewards={"sol_coalition": 15, "nebula_collective": 12, "vanguard_syndicate": 10, "outlaw_corsairs": -25},
    ),
}


def generate_system_enemy(
    system_id: str,
    security: float,
    faction: str,
    seed: int | None = None,
) -> CombatEncounter:
    """Generate a procedurally balanced CombatEncounter matching star system characteristics."""
    rng = random.Random(seed)

    # Low security boss spawn chance (Capital Dreadnought)
    if security < 0.20 and rng.random() < 0.30:
        arch = ENEMY_ARCHETYPES["warlord_dreadnought"]
    elif "pulsar" in system_id.lower() or "cygnus" in system_id.lower() or "precursor" in faction.lower():
        arch = ENEMY_ARCHETYPES["precursor_sentinel"]
    elif security >= 0.70:
        # High security corporate or light corsair infiltrator
        choices = ["corporate_enforcer", "corsair_interceptor"]
        arch = ENEMY_ARCHETYPES[rng.choice(choices)]
    elif security >= 0.35:
        # Mid security syndicate or raider
        choices = ["syndicate_marauder", "corsair_interceptor"]
        arch = ENEMY_ARCHETYPES[rng.choice(choices)]
    else:
        # Outlaw pirate infested
        choices = ["corsair_interceptor", "syndicate_marauder"]
        arch = ENEMY_ARCHETYPES[rng.choice(choices)]

    # Slight variance (+/- 10%)
    hull_var = int(arch.base_hull * rng.uniform(0.9, 1.15))
    shield_var = int(arch.base_shield * rng.uniform(0.9, 1.15))
    dmg_var = int(arch.base_damage * rng.uniform(0.95, 1.10))

    initial_telegraph = "Weapons powering up; calibrating fire control"
    if arch.special_ability == "shield_drain":
        initial_telegraph = "Energy siphon arrays locking onto flagship deflectors"
    elif arch.special_ability == "emp_overload":
        initial_telegraph = "EMP capacitors charging up for weapon disruption"
    elif arch.special_ability == "tachyon_lance":
        initial_telegraph = "Tachyon focal lenses aligning for phase-shield breach"
    elif arch.special_ability == "nanite_regen":
        initial_telegraph = "Nanite repair matrix deployed in automated standby"

    return CombatEncounter(
        id=f"combat_{system_id}_{rng.randint(100, 999)}",
        enemy_name=arch.name,
        enemy_class=arch.enemy_class,
        enemy_hull=hull_var,
        enemy_max_hull=hull_var,
        enemy_damage=dmg_var,
        bounty_credits=arch.bounty_credits,
        salvage_commodity=arch.salvage_commodity,
        enemy_shield=shield_var,
        enemy_max_shield=shield_var,
        faction_id=arch.faction_id,
        special_ability=arch.special_ability,
        ability_cooldown=0,
        telegraphed_action=initial_telegraph,
    )
