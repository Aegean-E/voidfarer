"""Procedural galaxy generator, celestial orbital mechanics, and market economy."""

from __future__ import annotations

import math
import random
from dataclasses import replace
from typing import Sequence

from voidfarer.models import (
    AnomalyChoice,
    AnomalyEncounter,
    CelestialBody,
    Commodity,
    MarketQuote,
    StarSystem,
)

CANONICAL_COMMODITIES: tuple[Commodity, ...] = (
    Commodity(id="fuel_cells", name="Quantum Fuel Cells", category="industrial", base_price=50, volatility=0.15, volume=1),
    Commodity(id="titanium", name="Titanium Alloy", category="raw", base_price=120, volatility=0.25, volume=2),
    Commodity(id="hydroponics", name="Hydroponic Nutrients", category="agricultural", base_price=40, volatility=0.20, volume=1),
    Commodity(id="medicines", name="Cryo-Antibiotics", category="medical", base_price=220, volatility=0.30, volume=1),
    Commodity(id="microchips", name="Quantum Substrates", category="tech", base_price=450, volatility=0.35, volume=1),
    Commodity(id="xenoliths", name="Xenolith Relics", category="contraband", base_price=950, volatility=0.50, volume=3),
)

COMMODITY_MAP: dict[str, Commodity] = {c.id: c for c in CANONICAL_COMMODITIES}

SYSTEM_ARCHETYPES = [
    ("sol", "Sol System", 0.0, 0.0, "G", "#ffd700", 1.0, "Sol Coalition", "hyperion_dynamics"),
    ("alpha_centauri", "Alpha Centauri", 18.0, 12.0, "K", "#ffaa44", 0.9, "Sol Coalition", "astraea_pharma"),
    ("sirius", "Sirius Prime", -22.0, 15.0, "A", "#cce6ff", 0.85, "Free Spacers Syndicate", "nexus_cybernetics"),
    ("procyon", "Procyon Nexus", 10.0, -28.0, "F", "#fff4e6", 0.8, "Free Spacers Syndicate", "nexus_cybernetics"),
    ("vega", "Vega Outpost", -35.0, -18.0, "A", "#99ccff", 0.65, "Nebula Collective", "omnicorp_mining"),
    ("arcturus", "Arcturus Foundry", 32.0, 30.0, "K", "#ff7733", 0.55, "Nebula Collective", "omnicorp_mining"),
    ("betelgeuse", "Betelgeuse Forge", -45.0, 38.0, "M", "#ff3333", 0.40, "Free Spacers Syndicate", "vortex_fuel"),
    ("cygnus_x1", "Cygnus Void Gate", 48.0, -35.0, "BlackHole", "#8833ff", 0.15, "Void Corsairs", None),
    ("pulsar_psr", "PSR Core Beacon", -15.0, 52.0, "Neutron", "#33ffff", 0.20, "Precursor Watch", None),
    ("rift_station", "The Dark Abyss", 55.0, 42.0, "M", "#cc2255", 0.05, "Void Corsairs", None),
]

ANOMALIES_CATALOG = [
    {
        "id": "derelict_cruiser",
        "title": "Derelict Dreadnought Beacon",
        "description": "Long-range sensors detect a silent decommissioned battlecruiser drifting in an unstable gravitational vortex.",
        "severity": "moderate",
        "choices": [
            {
                "choice_id": "salvage_hull",
                "text": "Send automated salvage drones to breach the cargo bay (Needs Shields >= 35%)",
                "required_power": "shields",
                "min_power_threshold": 35,
                "outcome_text": "Drones safely deflect orbital debris and recover valuable titanium alloys and credits.",
                "hull_delta": 0,
                "credits_delta": 450,
                "fuel_delta": -5,
                "cargo_reward": {"titanium": 4},
            },
            {
                "choice_id": "download_logs",
                "text": "Align sensor array to decrypt encrypted black-box memory (Needs Sensors >= 40%)",
                "required_power": "sensors",
                "min_power_threshold": 40,
                "outcome_text": "Sensor harmonics decrypt the memory core, uncovering navigational telemetry and rare quantum substrate schematics.",
                "hull_delta": 0,
                "credits_delta": 600,
                "fuel_delta": -3,
                "cargo_reward": {"microchips": 2},
            },
            {
                "choice_id": "emergency_jump",
                "text": "Reroute power to sub-light engines and clear the hazard perimeter",
                "required_power": "engines",
                "min_power_threshold": 20,
                "outcome_text": "The engines push the ship clear of the debris field without taking hull damage.",
                "hull_delta": 0,
                "credits_delta": 0,
                "fuel_delta": -2,
                "cargo_reward": {},
            },
        ],
    },
    {
        "id": "tachyon_rift",
        "title": "Tachyon Space-Time Anomaly",
        "description": "A miniature tachyon rift pulses rhythmically, distorting chronometric sensors and emitting Cherenkov luminescence.",
        "severity": "critical",
        "choices": [
            {
                "choice_id": "harmonic_drain",
                "text": "Calibrate shield harmonics to harvest tachyon flux energy (Needs Shields >= 45%)",
                "required_power": "shields",
                "min_power_threshold": 45,
                "outcome_text": "Shield arrays absorb the gravitational surge, supercharging the ship's hyperdrive fuel reserves.",
                "hull_delta": 0,
                "credits_delta": 300,
                "fuel_delta": 25,
                "cargo_reward": {"fuel_cells": 3},
            },
            {
                "choice_id": "xenolith_extraction",
                "text": "Fire focused pulse laser to destabilize crystallizing vacuum nodes (Needs Weapons >= 40%)",
                "required_power": "weapons",
                "min_power_threshold": 40,
                "outcome_text": "Coherent laser fire cleaves dense exotic crystals from the vortex. Xenolith relics recovered!",
                "hull_delta": -10,
                "credits_delta": 800,
                "fuel_delta": -5,
                "cargo_reward": {"xenoliths": 1},
            },
            {
                "choice_id": "scan_and_retreat",
                "text": "Execute passive sensor pass and stand off (Needs Sensors >= 25%)",
                "required_power": "sensors",
                "min_power_threshold": 25,
                "outcome_text": "Sensors log valuable astrophysical telemetry before radiation reaches danger levels.",
                "hull_delta": 0,
                "credits_delta": 250,
                "fuel_delta": -1,
                "cargo_reward": {},
            },
        ],
    },
    {
        "id": "stranded_freighter",
        "title": "Distress Signal: Merchant Cryo-Freighter",
        "description": "An automated SOS broadcast originates from a disabled civilian transport surrounded by micro-meteors.",
        "severity": "minor",
        "choices": [
            {
                "choice_id": "transfer_fuel",
                "text": "Transfer 5 fuel units and assist with repairs (Needs Engines >= 30%)",
                "required_power": "engines",
                "min_power_threshold": 30,
                "outcome_text": "The grateful crew awards you a generous credit bounty and fresh medical supplies.",
                "hull_delta": 0,
                "credits_delta": 500,
                "fuel_delta": -5,
                "cargo_reward": {"medicines": 3},
            },
            {
                "choice_id": "escort_tow",
                "text": "Lock tractor beam and escort them out of the meteor swarm (Needs Shields >= 35%)",
                "required_power": "shields",
                "min_power_threshold": 35,
                "outcome_text": "Shields withstand the impact cascade. The transport authority pays a substantial rescue bonus.",
                "hull_delta": -5,
                "credits_delta": 750,
                "fuel_delta": -4,
                "cargo_reward": {"hydroponics": 5},
            },
            {
                "choice_id": "ignore_distress",
                "text": "Log the coordinates and continue on current heading",
                "required_power": "none",
                "min_power_threshold": 0,
                "outcome_text": "You log the beacon and maintain your patrol corridor.",
                "hull_delta": 0,
                "credits_delta": 0,
                "fuel_delta": 0,
                "cargo_reward": {},
            },
        ],
    },
]


class GalaxyGenerator:
    """Generates deterministic star systems, celestial bodies, and hyperlane corridors."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.rng = random.Random(seed)

    def generate_galaxy(self) -> dict[str, StarSystem]:
        """Generate connected star systems across the sector."""
        systems: dict[str, StarSystem] = {}

        # 1. Create base systems
        for (
            sys_id,
            name,
            x,
            y,
            spectral,
            color,
            sec,
            faction,
            dominant_corp,
        ) in SYSTEM_ARCHETYPES:
            bodies = self._generate_bodies(sys_id, name, spectral)
            systems[sys_id] = StarSystem(
                id=sys_id,
                name=name,
                seed=self.rng.randint(1000, 99999),
                x=x,
                y=y,
                spectral_type=spectral,
                color=color,
                security=sec,
                faction=faction,
                bodies=tuple(bodies),
                connections=(),
                dominant_corp=dominant_corp,
            )

        # 2. Build hyperlane mesh ensuring full graph connectivity
        connections = self._build_hyperlanes(systems)
        final_systems: dict[str, StarSystem] = {}
        for s_id, s_obj in systems.items():
            final_systems[s_id] = StarSystem(
                id=s_obj.id,
                name=s_obj.name,
                seed=s_obj.seed,
                x=s_obj.x,
                y=s_obj.y,
                spectral_type=s_obj.spectral_type,
                color=s_obj.color,
                security=s_obj.security,
                faction=s_obj.faction,
                bodies=s_obj.bodies,
                connections=tuple(sorted(connections[s_id])),
                dominant_corp=s_obj.dominant_corp,
            )
        return final_systems

    def _generate_bodies(
        self, sys_id: str, sys_name: str, spectral: str
    ) -> list[CelestialBody]:
        """Generate central star and orbiting planetary bodies."""
        bodies: list[CelestialBody] = []

        # Central primary star
        star_color = "#ffd700" if spectral == "G" else ("#99ccff" if spectral == "A" else "#ff5533")
        bodies.append(
            CelestialBody(
                id=f"{sys_id}_star",
                name=f"{sys_name} Primary",
                body_type="star",
                orbit_radius=0.0,
                orbit_speed=0.0,
                current_angle=0.0,
                radius_km=696340.0,
                color=star_color,
                hazards=("solar_radiation",),
                station_dockable=False,
                market_archetype="none",
                scan_completed=True,
                scan_discovery="Main-sequence stellar furnace emitting radiant plasma.",
            )
        )

        archetype_pool = [
            ("terrestrial", "mineral_rich", "mining", "#d4a373", "Rich subterranean veins of rare heavy metals."),
            ("oceanic", "habitable", "agricultural", "#48cae4", "Atmospheric bio-spheres generating organic nutrients."),
            ("gas_giant", "hydrogen_storm", "industrial", "#f4a261", "Upper atmospheric siphon extracting deuterium isotopes."),
            ("orbital_station", "citadel", "high_tech", "#00f0ff", "Orbital manufacturing enclave producing quantum substrates."),
            ("asteroid_belt", "debris_field", "mining", "#8d99ae", "Shattered planetesimals harboring raw titanium ores."),
            ("desert_world", "silicate_plains", "mining", "#e9c46a", "Sun-scorched dunes concealing rare silicate crystal seams."),
            ("ice_world", "cryo_ocean", "agricultural", "#a8dadc", "Subsurface cryo-oceans teeming with cultivable extremophiles."),
            ("lava_world", "magma_forge", "industrial", "#e76f51", "Tectonic magma vents powering automated heavy foundries."),
            ("ringed_giant", "helium_harvest", "industrial", "#c9ada7", "Ringed gas envelope mined for helium-3 and exotic isotopes."),
            ("research_outpost", "science", "high_tech", "#b5179e", "Deep-space research campus studying precursor field harmonics."),
        ]

        if sys_id in ("betelgeuse", "cygnus_x1", "rift_station"):
            archetype_pool.append(
                ("volcanic", "dark_market", "black_market", "#e63946", "Unregulated shadow bazaar trafficking illicit xenoliths.")
            )

        num_bodies = 6 if sys_id in ("sol", "betelgeuse") else 5
        for i in range(num_bodies):
            body_type, designation, market_arch, color, discovery = archetype_pool[
                (i + len(sys_id)) % len(archetype_pool)
            ]
            orbit_dist = 1.0 + (i + 1) * 1.35
            orbit_speed = 0.08 / (i + 1)
            is_station = body_type == "orbital_station"

            bodies.append(
                CelestialBody(
                    id=f"{sys_id}_body_{i+1}",
                    name=f"{sys_name} {chr(65+i)} ({designation.title()})",
                    body_type=body_type,
                    orbit_radius=orbit_dist,
                    orbit_speed=orbit_speed,
                    current_angle=(i * 1.6) % (2 * math.pi),
                    radius_km=3000.0 + i * 2500.0,
                    color=color,
                    hazards=("pirate_activity",) if market_arch == "black_market" else (),
                    station_dockable=is_station or (body_type in ("terrestrial", "oceanic")),
                    market_archetype=market_arch,
                    scan_completed=False,
                    scan_discovery=discovery,
                )
            )

        if not any(b.station_dockable for b in bodies[1:]):
            bodies[-1] = replace(
                bodies[-1],
                body_type="orbital_station",
                color="#00f0ff",
                hazards=(),
                station_dockable=True,
                market_archetype="high_tech",
                scan_discovery="Orbital trade citadel servicing deep-space convoys.",
            )

        return bodies

    def _build_hyperlanes(
        self, systems: dict[str, StarSystem]
    ) -> dict[str, set[str]]:
        """Calculate hyperlane network ensuring a fully connected graph."""
        adj: dict[str, set[str]] = {k: set() for k in systems}
        sys_list = list(systems.values())

        # Connect closest neighbors
        for s1 in sys_list:
            distances = []
            for s2 in sys_list:
                if s1.id != s2.id:
                    dist = math.hypot(s1.x - s2.x, s1.y - s2.y)
                    distances.append((dist, s2.id))
            distances.sort()
            # Link at least the 2 nearest neighbors
            for _, target_id in distances[:2]:
                adj[s1.id].add(target_id)
                adj[target_id].add(s1.id)

        # Connect spanning links to avoid islands
        for i in range(len(sys_list) - 1):
            s_a = sys_list[i].id
            s_b = sys_list[i + 1].id
            adj[s_a].add(s_b)
            adj[s_b].add(s_a)

        return adj

    @staticmethod
    def get_market_quotes(
        system: StarSystem, body: CelestialBody
    ) -> list[MarketQuote]:
        """Compute localized commodity market pricing based on archetype and security."""
        quotes: list[MarketQuote] = []
        sec = system.security
        arch = body.market_archetype

        for comm in CANONICAL_COMMODITIES:
            base = comm.base_price
            supply = 50
            demand = 50

            # Archetype price adjustments
            if arch == "mining":
                if comm.id == "titanium":
                    supply = 120
                    demand = 20
                    base = int(base * 0.70)
                elif comm.id in ("hydroponics", "microchips"):
                    supply = 15
                    demand = 110
                    base = int(base * 1.35)
            elif arch == "agricultural":
                if comm.id == "hydroponics":
                    supply = 140
                    demand = 15
                    base = int(base * 0.65)
                elif comm.id in ("titanium", "medicines"):
                    supply = 20
                    demand = 100
                    base = int(base * 1.30)
            elif arch == "high_tech":
                if comm.id == "microchips":
                    supply = 110
                    demand = 25
                    base = int(base * 0.75)
                elif comm.id in ("titanium", "fuel_cells"):
                    supply = 30
                    demand = 120
                    base = int(base * 1.25)
            elif arch == "black_market":
                if comm.id == "xenoliths":
                    supply = 60
                    demand = 150
                    base = int(base * 1.60)
                elif comm.id == "medicines":
                    supply = 30
                    demand = 130
                    base = int(base * 1.40)

            # Security modifier (anarchy drives up fuel and risk premiums)
            if sec < 0.3:
                if comm.id in ("fuel_cells", "medicines"):
                    base = int(base * 1.25)

            # Spread calculation
            spread = max(2, int(base * 0.12))
            buy_price = base + spread
            sell_price = max(1, base - spread)

            quotes.append(
                MarketQuote(
                    commodity_id=comm.id,
                    name=comm.name,
                    category=comm.category,
                    buy_price=buy_price,
                    sell_price=sell_price,
                    supply=supply,
                    demand=demand,
                )
            )

        return quotes

    @staticmethod
    def get_random_anomaly(seed: int | None = None) -> AnomalyEncounter:
        """Select and instantiate a deep-space anomaly event."""
        rng = random.Random(seed)
        chosen = rng.choice(ANOMALIES_CATALOG)
        return AnomalyEncounter.from_dict(chosen)
