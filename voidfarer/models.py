"""Domain state models and frozen data transfer objects for VoidFarer."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class CelestialBody:
    """Represents a planetary, stellar, or orbital body in a star system."""

    id: str
    name: str
    body_type: str  # 'star', 'terrestrial', 'gas_giant', 'oceanic', 'volcanic', 'orbital_station', 'asteroid_belt'
    orbit_radius: float  # In Astronomical Units (AU)
    orbit_speed: float  # Orbital angular velocity
    current_angle: float  # Current orbital phase (radians)
    radius_km: float
    color: str  # Hex display color
    hazards: tuple[str, ...] = ()
    station_dockable: bool = False
    market_archetype: str = "none"  # 'none', 'mining', 'agricultural', 'industrial', 'high_tech', 'black_market'
    scan_completed: bool = False
    scan_discovery: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CelestialBody:
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            body_type=str(data["body_type"]),
            orbit_radius=float(data["orbit_radius"]),
            orbit_speed=float(data.get("orbit_speed", 0.05)),
            current_angle=float(data.get("current_angle", 0.0)),
            radius_km=float(data.get("radius_km", 6000.0)),
            color=str(data.get("color", "#00f0ff")),
            hazards=tuple(data.get("hazards", ())),
            station_dockable=bool(data.get("station_dockable", False)),
            market_archetype=str(data.get("market_archetype", "none")),
            scan_completed=bool(data.get("scan_completed", False)),
            scan_discovery=str(data.get("scan_discovery", "")),
        )


@dataclass(frozen=True)
class StarSystem:
    """Represents a star system with celestial bodies and hyperlane links."""

    id: str
    name: str
    seed: int
    x: float
    y: float
    spectral_type: str  # 'O', 'B', 'A', 'F', 'G', 'K', 'M', 'Neutron', 'BlackHole'
    color: str
    security: float  # 0.0 (anarchy) to 1.0 (high-sec)
    faction: str
    bodies: tuple[CelestialBody, ...]
    connections: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "seed": self.seed,
            "x": self.x,
            "y": self.y,
            "spectral_type": self.spectral_type,
            "color": self.color,
            "security": self.security,
            "faction": self.faction,
            "bodies": [b.to_dict() for b in self.bodies],
            "connections": list(self.connections),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StarSystem:
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            seed=int(data["seed"]),
            x=float(data["x"]),
            y=float(data["y"]),
            spectral_type=str(data["spectral_type"]),
            color=str(data.get("color", "#ffffff")),
            security=float(data.get("security", 0.5)),
            faction=str(data.get("faction", "Independent")),
            bodies=tuple(CelestialBody.from_dict(b) for b in data.get("bodies", [])),
            connections=tuple(data.get("connections", ())),
        )


@dataclass(frozen=True)
class Commodity:
    """Trade goods and planetary resources."""

    id: str
    name: str
    category: str  # 'raw', 'industrial', 'medical', 'tech', 'contraband'
    base_price: int
    volatility: float
    volume: int = 1


@dataclass(frozen=True)
class MarketQuote:
    """Current price quotation for a commodity at a local market."""

    commodity_id: str
    name: str
    category: str
    buy_price: int
    sell_price: int
    supply: int
    demand: int


@dataclass(frozen=True)
class ShipPower:
    """Reactor power distribution across primary subsystems (sum <= 100)."""

    engines: int = 25
    shields: int = 25
    sensors: int = 25
    weapons: int = 25

    def __post_init__(self) -> None:
        total = self.engines + self.shields + self.sensors + self.weapons
        if total > 100:
            raise ValueError(f"Total allocated power ({total}%) exceeds reactor capacity (100%)")
        if any(p < 0 for p in (self.engines, self.shields, self.sensors, self.weapons)):
            raise ValueError("Subsystem power cannot be negative")

    def to_dict(self) -> dict[str, int]:
        return {
            "engines": self.engines,
            "shields": self.shields,
            "sensors": self.sensors,
            "weapons": self.weapons,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ShipPower:
        return cls(
            engines=int(data.get("engines", 25)),
            shields=int(data.get("shields", 25)),
            sensors=int(data.get("sensors", 25)),
            weapons=int(data.get("weapons", 25)),
        )


@dataclass(frozen=True)
class AnomalyChoice:
    """Player decision branch for resolving a deep-space anomaly encounter."""

    choice_id: str
    text: str
    required_power: str  # 'engines', 'shields', 'sensors', 'weapons', 'none'
    min_power_threshold: int
    outcome_text: str
    hull_delta: int = 0
    credits_delta: int = 0
    fuel_delta: int = 0
    cargo_reward: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnomalyChoice:
        return cls(
            choice_id=str(data["choice_id"]),
            text=str(data["text"]),
            required_power=str(data.get("required_power", "none")),
            min_power_threshold=int(data.get("min_power_threshold", 0)),
            outcome_text=str(data["outcome_text"]),
            hull_delta=int(data.get("hull_delta", 0)),
            credits_delta=int(data.get("credits_delta", 0)),
            fuel_delta=int(data.get("fuel_delta", 0)),
            cargo_reward=dict(data.get("cargo_reward", {})),
        )


@dataclass(frozen=True)
class AnomalyEncounter:
    """Procedurally triggered deep-space anomaly event."""

    id: str
    title: str
    description: str
    severity: str  # 'minor', 'moderate', 'critical'
    choices: tuple[AnomalyChoice, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "choices": [c.to_dict() for c in self.choices],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AnomalyEncounter:
        return cls(
            id=str(data["id"]),
            title=str(data["title"]),
            description=str(data["description"]),
            severity=str(data.get("severity", "moderate")),
            choices=tuple(AnomalyChoice.from_dict(c) for c in data.get("choices", [])),
        )


@dataclass(frozen=True)
class ShipState:
    """Complete telemetry, resource inventory, and status of the player's flagship."""

    commander_name: str
    callsign: str
    ship_class: str
    hull: int
    max_hull: int
    shield: int
    max_shield: int
    fuel: int
    max_fuel: int
    credits: int
    cargo: dict[str, int]
    cargo_capacity: int
    current_system_id: str
    orbiting_body_id: str | None
    power: ShipPower = field(default_factory=ShipPower)
    upgrades: tuple[str, ...] = ()
    flight_log: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "commander_name": self.commander_name,
            "callsign": self.callsign,
            "ship_class": self.ship_class,
            "hull": self.hull,
            "max_hull": self.max_hull,
            "shield": self.shield,
            "max_shield": self.max_shield,
            "fuel": self.fuel,
            "max_fuel": self.max_fuel,
            "credits": self.credits,
            "cargo": dict(self.cargo),
            "cargo_capacity": self.cargo_capacity,
            "current_system_id": self.current_system_id,
            "orbiting_body_id": self.orbiting_body_id,
            "power": self.power.to_dict(),
            "upgrades": list(self.upgrades),
            "flight_log": list(self.flight_log),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ShipState:
        return cls(
            commander_name=str(data.get("commander_name", "Valerius")),
            callsign=str(data.get("callsign", "Aegis-7")),
            ship_class=str(data.get("ship_class", "Vanguard Explorer")),
            hull=int(data.get("hull", 100)),
            max_hull=int(data.get("max_hull", 100)),
            shield=int(data.get("shield", 100)),
            max_shield=int(data.get("max_shield", 100)),
            fuel=int(data.get("fuel", 50)),
            max_fuel=int(data.get("max_fuel", 50)),
            credits=int(data.get("credits", 1500)),
            cargo=dict(data.get("cargo", {})),
            cargo_capacity=int(data.get("cargo_capacity", 30)),
            current_system_id=str(data.get("current_system_id", "sol")),
            orbiting_body_id=data.get("orbiting_body_id"),
            power=ShipPower.from_dict(data.get("power", {})),
            upgrades=tuple(data.get("upgrades", ())),
            flight_log=tuple(data.get("flight_log", ())),
        )


@dataclass(frozen=True)
class GameState:
    """Master simulation universe state container."""

    version: int
    galaxy_seed: int
    ship: ShipState
    systems: dict[str, StarSystem]
    visited_systems: tuple[str, ...]
    active_anomaly: AnomalyEncounter | None = None
    stats: dict[str, int] = field(default_factory=lambda: {
        "jumps": 0,
        "scans": 0,
        "trades": 0,
        "anomalies_resolved": 0,
        "credits_earned": 0,
    })

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "galaxy_seed": self.galaxy_seed,
            "ship": self.ship.to_dict(),
            "systems": {k: v.to_dict() for k, v in self.systems.items()},
            "visited_systems": list(self.visited_systems),
            "active_anomaly": self.active_anomaly.to_dict() if self.active_anomaly else None,
            "stats": dict(self.stats),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GameState:
        systems = {
            k: StarSystem.from_dict(v)
            for k, v in data.get("systems", {}).items()
        }
        active_anomaly = (
            AnomalyEncounter.from_dict(data["active_anomaly"])
            if data.get("active_anomaly")
            else None
        )
        return cls(
            version=int(data.get("version", 1)),
            galaxy_seed=int(data.get("galaxy_seed", 42)),
            ship=ShipState.from_dict(data["ship"]),
            systems=systems,
            visited_systems=tuple(data.get("visited_systems", ())),
            active_anomaly=active_anomaly,
            stats=dict(data.get("stats", {
                "jumps": 0,
                "scans": 0,
                "trades": 0,
                "anomalies_resolved": 0,
                "credits_earned": 0,
            })),
        )
