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
    dominant_corp: str | None = None

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
            "dominant_corp": self.dominant_corp,
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
            dominant_corp=data.get("dominant_corp"),
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
class FleetDrone:
    """Autonomous fleet asset deployed to star systems for mining, scouting, or escort."""

    id: str
    name: str
    drone_type: str  # 'mining', 'scout', 'combat_escort'
    assigned_system_id: str
    status: str = "harvesting"  # 'harvesting', 'patrolling', 'idle'
    cargo_accumulated: int = 0
    credits_accumulated: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FleetDrone:
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            drone_type=str(data["drone_type"]),
            assigned_system_id=str(data.get("assigned_system_id", "sol")),
            status=str(data.get("status", "harvesting")),
            cargo_accumulated=int(data.get("cargo_accumulated", 0)),
            credits_accumulated=int(data.get("credits_accumulated", 0)),
        )


@dataclass(frozen=True)
class ShipUpgrade:
    """Modular hardware upgrade installed on flagship."""

    id: str
    name: str
    slot: str  # 'engines', 'shields', 'sensors', 'weapons', 'cargo'
    cost: int
    description: str
    stat_bonus: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ShipUpgrade:
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            slot=str(data["slot"]),
            cost=int(data["cost"]),
            description=str(data["description"]),
            stat_bonus=dict(data.get("stat_bonus", {})),
        )


@dataclass(frozen=True)
class CombatEncounter:
    """Hostile deep-space pirate or automated intercept encounter."""

    id: str
    enemy_name: str
    enemy_class: str
    enemy_hull: int
    enemy_max_hull: int
    enemy_damage: int
    bounty_credits: int
    salvage_commodity: str = "titanium"
    enemy_shield: int = 0
    enemy_max_shield: int = 0
    faction_id: str = "outlaw_corsairs"
    special_ability: str = "none"
    ability_cooldown: int = 0
    telegraphed_action: str = "Hostile weapons powering up"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CombatEncounter:
        return cls(
            id=str(data["id"]),
            enemy_name=str(data["enemy_name"]),
            enemy_class=str(data["enemy_class"]),
            enemy_hull=int(data["enemy_hull"]),
            enemy_max_hull=int(data["enemy_max_hull"]),
            enemy_damage=int(data["enemy_damage"]),
            bounty_credits=int(data["bounty_credits"]),
            salvage_commodity=str(data.get("salvage_commodity", "titanium")),
            enemy_shield=int(data.get("enemy_shield", 0)),
            enemy_max_shield=int(data.get("enemy_max_shield", 0)),
            faction_id=str(data.get("faction_id", "outlaw_corsairs")),
            special_ability=str(data.get("special_ability", "none")),
            ability_cooldown=int(data.get("ability_cooldown", 0)),
            telegraphed_action=str(data.get("telegraphed_action", "Hostile weapons powering up")),
        )


@dataclass(frozen=True)
class BountyContract:
    """Dynamic mission contract leveraging Zeigarnik task completion tension."""

    id: str
    title: str
    description: str
    category: str  # 'combat', 'mining', 'exploration', 'trade'
    target_count: int
    current_count: int = 0
    reward_credits: int = 500
    reward_xp: int = 150
    reward_relic_tier: str | None = None
    completed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BountyContract:
        return cls(
            id=str(data["id"]),
            title=str(data["title"]),
            description=str(data["description"]),
            category=str(data.get("category", "exploration")),
            target_count=int(data.get("target_count", 1)),
            current_count=int(data.get("current_count", 0)),
            reward_credits=int(data.get("reward_credits", 500)),
            reward_xp=int(data.get("reward_xp", 150)),
            reward_relic_tier=data.get("reward_relic_tier"),
            completed=bool(data.get("completed", False)),
        )


@dataclass(frozen=True)
class PrecursorRelic:
    """Ancient artifact dropped via variable ratio schedule with passive multipliers."""

    id: str
    name: str
    rarity: str  # 'common', 'rare', 'epic', 'legendary'
    description: str
    passive_stat: str  # 'laser_dmg', 'shield_cap', 'fuel_efficiency', 'trade_margin', 'scanner_bounty'
    stat_multiplier: float  # e.g. 0.15 for +15%
    discovered_at_system: str = "sol"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PrecursorRelic:
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            rarity=str(data.get("rarity", "common")),
            description=str(data.get("description", "")),
            passive_stat=str(data.get("passive_stat", "laser_dmg")),
            stat_multiplier=float(data.get("stat_multiplier", 0.05)),
            discovered_at_system=str(data.get("discovered_at_system", "sol")),
        )


@dataclass(frozen=True)
class PilotMastery:
    """Self-Determination Theory competence framework: XP, levels, and talent specs."""

    level: int = 1
    xp: int = 0
    next_level_xp: int = 500
    talent_points: int = 0
    specializations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "xp": self.xp,
            "next_level_xp": self.next_level_xp,
            "talent_points": self.talent_points,
            "specializations": list(self.specializations),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PilotMastery:
        return cls(
            level=int(data.get("level", 1)),
            xp=int(data.get("xp", 0)),
            next_level_xp=int(data.get("next_level_xp", 500)),
            talent_points=int(data.get("talent_points", 0)),
            specializations=tuple(data.get("specializations", ())),
        )


@dataclass(frozen=True)
class TutorialStep:
    """A progressive instructional milestone in the Cadet Flight Academy."""

    id: str  # e.g., 'step_orbit', 'step_scan', 'step_trade', 'step_jump', 'step_drone', 'step_combat'
    title: str
    instruction: str
    hint: str
    description: str = ""
    action_target: str = ""
    reward_credits: int = 250
    reward_xp: int = 100
    completed: bool = False

    def __post_init__(self) -> None:
        if not self.description and self.instruction:
            object.__setattr__(self, "description", self.instruction)
        elif not self.instruction and self.description:
            object.__setattr__(self, "instruction", self.description)
        if not self.action_target and "_" in self.id:
            object.__setattr__(self, "action_target", self.id.split("_", 1)[1])

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "instruction": self.instruction,
            "description": self.description or self.instruction,
            "hint": self.hint,
            "action_target": self.action_target or (self.id.split("_", 1)[1] if "_" in self.id else ""),
            "reward_credits": self.reward_credits,
            "reward_xp": self.reward_xp,
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TutorialStep:
        inst = str(data.get("instruction") or data.get("description") or "")
        step_id = str(data["id"])
        target = str(data.get("action_target") or (step_id.split("_", 1)[1] if "_" in step_id else ""))
        return cls(
            id=step_id,
            title=str(data["title"]),
            instruction=inst,
            description=inst,
            hint=str(data.get("hint", "")),
            action_target=target,
            reward_credits=int(data.get("reward_credits", 250)),
            reward_xp=int(data.get("reward_xp", 100)),
            completed=bool(data.get("completed", False)),
        )


@dataclass(frozen=True)
class TutorialState:
    """State of the Cadet Flight Academy onboarding progression."""

    active: bool = True
    current_step_index: int = 0
    steps: tuple[TutorialStep, ...] = ()
    completed: bool = False
    skipped: bool = False

    @property
    def is_active(self) -> bool:
        return self.active and not self.completed and not self.skipped and (self.current_step_index < len(self.steps))

    @property
    def current_step(self) -> TutorialStep:
        if self.steps and 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return TutorialStep(id="none", title="Graduated", instruction="", hint="")

    def to_dict(self) -> dict[str, Any]:
        return {
            "active": self.active,
            "is_active": self.is_active,
            "current_step_index": self.current_step_index,
            "steps": [s.to_dict() for s in self.steps],
            "completed": self.completed,
            "skipped": self.skipped,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TutorialState:
        raw_steps = data.get("steps") or ()
        steps = tuple(TutorialStep.from_dict(s) for s in raw_steps)

        return cls(
            active=bool(data.get("active", True)),
            current_step_index=int(data.get("current_step_index", 0)),
            steps=steps,
            completed=bool(data.get("completed", False)),
            skipped=bool(data.get("skipped", False)),
        )


@dataclass(frozen=True)
class StoryChoice:
    """Branching story decision impacting faction alignment, rewards, and narrative path."""

    id: str
    text: str
    faction_alignment: str  # 'coalition', 'syndicate', 'precursor', 'independent'
    reward_credits: int = 0
    reward_relic_id: str | None = None
    outcome_text: str = ""
    cost_credits: int = 0

    @property
    def label(self) -> str:
        return self.text

    @property
    def consequence_summary(self) -> str:
        return self.outcome_text

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "label": self.label,
            "faction_alignment": self.faction_alignment,
            "reward_credits": self.reward_credits,
            "reward_relic_id": self.reward_relic_id,
            "outcome_text": self.outcome_text,
            "consequence_summary": self.consequence_summary,
            "cost_credits": self.cost_credits,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StoryChoice:
        return cls(
            id=str(data["id"]),
            text=str(data.get("text") or data.get("label") or ""),
            faction_alignment=str(data.get("faction_alignment", "independent")),
            reward_credits=int(data.get("reward_credits", 0)),
            reward_relic_id=data.get("reward_relic_id"),
            outcome_text=str(data.get("outcome_text") or data.get("consequence_summary") or ""),
            cost_credits=int(data.get("cost_credits", 0)),
        )


@dataclass(frozen=True)
class StoryTransmission:
    """Character audio dispatch received across the subspace radio array."""

    speaker: str
    callsign: str
    channel: str
    message: str
    timestamp_system: str = "sol"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StoryTransmission:
        return cls(
            speaker=str(data["speaker"]),
            callsign=str(data.get("callsign", "UNKNOWN")),
            channel=str(data.get("channel", "Subspace Broad-Band")),
            message=str(data["message"]),
            timestamp_system=str(data.get("timestamp_system", "sol")),
        )


@dataclass(frozen=True)
class StoryChapter:
    """An episodic narrative chapter in the Precursor Cipher campaign."""

    chapter_index: int
    title: str
    target_system_id: str | None
    objective: str
    transmission: StoryTransmission
    choices: tuple[StoryChoice, ...] = ()
    completed: bool = False
    chosen_id: str | None = None

    @property
    def id(self) -> str:
        chapter_ids = {
            0: "act1_ghost_signal",
            1: "act2_sirius_forge",
            2: "act3_eternity_gate",
        }
        return chapter_ids.get(self.chapter_index, f"act{self.chapter_index + 1}")

    @property
    def synopsis(self) -> str:
        return self.objective

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "chapter_index": self.chapter_index,
            "title": self.title,
            "target_system_id": self.target_system_id,
            "objective": self.objective,
            "synopsis": self.synopsis,
            "transmission": self.transmission.to_dict(),
            "choices": [c.to_dict() for c in self.choices],
            "completed": self.completed,
            "chosen_id": self.chosen_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StoryChapter:
        raw_tx = data.get("transmission") or {"speaker": "System", "callsign": "AI", "channel": "Local", "message": ""}
        return cls(
            chapter_index=int(data.get("chapter_index", 0)),
            title=str(data.get("title", "Prologue")),
            target_system_id=data.get("target_system_id"),
            objective=str(data.get("objective") or data.get("synopsis") or ""),
            transmission=StoryTransmission.from_dict(raw_tx),
            choices=tuple(StoryChoice.from_dict(c) for c in data.get("choices", ())),
            completed=bool(data.get("completed", False)),
            chosen_id=data.get("chosen_id"),
        )


@dataclass(frozen=True)
class StoryState:
    """Master progression tracker for narrative campaign and faction standings."""

    campaign_title: str = "The Precursor Cipher"
    current_chapter_index: int = 0
    chapters: tuple[StoryChapter, ...] = ()
    transmission_log: tuple[StoryTransmission, ...] = ()
    reputation: dict[str, int] = field(default_factory=lambda: {"coalition": 0, "syndicate": 0, "precursor": 0})
    completed: bool = False

    @property
    def active_act(self) -> int:
        return self.current_chapter_index + 1

    @property
    def current_chapter_id(self) -> str:
        if self.chapters and 0 <= self.current_chapter_index < len(self.chapters):
            return self.chapters[self.current_chapter_index].id
        return f"act{self.active_act}"

    @property
    def current_chapter(self) -> StoryChapter:
        if self.chapters and 0 <= self.current_chapter_index < len(self.chapters):
            return self.chapters[self.current_chapter_index]
        return StoryChapter(
            chapter_index=0,
            title="Epilogue",
            target_system_id=None,
            objective="All narrative objectives fulfilled.",
            transmission=StoryTransmission("Archon", "Archon-Prime", "Subspace Void", "The galaxy awakens."),
        )

    @property
    def faction_reputation(self) -> dict[str, int]:
        return self.reputation

    def to_dict(self) -> dict[str, Any]:
        return {
            "campaign_title": self.campaign_title,
            "current_chapter_index": self.current_chapter_index,
            "active_act": self.active_act,
            "current_chapter_id": self.current_chapter_id,
            "chapters": [c.to_dict() for c in self.chapters],
            "transmission_log": [t.to_dict() for t in self.transmission_log],
            "reputation": dict(self.reputation),
            "faction_reputation": dict(self.reputation),
            "completed": self.completed,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> StoryState:
        raw_chapters = data.get("chapters") or ()
        chapters = tuple(StoryChapter.from_dict(c) for c in raw_chapters)

        raw_tx = data.get("transmission_log")
        if not raw_tx and chapters:
            transmission_log = (chapters[0].transmission,)
        else:
            transmission_log = tuple(StoryTransmission.from_dict(t) for t in (raw_tx or ()))

        return cls(
            campaign_title=str(data.get("campaign_title", "The Precursor Cipher")),
            current_chapter_index=int(data.get("current_chapter_index", 0)),
            chapters=chapters,
            transmission_log=transmission_log,
            reputation=dict(data.get("reputation") or data.get("faction_reputation") or {"coalition": 0, "syndicate": 0, "precursor": 0}),
            completed=bool(data.get("completed", False)),
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
    equipped_upgrades: dict[str, str] = field(default_factory=dict)
    fleet_drones: tuple[FleetDrone, ...] = ()
    flight_log: tuple[str, ...] = ()
    streak: int = 1
    relics: tuple[PrecursorRelic, ...] = ()
    mastery: PilotMastery = field(default_factory=PilotMastery)
    active_contracts: tuple[BountyContract, ...] = ()
    tactical_combo: int = 0
    near_miss_scanner_bonus: float = 0.0
    tutorial: TutorialState = field(default_factory=TutorialState)
    story: StoryState = field(default_factory=StoryState)
    faction_standings: dict[str, int] = field(default_factory=dict)
    corp_standings: dict[str, int] = field(default_factory=dict)

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
            "equipped_upgrades": dict(self.equipped_upgrades),
            "fleet_drones": [d.to_dict() for d in self.fleet_drones],
            "flight_log": list(self.flight_log),
            "streak": self.streak,
            "relics": [r.to_dict() for r in self.relics],
            "mastery": self.mastery.to_dict(),
            "active_contracts": [c.to_dict() for c in self.active_contracts],
            "tactical_combo": self.tactical_combo,
            "near_miss_scanner_bonus": self.near_miss_scanner_bonus,
            "tutorial": self.tutorial.to_dict(),
            "story": self.story.to_dict(),
            "faction_standings": dict(self.faction_standings),
            "corp_standings": dict(self.corp_standings),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ShipState:
        story_data = data.get("story", {})
        story_rep = story_data.get("reputation", {}) if isinstance(story_data, dict) else {}
        default_factions = {
            "sol_coalition": int(story_rep.get("coalition", 0)),
            "vanguard_syndicate": int(story_rep.get("syndicate", 0)),
            "precursor_watch": int(story_rep.get("precursor", 0)),
            "nebula_collective": 0,
            "outlaw_corsairs": -15,
        }
        faction_standings = dict(data.get("faction_standings") or default_factions)

        default_corps = {
            "hyperion_dynamics": 0,
            "astraea_pharma": 0,
            "omnicorp_mining": 0,
            "nexus_cybernetics": 0,
            "vortex_fuel": 0,
        }
        corp_standings = dict(data.get("corp_standings") or default_corps)

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
            equipped_upgrades=dict(data.get("equipped_upgrades", {})),
            fleet_drones=tuple(FleetDrone.from_dict(d) for d in data.get("fleet_drones", [])),
            flight_log=tuple(data.get("flight_log", ())),
            streak=int(data.get("streak", 1)),
            relics=tuple(PrecursorRelic.from_dict(r) for r in data.get("relics", [])),
            mastery=PilotMastery.from_dict(data.get("mastery", {})),
            active_contracts=tuple(BountyContract.from_dict(c) for c in data.get("active_contracts", [])),
            tactical_combo=int(data.get("tactical_combo", 0)),
            near_miss_scanner_bonus=float(data.get("near_miss_scanner_bonus", 0.0)),
            tutorial=TutorialState.from_dict(data.get("tutorial", {})),
            story=StoryState.from_dict(data.get("story", {})),
            faction_standings=faction_standings,
            corp_standings=corp_standings,
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
    active_combat: CombatEncounter | None = None
    stats: dict[str, int] = field(default_factory=lambda: {
        "jumps": 0,
        "scans": 0,
        "trades": 0,
        "anomalies_resolved": 0,
        "combat_victories": 0,
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
            "active_combat": self.active_combat.to_dict() if self.active_combat else None,
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
        active_combat = (
            CombatEncounter.from_dict(data["active_combat"])
            if data.get("active_combat")
            else None
        )
        return cls(
            version=int(data.get("version", 1)),
            galaxy_seed=int(data.get("galaxy_seed", 42)),
            ship=ShipState.from_dict(data["ship"]),
            systems=systems,
            visited_systems=tuple(data.get("visited_systems", ())),
            active_anomaly=active_anomaly,
            active_combat=active_combat,
            stats=dict(data.get("stats", {
                "jumps": 0,
                "scans": 0,
                "trades": 0,
                "anomalies_resolved": 0,
                "combat_victories": 0,
                "credits_earned": 0,
            })),
        )
