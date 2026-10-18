"""Hardware upgrade catalog, fleet drone definitions, and equipment registry."""

from __future__ import annotations

from typing import Sequence

from voidfarer.models import FleetDrone, ShipUpgrade

CATALOG_UPGRADES: tuple[ShipUpgrade, ...] = (
    ShipUpgrade(
        id="warp_booster_mk2",
        name="Hyperdrive Booster MK-II",
        slot="engines",
        cost=850,
        description="Quantum field accelerator reducing hyperlane jump fuel burn by 35%.",
        stat_bonus={"fuel_efficiency": 0.35},
    ),
    ShipUpgrade(
        id="tachyon_shield_matrix",
        name="Tachyon Shield Matrix",
        slot="shields",
        cost=1100,
        description="High-frequency deflector array augmenting shield capacity by +40 MW.",
        stat_bonus={"max_shield": 40.0},
    ),
    ShipUpgrade(
        id="deep_core_scanner",
        name="Deep-Core Astrometric Array",
        slot="sensors",
        cost=750,
        description="Sub-space sensor array boosting planetary scan science bounties by +50%.",
        stat_bonus={"scan_mult": 1.5},
    ),
    ShipUpgrade(
        id="pulse_cannon_array",
        name="Coherent Laser Strike Battery",
        slot="weapons",
        cost=950,
        description="Focused laser battery delivering +15 hull damage in tactical combat.",
        stat_bonus={"combat_damage": 15.0},
    ),
    ShipUpgrade(
        id="subspace_cargo_pods",
        name="Sub-Space Expanded Cargo Hold",
        slot="cargo",
        cost=600,
        description="Dimensional compression cargo pods expanding hold capacity by +20 units.",
        stat_bonus={"cargo_capacity": 20.0},
    ),
)

UPGRADE_MAP: dict[str, ShipUpgrade] = {u.id: u for u in CATALOG_UPGRADES}

CATALOG_DRONE_TEMPLATES = {
    "mining": {
        "name": "Automated Mining Drone",
        "type": "mining",
        "cost": 650,
        "description": "Extracts raw titanium and minerals in assigned star system each flight cycle.",
    },
    "scout": {
        "name": "Deep-Space Recon Drone",
        "type": "scout",
        "cost": 500,
        "description": "Monitors spatial harmonics and yields steady research credits.",
    },
    "combat_escort": {
        "name": "Vanguard Escort Frigate",
        "type": "combat_escort",
        "cost": 1300,
        "description": "Heavy automated gunboat providing point-defense against pirate ambushes.",
    },
}


def get_upgrade(upgrade_id: str) -> ShipUpgrade | None:
    return UPGRADE_MAP.get(upgrade_id)


def get_available_upgrades(installed: dict[str, str]) -> list[ShipUpgrade]:
    """Return upgrades that have not yet been installed."""
    installed_ids = set(installed.values())
    return [u for u in CATALOG_UPGRADES if u.id not in installed_ids]
