"""Deterministic state machine and simulation engine for VoidFarer."""

from __future__ import annotations

from dataclasses import asdict, replace
import math
import random
import threading
from typing import Any, Sequence

from voidfarer.enemies import (
    ENEMY_ARCHETYPES,
    choose_enemy_intent,
    generate_system_enemy,
)
from voidfarer.factions import (
    CANONICAL_CORPORATIONS,
    CANONICAL_FACTIONS,
    calculate_faction_market_modifier,
    get_corporation,
    get_faction,
    get_faction_id_from_name,
    get_faction_service_perks,
    get_faction_standing_tier,
)
from voidfarer.economy import (
    MAX_STOCK,
    MIN_STOCK,
    calculate_dynamic_market_quote,
    generate_initial_economy,
    get_galactic_trade_routes,
    tick_global_economy,
)
from voidfarer.inventory import (
    ITEM_CATALOG,
    calculate_cargo_volume,
    get_inventory_manifest,
    get_item_info,
)
from voidfarer.galaxy import (
    CANONICAL_COMMODITIES,
    COMMODITY_MAP,
    GalaxyGenerator,
    compute_scientific_planet_properties,
)
from voidfarer.models import (
    AICaptain,
    BountyContract,
    CelestialBody,
    CombatEncounter,
    Depot,
    EconomicEvent,
    FleetDrone,
    GameEvent,
    GameState,
    GlobalEconomyState,
    MarketQuote,
    PilotMastery,
    PrecursorRelic,
    QuantumMessage,
    ShipPower,
    ShipState,
    ShipUpgrade,
    StarSystem,
    StoryChapter,
    StoryChoice,
    StoryState,
    StoryTransmission,
    SystemMarketState,
    TimeState,
    TravelState,
    TutorialState,
    TutorialStep,
)
from voidfarer.frontier import (
    MERCENARY_CATALOG,
    generate_ai_captains,
    generate_depots,
    generate_welcome_messages,
    simulate_ai_trade,
)
from voidfarer.retention import (
    CATALOG_RELICS,
    PILOT_TALENTS,
    calculate_passive_multipliers,
    generate_contract,
    generate_initial_contracts,
    roll_relic_drop,
)
from voidfarer.story import (
    CAMPAIGN_CHAPTERS,
    INITIAL_TUTORIAL_STEPS,
    STORY_RELICS,
    generate_initial_story,
    generate_initial_tutorial,
)
from voidfarer.upgrades import (
    CATALOG_CHASSIS,
    CATALOG_DRONE_TEMPLATES,
    CATALOG_UPGRADES,
    CHASSIS_MAP,
    UPGRADE_MAP,
    calculate_equipment_bonuses,
    get_available_chassis,
    get_available_upgrades,
    get_chassis,
    get_sell_value,
    get_upgrade,
)


class SimulationEngine:
    """Coordinates space flight, star navigation, fleet drones, upgrades, and tactical combat."""

    def __init__(self, seed: int = 42, state: GameState | None = None) -> None:
        self.lock = threading.Lock()
        self.seed = seed
        self.rng = random.Random(seed)

        if state is not None:
            ship = state.ship
            tut = ship.tutorial
            if not tut.steps and not tut.completed and not tut.skipped:
                tut = generate_initial_tutorial()
            st = ship.story
            if not st.chapters:
                st = generate_initial_story()
            self.state = state
            new_ship = self._clone_ship(tutorial=tut, story=st) if (tut != ship.tutorial or st != ship.story) else ship
            econ = state.economy
            if not econ or not econ.markets:
                econ = generate_initial_economy(state.systems, self.rng)
            if new_ship != ship or econ != state.economy:
                self.state = self._clone_state(ship=new_ship, economy=econ)
        else:
            self.state = self._create_initial_state(seed)
        self._bootstrap_frontier()

    def _bootstrap_frontier(self) -> None:
        """Backfill frontier systems for legacy saves without changing the save schema."""
        updates: dict[str, Any] = {}
        if not self.state.ai_captains:
            updates["ai_captains"] = generate_ai_captains(self.state.systems, self.state.galaxy_seed)
        if not self.state.depots:
            updates["depots"] = generate_depots(self.state.systems)
        if not self.state.messages:
            updates["messages"] = generate_welcome_messages(self.state.time.tick)
        gov_map = {
            "Sol Coalition": "Federal Democracy",
            "Free Spacers Syndicate": "Trade Directorate",
            "Nebula Collective": "Technocratic Council",
            "Void Corsairs": "Pirate Warlordship",
            "Precursor Watch": "Monastic Curate",
        }
        updated_systems: dict[str, StarSystem] = {}
        systems_changed = False
        for sys_id, sys_obj in self.state.systems.items():
            new_bodies = []
            body_changed = False
            for idx, body in enumerate(sys_obj.bodies):
                updated_body = body
                if (updated_body.station_dockable or updated_body.landable) and updated_body.population == 0:
                    pop = 120_000_000 + idx * 45_000_000 if updated_body.landable else 250_000 + idx * 85_000
                    gov = "Science Directorate" if updated_body.body_type == "research_outpost" else gov_map.get(sys_obj.faction, "Colonial Republic")
                    updated_body = replace(
                        updated_body,
                        faction=sys_obj.faction if updated_body.faction == "Unclaimed" else updated_body.faction,
                        population=pop,
                        government=gov if updated_body.government == "None" else updated_body.government,
                    )
                    body_changed = True
                if updated_body.body_type != "star" and ("(" not in updated_body.atmosphere or (updated_body.habitability == 0.0 and updated_body.body_type not in ("gas_giant", "ringed_giant", "ice_giant", "methane_storm", "lava_world"))):
                    rad_seed = 4000.0 + ((idx + len(sys_id)) % 9) * 6500.0
                    grav_seed = 0.65 + ((idx * 3 + len(sys_id)) % 7) * 0.22
                    jitter_seed = ((idx * 5 + len(sys_id)) % 9) - 4
                    phys = compute_scientific_planet_properties(
                        body_type=updated_body.body_type,
                        spectral_type=sys_obj.spectral_type,
                        orbit_radius_au=updated_body.orbit_radius,
                        rad_sample=rad_seed,
                        grav_sample=grav_seed,
                        temp_jitter=jitter_seed,
                        hazards=updated_body.hazards,
                    )
                    updated_body = replace(
                        updated_body,
                        radius_km=float(phys["radius_km"]),
                        gravity=float(phys["gravity"]),
                        atmosphere=str(phys["atmosphere"]),
                        temperature_c=int(phys["temperature_c"]),
                        habitability=float(phys["habitability"]),
                    )
                    body_changed = True
                new_bodies.append(updated_body)
            if body_changed:
                updated_systems[sys_id] = replace(sys_obj, bodies=tuple(new_bodies))
                systems_changed = True
            else:
                updated_systems[sys_id] = sys_obj
        if systems_changed:
            updates["systems"] = updated_systems
        if updates:
            self.state = self._clone_state(**updates)

    def _clone_ship(self, **kwargs: Any) -> ShipState:
        """Create a new ShipState preserving all unspecified telemetry and inventory attributes."""
        cur = self.state.ship
        return ShipState(
            commander_name=kwargs.get("commander_name", cur.commander_name),
            callsign=kwargs.get("callsign", cur.callsign),
            ship_class=kwargs.get("ship_class", cur.ship_class),
            hull=kwargs.get("hull", cur.hull),
            max_hull=kwargs.get("max_hull", cur.max_hull),
            shield=kwargs.get("shield", cur.shield),
            max_shield=kwargs.get("max_shield", cur.max_shield),
            fuel=kwargs.get("fuel", cur.fuel),
            max_fuel=kwargs.get("max_fuel", cur.max_fuel),
            credits=kwargs.get("credits", cur.credits),
            cargo=kwargs.get("cargo", cur.cargo),
            cargo_capacity=kwargs.get("cargo_capacity", cur.cargo_capacity),
            current_system_id=kwargs.get("current_system_id", cur.current_system_id),
            orbiting_body_id=kwargs.get("orbiting_body_id", cur.orbiting_body_id),
            power=kwargs.get("power", cur.power),
            upgrades=kwargs.get("upgrades", cur.upgrades),
            equipped_upgrades=kwargs.get("equipped_upgrades", cur.equipped_upgrades),
            fleet_drones=kwargs.get("fleet_drones", cur.fleet_drones),
            flight_log=kwargs.get("flight_log", cur.flight_log),
            streak=kwargs.get("streak", cur.streak),
            relics=kwargs.get("relics", cur.relics),
            mastery=kwargs.get("mastery", cur.mastery),
            active_contracts=kwargs.get("active_contracts", cur.active_contracts),
            tactical_combo=kwargs.get("tactical_combo", cur.tactical_combo),
            near_miss_scanner_bonus=kwargs.get("near_miss_scanner_bonus", cur.near_miss_scanner_bonus),
            tutorial=kwargs.get("tutorial", cur.tutorial),
            story=kwargs.get("story", cur.story),
            faction_standings=kwargs.get("faction_standings", cur.faction_standings),
            corp_standings=kwargs.get("corp_standings", cur.corp_standings),
            allies=kwargs.get("allies", cur.allies),
            landed_body_id=kwargs["landed_body_id"] if "landed_body_id" in kwargs else cur.landed_body_id,
            travel=kwargs["travel"] if "travel" in kwargs else cur.travel,
        )

    def _clone_state(self, **kwargs: Any) -> GameState:
        """Create a new GameState preserving time, stats, economy, and all unspecified universe fields."""
        cur = self.state
        return GameState(
            version=kwargs.get("version", cur.version),
            galaxy_seed=kwargs.get("galaxy_seed", cur.galaxy_seed),
            ship=kwargs.get("ship", cur.ship),
            systems=kwargs.get("systems", cur.systems),
            visited_systems=kwargs.get("visited_systems", cur.visited_systems),
            active_anomaly=kwargs["active_anomaly"] if "active_anomaly" in kwargs else cur.active_anomaly,
            active_combat=kwargs["active_combat"] if "active_combat" in kwargs else cur.active_combat,
            time=kwargs.get("time", cur.time),
            stats=kwargs.get("stats", cur.stats),
            economy=kwargs.get("economy", cur.economy),
            ai_captains=kwargs.get("ai_captains", cur.ai_captains),
            depots=kwargs.get("depots", cur.depots),
            messages=kwargs.get("messages", cur.messages),
            events=kwargs.get("events", cur.events),
        )

    def _grant_cargo(self, cargo: dict[str, int], commodity_id: str, quantity: int) -> tuple[int, int]:
        """Add as many units as the hold allows, returning (granted, overflow)."""
        unit_volume = max(1, calculate_cargo_volume({commodity_id: 1}))
        free_volume = self.state.ship.cargo_capacity - calculate_cargo_volume(cargo)
        granted = min(max(0, int(quantity)), max(0, free_volume // unit_volume))
        if granted > 0:
            cargo[commodity_id] = cargo.get(commodity_id, 0) + granted
        return granted, int(quantity) - granted

    def _apply_relic_stat_bonuses(
        self,
        hull: int,
        max_hull: int,
        shield: int,
        max_shield: int,
        relics: Sequence[PrecursorRelic],
    ) -> tuple[int, int, int, int]:
        """Raise current and maximum hull/shield for newly acquired permanent relics."""
        for relic in relics:
            stats = dict(relic.bonuses)
            stats[relic.passive_stat] = stats.get(relic.passive_stat, 0.0) + relic.stat_multiplier
            if relic.passive_stat == "stellar_forge":
                stats.setdefault("shield_cap", 40.0)
            if "max_hull" in stats:
                bonus = int(stats["max_hull"])
                max_hull += bonus
                hull += bonus
            if "shield_cap" in stats:
                bonus = int(stats["shield_cap"])
                max_shield += bonus
                shield += bonus
        return hull, max_hull, shield, max_shield

    def _progress_tutorial(self, action_type: str) -> tuple[TutorialState, int, int, list[PrecursorRelic], list[str]]:
        """Advance the Cadet Flight Academy if current step requirement is satisfied."""
        cur = self.state.ship.tutorial
        if not cur.active or cur.completed or cur.skipped:
            return cur, 0, 0, [], []

        if cur.current_step_index >= len(cur.steps):
            return cur, 0, 0, [], []

        current_step = cur.steps[cur.current_step_index]
        match_map = {
            "step_orbit": "orbit",
            "step_scan": "scan",
            "step_power": "power",
            "step_trade": "trade",
            "step_drone": "drone",
            "step_jump": "jump",
        }

        if match_map.get(current_step.id) != action_type:
            return cur, 0, 0, [], []

        updated_steps = list(cur.steps)
        updated_steps[cur.current_step_index] = TutorialStep(
            id=current_step.id,
            title=current_step.title,
            instruction=current_step.instruction,
            hint=current_step.hint,
            reward_credits=current_step.reward_credits,
            reward_xp=current_step.reward_xp,
            completed=True,
        )

        credits_awarded = current_step.reward_credits
        xp_awarded = current_step.reward_xp
        relics_awarded: list[PrecursorRelic] = []
        logs: list[str] = [
            f"ACADEMY STEP COMPLETE: [{current_step.title}] finished (+{current_step.reward_credits} cr, +{current_step.reward_xp} XP)!"
        ]

        next_idx = cur.current_step_index + 1
        is_all_done = next_idx >= len(cur.steps)

        if is_all_done:
            credits_awarded += 1500
            xp_awarded += 400
            cadet_wings = STORY_RELICS.get("relic_cadet_wings")
            if cadet_wings:
                relics_awarded.append(cadet_wings)
            logs.append("🎓 ACADEMY GRADUATION: Commander Astraea has graduated from the Cadet Flight Academy! Awarded Cadet Honor Wings (+1,500 cr, +400 XP).")

        new_tutorial = TutorialState(
            active=cur.active,
            current_step_index=next_idx,
            steps=tuple(updated_steps),
            completed=is_all_done,
            skipped=cur.skipped,
        )
        return new_tutorial, credits_awarded, xp_awarded, relics_awarded, logs

    def _award_pilot_xp(self, amount: int, current_mastery: PilotMastery) -> tuple[PilotMastery, list[str]]:
        """Award experience points and compute level promotions and talent points."""
        new_xp = current_mastery.xp + amount
        level = current_mastery.level
        next_xp = max(1, current_mastery.next_level_xp)
        points = current_mastery.talent_points
        logs: list[str] = []

        while new_xp >= next_xp:
            new_xp -= next_xp
            level += 1
            points += 1
            next_xp = int(next_xp * 1.5)
            logs.append(f"★ PILOT PROMOTION: Reached Pilot Mastery Level {level}! Earned +1 Specialization Point.")

        return PilotMastery(
            level=level,
            xp=new_xp,
            next_level_xp=next_xp,
            talent_points=points,
            specializations=current_mastery.specializations,
        ), logs

    def _progress_contracts(self, category: str, amount: int = 1) -> tuple[tuple[BountyContract, ...], list[str]]:
        """Advance matching active contracts toward completion objectives."""
        updated: list[BountyContract] = []
        logs: list[str] = []
        for c in self.state.ship.active_contracts:
            if c.category == category and not c.completed:
                new_cnt = min(c.target_count, c.current_count + amount)
                is_done = new_cnt >= c.target_count
                updated.append(
                    BountyContract(
                        id=c.id,
                        title=c.title,
                        description=c.description,
                        category=c.category,
                        target_count=c.target_count,
                        current_count=new_cnt,
                        reward_credits=c.reward_credits,
                        reward_xp=c.reward_xp,
                        reward_relic_tier=c.reward_relic_tier,
                        completed=is_done,
                    )
                )
                if is_done:
                    logs.append(f"OBJECTIVE COMPLETE: [{c.title}] ready to claim ({c.reward_credits} cr, {c.reward_xp} XP)!")
            else:
                updated.append(c)
        return tuple(updated), logs

    def reset(self, seed: int = 42) -> tuple[bool, str]:
        """Reset the simulation to a fresh galaxy with an isolated deterministic RNG stream."""
        with self.lock:
            self.seed = int(seed)
            self.rng = random.Random(self.seed)
            self.state = self._create_initial_state(self.seed)
            return True, "Simulation reset to factory state."

    def load_state(self, state: GameState) -> tuple[bool, str]:
        """Replace the live universe with a loaded save and reseed its RNG stream."""
        with self.lock:
            self.seed = int(state.galaxy_seed)
            self.rng = random.Random(self.seed)
            self.state = state
            self._bootstrap_frontier()
            return True, f"Loaded save at {state.time.current_date} (tick #{state.time.tick})."

    def _create_initial_state(self, seed: int) -> GameState:
        """Construct a fresh universe state rooted at Sol System."""
        generator = GalaxyGenerator(seed=seed)
        systems = generator.generate_galaxy()
        initial_contracts = generate_initial_contracts(self.rng)

        ship = ShipState(
            commander_name="Astraea",
            callsign="VF-Vanguard",
            ship_class="Corvette Scout",
            hull=100,
            max_hull=100,
            shield=100,
            max_shield=100,
            fuel=60,
            max_fuel=60,
            credits=2000,
            cargo={"fuel_cells": 5, "hydroponics": 10},
            cargo_capacity=40,
            current_system_id="sol",
            orbiting_body_id="sol_body_1",
            power=ShipPower(engines=30, shields=25, sensors=25, weapons=20),
            upgrades=("Pulse Scanner MK-I", "Shield Buffer"),
            equipped_upgrades={},
            fleet_drones=(
                FleetDrone(
                    id="drone_mining_1",
                    name="Mining Drone Alpha",
                    drone_type="mining",
                    assigned_system_id="sol",
                    status="harvesting",
                ),
            ),
            flight_log=("Command initialization verified at Sol Starport.",),
            streak=1,
            relics=(),
            mastery=PilotMastery(level=1, xp=0, next_level_xp=500, talent_points=0, specializations=()),
            active_contracts=initial_contracts,
            tactical_combo=0,
            near_miss_scanner_bonus=0.0,
            tutorial=generate_initial_tutorial(),
            story=generate_initial_story(),
            faction_standings={
                "sol_coalition": 0,
                "vanguard_syndicate": 0,
                "precursor_watch": 0,
                "nebula_collective": 0,
                "outlaw_corsairs": -15,
            },
            corp_standings={
                "hyperion_dynamics": 0,
                "astraea_pharma": 0,
                "omnicorp_mining": 0,
                "nexus_cybernetics": 0,
                "vortex_fuel": 0,
            },
        )

        economy = generate_initial_economy(systems, self.rng)
        return GameState(
            version=1,
            galaxy_seed=seed,
            ship=ship,
            systems=systems,
            visited_systems=("sol",),
            active_anomaly=None,
            active_combat=None,
            stats={
                "jumps": 0,
                "scans": 0,
                "trades": 0,
                "anomalies_resolved": 0,
                "combat_victories": 0,
                "credits_earned": 0,
                "contracts_completed": 0,
            },
            economy=economy,
            ai_captains=generate_ai_captains(systems, seed),
            depots=generate_depots(systems),
            messages=generate_welcome_messages(0),
        )

    @property
    def current_system(self) -> StarSystem:
        return self.state.systems[self.state.ship.current_system_id]

    @property
    def orbiting_body(self) -> CelestialBody | None:
        b_id = self.state.ship.orbiting_body_id
        if not b_id:
            return None
        for b in self.current_system.bodies:
            if b.id == b_id:
                return b
        return None

    def _process_drone_cycle(self, ship: ShipState) -> tuple[FleetDrone, ...]:
        """Advance autonomous drone harvest cycle across star systems."""
        updated_drones = []
        for d in ship.fleet_drones:
            assigned_system = self.state.systems.get(d.assigned_system_id)
            faction_id = get_faction_id_from_name(assigned_system.faction) if assigned_system else "sol_coalition"
            perks = get_faction_service_perks(faction_id, self.state.ship.faction_standings.get(faction_id, 0))
            yield_bonus = 1.0 + float(perks["drone_yield_bonus"])
            if d.drone_type == "mining":
                yield_amount = max(1, int(2 * d.efficiency * (0.5 + d.integrity / 200.0) * yield_bonus))
                updated_drones.append(
                    replace(
                        d,
                        status="harvesting",
                        cargo_accumulated=d.cargo_accumulated + yield_amount,
                        sorties=d.sorties + 1,
                        integrity=max(0, d.integrity - 1),
                        level=d.level + 1 if (d.sorties + 1) % 10 == 0 else d.level,
                    )
                )
            elif d.drone_type == "scout":
                yield_amount = max(10, int(75 * d.efficiency * (0.5 + d.integrity / 200.0) * yield_bonus))
                updated_drones.append(
                    replace(
                        d,
                        status="patrolling",
                        credits_accumulated=d.credits_accumulated + yield_amount,
                        sorties=d.sorties + 1,
                        integrity=max(0, d.integrity - 1),
                        level=d.level + 1 if (d.sorties + 1) % 10 == 0 else d.level,
                    )
                )
            else:
                updated_drones.append(d)
        return tuple(updated_drones)

    def jump(self, target_system_id: str) -> tuple[bool, str]:
        """Execute a hyperspace jump to an adjacent star system."""
        with self.lock:
            if self.state.active_combat is not None:
                return False, "Hyperspace drive locked by hostile enemy tractor field! Must resolve combat or flee."

            if self.state.active_anomaly is not None:
                return False, "Hyperspace drive locked: unresolved spatial anomaly in proximity!"

            cur_sys = self.current_system
            if target_system_id not in cur_sys.connections:
                return False, f"System '{target_system_id}' is not linked via hyperlane corridor."

            target_sys = self.state.systems.get(target_system_id)
            if not target_sys:
                return False, f"Unknown system target '{target_system_id}'."

            # Calculate fuel cost (with warp booster upgrade bonus, relics, and talents)
            passives = calculate_passive_multipliers(self.state.ship)
            equipment = calculate_equipment_bonuses(self.state.ship)
            eng_pwr = self.state.ship.power.engines
            base_fuel = 8
            if eng_pwr >= 40:
                fuel_cost = max(3, base_fuel - 3)
            elif eng_pwr < 20:
                fuel_cost = base_fuel + 4
            else:
                fuel_cost = base_fuel

            fuel_cost = max(1, int(fuel_cost * equipment["fuel_efficiency"] * passives["fuel_efficiency"]))

            if self.state.ship.fuel < fuel_cost:
                return False, f"Insufficient Quantum Fuel: {fuel_cost} units required, {self.state.ship.fuel} available."

            # Execute jump
            new_fuel = self.state.ship.fuel - fuel_cost
            visited = set(self.state.visited_systems)
            visited.add(target_system_id)

            # Update streak (rewarding safe transit under loss aversion mechanics)
            new_streak = min(10, self.state.ship.streak + 1) if self.state.ship.hull >= 75 else self.state.ship.streak
            streak_mult = 1.0 + min(1.5, (new_streak - 1) * 0.15)
            log_entry = f"Hyperspace jump completed to {target_sys.name} (fuel: {fuel_cost}). Streak: x{streak_mult:.2f} ({new_streak} jumps)."
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            # Process autonomous fleet drone cycle
            updated_drones = self._process_drone_cycle(self.state.ship)

            # Progress exploration contracts and award navigation pilot XP
            updated_contracts, contract_logs = self._progress_contracts("exploration", 1)
            new_log.extend(contract_logs)
            new_mastery, xp_logs = self._award_pilot_xp(35, self.state.ship.mastery)
            new_log.extend(xp_logs)

            # Encounter calculation
            anomaly = None
            combat = None

            # Check hostile faction interception or low security ambush
            has_escort = any(d.drone_type == "combat_escort" for d in self.state.ship.fleet_drones)
            sys_faction_id = get_faction_id_from_name(target_sys.faction)
            standing = self.state.ship.faction_standings.get(sys_faction_id, 0)
            is_hostile_territory = standing <= -50
            home_faction_id = get_faction_id_from_name(cur_sys.faction)
            home_standing = self.state.ship.faction_standings.get(home_faction_id, 0)
            escort_evasion = 0.25 if home_standing >= 70 else 0.0
            encounter_evasion = min(0.90, equipment["pirate_evasion"] + escort_evasion)

            if is_hostile_territory and self.rng.random() < 0.65 * (1.0 - encounter_evasion):
                combat = generate_system_enemy(
                    system_id=target_system_id,
                    security=target_sys.security,
                    faction=target_sys.faction,
                    seed=self.rng.randint(1000, 99999),
                )
                new_log.append(f"HOSTILE PATROL: Intercepted by {combat.enemy_name} due to hostile faction standing ({standing})!")
            elif target_sys.security < 0.35:
                if has_escort:
                    new_log.append("TACTICAL: Combat escort frigate dispersed hostile ambush.")
                elif self.rng.random() < 0.40 * (1.0 - encounter_evasion):
                    combat = generate_system_enemy(
                        system_id=target_system_id,
                        security=target_sys.security,
                        faction=target_sys.faction,
                        seed=self.rng.randint(1000, 99999),
                    )
                    new_log.append(f"ALERT: Intercepted by hostile {combat.enemy_name}! Weapons locked.")

            if not combat and self.rng.random() < 0.35:
                anomaly = GalaxyGenerator.get_random_anomaly(self.rng.randint(1, 99999))
                new_log.append(f"WARNING: Deep-space anomaly detected! [{anomaly.title}]")

            # Tutorial progression on hyperspace jump
            new_tut, tut_cr, tut_xp, tut_relics, tut_logs = self._progress_tutorial("jump")
            new_log.extend(tut_logs)
            if tut_xp > 0:
                new_mastery, xp_logs = self._award_pilot_xp(tut_xp, new_mastery)
                new_log.extend(xp_logs)

            # Story transmission alert if arrived in chapter target system
            story = self.state.ship.story
            new_story = story
            if not story.completed and story.current_chapter_index < len(story.chapters):
                cur_chap = story.chapters[story.current_chapter_index]
                if cur_chap.target_system_id == target_system_id and not cur_chap.completed:
                    new_log.append(f"📡 INCOMING SUBSPACE TRANSMISSION: [{cur_chap.transmission.speaker}] '{cur_chap.title}'")
                    existing_msgs = {t.message for t in story.transmission_log}
                    if cur_chap.transmission.message not in existing_msgs:
                        new_story = StoryState(
                            campaign_title=story.campaign_title,
                            current_chapter_index=story.current_chapter_index,
                            chapters=story.chapters,
                            transmission_log=tuple(list(story.transmission_log) + [cur_chap.transmission]),
                            reputation=story.reputation,
                            completed=story.completed,
                        )

            new_hull, new_max_hull, new_shield, new_max_shield = self._apply_relic_stat_bonuses(
                self.state.ship.hull,
                self.state.ship.max_hull,
                self.state.ship.shield,
                self.state.ship.max_shield,
                tut_relics,
            )

            new_ship = self._clone_ship(
                hull=new_hull,
                max_hull=new_max_hull,
                shield=new_shield,
                max_shield=new_max_shield,
                fuel=new_fuel,
                credits=self.state.ship.credits + tut_cr,
                current_system_id=target_system_id,
                orbiting_body_id=target_sys.bodies[0].id if target_sys.bodies else None,
                landed_body_id=None,
                travel=None,
                fleet_drones=updated_drones,
                flight_log=tuple(new_log[-20:]),
                streak=new_streak,
                mastery=new_mastery,
                relics=tuple(list(self.state.ship.relics) + tut_relics),
                active_contracts=updated_contracts,
                tactical_combo=0,
                tutorial=new_tut,
                story=new_story,
            )

            stats = dict(self.state.stats)
            stats["jumps"] += 1

            # Advance cosmic time by 2 ticks (12 hours transit) during interstellar hyperspace jump
            cur_time = self.state.time
            new_tick = cur_time.tick + 2
            new_days = cur_time.elapsed_days + 0.5
            new_stardate = 3042.0 + (new_days / 365.25)
            transit_time = TimeState(
                tick=new_tick,
                stardate=new_stardate,
                speed=cur_time.speed,
                is_paused=cur_time.is_paused,
                time_scale=cur_time.time_scale,
                elapsed_days=new_days,
            )

            # Advance planetary orbits across all systems by 2 transit ticks
            updated_systems = {}
            for sys_id, system in self.state.systems.items():
                updated_bodies = []
                for body in system.bodies:
                    d_angle = body.orbit_speed * 0.05 * 2
                    updated_bodies.append(
                        replace(body, current_angle=(body.current_angle + d_angle) % (2.0 * math.pi))
                    )
                updated_systems[sys_id] = StarSystem(
                    id=system.id,
                    name=system.name,
                    seed=system.seed,
                    x=system.x,
                    y=system.y,
                    spectral_type=system.spectral_type,
                    color=system.color,
                    security=system.security,
                    faction=system.faction,
                    bodies=tuple(updated_bodies),
                    connections=system.connections,
                    dominant_corp=system.dominant_corp,
                )

            # Advance global economy by 2 transit ticks
            new_econ, econ_logs = tick_global_economy(self.state.economy, 2, self.state.systems, self.rng)
            if econ_logs:
                new_flight_log = list(new_ship.flight_log) + econ_logs
                new_ship = self._clone_ship(
                    ship_class=new_ship.ship_class,
                    hull=new_ship.hull,
                    max_hull=new_ship.max_hull,
                    shield=new_ship.shield,
                    max_shield=new_ship.max_shield,
                    fuel=new_ship.fuel,
                    max_fuel=new_ship.max_fuel,
                    credits=new_ship.credits,
                    cargo=new_ship.cargo,
                    cargo_capacity=new_ship.cargo_capacity,
                    current_system_id=new_ship.current_system_id,
                    orbiting_body_id=new_ship.orbiting_body_id,
                    landed_body_id=None,
                    travel=None,
                    power=new_ship.power,
                    upgrades=new_ship.upgrades,
                    equipped_upgrades=new_ship.equipped_upgrades,
                    fleet_drones=new_ship.fleet_drones,
                    flight_log=tuple(new_flight_log[-20:]),
                    streak=new_ship.streak,
                    relics=new_ship.relics,
                    mastery=new_ship.mastery,
                    active_contracts=new_ship.active_contracts,
                    tactical_combo=new_ship.tactical_combo,
                    near_miss_scanner_bonus=new_ship.near_miss_scanner_bonus,
                    tutorial=new_ship.tutorial,
                    story=new_ship.story,
                    faction_standings=new_ship.faction_standings,
                    corp_standings=new_ship.corp_standings,
                )

            self.state = self._clone_state(
                ship=new_ship,
                systems=updated_systems,
                visited_systems=tuple(sorted(visited)),
                active_anomaly=anomaly,
                active_combat=combat,
                stats=stats,
                time=transit_time,
                economy=new_econ,
            )

            msg = f"Jump successful: arrived in {target_sys.name}."
            if combat:
                msg += f" WARNING: Intercepted by {combat.enemy_name}!"
            return True, msg

    def orbit(self, body_id: str) -> tuple[bool, str]:
        """Establish orbital trajectory around a celestial body in the current system."""
        with self.lock:
            cur_sys = self.current_system
            matched = None
            for b in cur_sys.bodies:
                if b.id == body_id:
                    matched = b
                    break

            if not matched:
                return False, f"Celestial body '{body_id}' not found in {cur_sys.name}."

            log_entry = f"Orbital capture achieved around {matched.name}."
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            new_tut, tut_cr, tut_xp, tut_relics, tut_logs = self._progress_tutorial("orbit")
            new_log.extend(tut_logs)
            new_mastery, xp_logs = self._award_pilot_xp(tut_xp, self.state.ship.mastery) if tut_xp > 0 else (self.state.ship.mastery, [])
            new_log.extend(xp_logs)

            new_ship = self._clone_ship(
                orbiting_body_id=body_id,
                landed_body_id=None,
                travel=None,
                credits=self.state.ship.credits + tut_cr,
                mastery=new_mastery,
                relics=tuple(list(self.state.ship.relics) + tut_relics),
                tutorial=new_tut,
                flight_log=tuple(new_log[-20:]),
            )

            self.state = self._clone_state(ship=new_ship)
            return True, f"Now in orbit around {matched.name}."

    def start_travel(self, body_id: str, mode: str = "sublight") -> tuple[bool, str]:
        """Initiate sublight or quantum in-system transit toward a celestial body."""
        with self.lock:
            norm_mode = str(mode).strip().lower()
            if norm_mode not in ("sublight", "quantum"):
                return False, f"Invalid transit mode '{mode}'. Choose 'sublight' or 'quantum'."

            cur_sys = self.current_system
            matched = None
            for b in cur_sys.bodies:
                if b.id == body_id:
                    matched = b
                    break

            if not matched:
                return False, f"Celestial body '{body_id}' not found in {cur_sys.name}."

            origin = self.orbiting_body
            origin_id = origin.id if origin else None
            origin_r = origin.orbit_radius if origin else 0.0
            distance_au = round(max(0.5, abs(matched.orbit_radius - origin_r)), 2)

            new_fuel = self.state.ship.fuel
            if norm_mode == "quantum":
                fuel_cost = max(2, int(math.ceil(distance_au * 0.8)))
                if self.state.ship.fuel < fuel_cost:
                    return False, f"Insufficient quantum fuel for micro-jump: need {fuel_cost}, have {self.state.ship.fuel}."
                new_fuel -= fuel_cost
                duration_ticks = 1
            else:
                engine_factor = max(0.5, self.state.ship.power.engines / 25.0)
                duration_ticks = max(1, min(8, int(math.ceil(distance_au / (1.2 * engine_factor)))))

            cur_tick = self.state.time.tick
            travel = TravelState(
                origin_body_id=origin_id,
                destination_body_id=matched.id,
                mode=norm_mode,
                started_tick=cur_tick,
                arrival_tick=cur_tick + duration_ticks,
                distance_au=distance_au,
                duration_ticks=duration_ticks,
            )

            log_entry = f"Engaged {norm_mode} drive toward {matched.name} ({distance_au:.1f} AU, ETA {duration_ticks} tick(s))."
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            new_ship = self._clone_ship(
                fuel=new_fuel,
                landed_body_id=None,
                travel=travel,
                flight_log=tuple(new_log[-20:]),
            )
            self.state = self._clone_state(ship=new_ship)
            return True, log_entry

    def scan(self) -> tuple[bool, str, dict[str, Any]]:
        """Perform sensor sweep of current body or local space."""
        with self.lock:
            body = self.orbiting_body
            if not body:
                return False, "Cannot scan: ship must establish orbit around a celestial body first.", {}

            if body.scan_completed:
                return False, f"{body.name} has already been surveyed; no further research bounty is available.", {}

            passives = calculate_passive_multipliers(self.state.ship)
            equipment = calculate_equipment_bonuses(self.state.ship)
            pwr = self.state.ship.power.sensors
            credit_bounty = int(100 * (pwr / 25.0))
            credit_bounty = int(credit_bounty * equipment["scan_mult"] * passives["scan_bounty"])

            # Mark scan completed on body
            updated_bodies = []
            for b in self.current_system.bodies:
                if b.id == body.id:
                    scanned = replace(b, scan_completed=True)
                    updated_bodies.append(scanned)
                else:
                    updated_bodies.append(b)

            cur_sys = self.current_system
            new_sys = StarSystem(
                id=cur_sys.id,
                name=cur_sys.name,
                seed=cur_sys.seed,
                x=cur_sys.x,
                y=cur_sys.y,
                spectral_type=cur_sys.spectral_type,
                color=cur_sys.color,
                security=cur_sys.security,
                faction=cur_sys.faction,
                bodies=tuple(updated_bodies),
                connections=cur_sys.connections,
                dominant_corp=cur_sys.dominant_corp,
            )

            systems = dict(self.state.systems)
            systems[cur_sys.id] = new_sys

            # Award credit bounty
            new_credits = self.state.ship.credits + credit_bounty

            # Variable Ratio relic drop and near-miss feedback
            relic_bonus = passives["relic_find"] + equipment["relic_find"] + self.state.ship.near_miss_scanner_bonus
            found_relic, is_near_miss = roll_relic_drop(self.rng, bonus_prob=relic_bonus, current_system=cur_sys.name)
            new_relics = list(self.state.ship.relics)
            new_near_miss = 0.0

            log_entry = f"Sensor scan completed for {body.name}: awarded {credit_bounty} cr scientific research bounty."
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            if found_relic:
                new_relics.append(found_relic)
                new_log.append(f"★ PRECURSOR ARTIFACT DISCOVERED: Salvaged {found_relic.rarity.upper()} relic [{found_relic.name}]! {found_relic.description}")
            elif is_near_miss:
                new_near_miss = 0.25
                new_log.append("RESONANCE NEAR-MISS: Faint Precursor harmonics slipped out of phase! Sensor array tuned (+25% discovery chance next scan).")

            # Progress exploration contracts and award survey pilot XP
            updated_contracts, contract_logs = self._progress_contracts("exploration", 1)
            new_log.extend(contract_logs)
            scan_faction_id = get_faction_id_from_name(cur_sys.faction)
            scan_perks = get_faction_service_perks(scan_faction_id, self.state.ship.faction_standings.get(scan_faction_id, 0))
            scan_xp = int(50 * (1.0 + float(scan_perks["scan_xp_bonus"])))
            new_mastery, xp_logs = self._award_pilot_xp(scan_xp, self.state.ship.mastery)
            new_log.extend(xp_logs)

            new_tut, tut_cr, tut_xp, tut_relics, tut_logs = self._progress_tutorial("scan")
            new_log.extend(tut_logs)
            if tut_xp > 0:
                new_mastery, tut_xp_logs = self._award_pilot_xp(tut_xp, new_mastery)
                new_log.extend(tut_xp_logs)

            added_relics = ([found_relic] if found_relic else []) + list(tut_relics)
            new_hull, new_max_hull, new_shield, new_max_shield = self._apply_relic_stat_bonuses(
                self.state.ship.hull,
                self.state.ship.max_hull,
                self.state.ship.shield,
                self.state.ship.max_shield,
                added_relics,
            )

            new_ship = self._clone_ship(
                hull=new_hull,
                max_hull=new_max_hull,
                shield=new_shield,
                max_shield=new_max_shield,
                credits=new_credits + tut_cr,
                relics=tuple(new_relics + tut_relics),
                near_miss_scanner_bonus=new_near_miss,
                mastery=new_mastery,
                active_contracts=updated_contracts,
                tutorial=new_tut,
                flight_log=tuple(new_log[-20:]),
            )

            stats = dict(self.state.stats)
            stats["scans"] += 1
            stats["credits_earned"] += credit_bounty

            self.state = self._clone_state(ship=new_ship, systems=systems, stats=stats)

            discovery_info = {
                "body_name": body.name,
                "body_type": body.body_type,
                "discovery": body.scan_discovery,
                "bounty": credit_bounty,
                "market_archetype": body.market_archetype,
                "hazards": list(body.hazards),
                "relic": found_relic.to_dict() if found_relic else None,
                "near_miss": is_near_miss,
            }

            return True, f"Scan analysis complete: {body.scan_discovery}", discovery_info

    def route_power(self, engines: int, shields: int, sensors: int, weapons: int) -> tuple[bool, str]:
        """Adjust reactor power distribution across ship subsystems."""
        with self.lock:
            try:
                new_power = ShipPower(engines=engines, shields=shields, sensors=sensors, weapons=weapons)
            except ValueError as e:
                return False, f"Power routing rejected: {str(e)}"

            log_entry = f"Reactor power redistributed: ENG {engines}%, SHD {shields}%, SEN {sensors}%, WEP {weapons}%."
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            new_tut, tut_cr, tut_xp, tut_relics, tut_logs = self._progress_tutorial("power")
            new_log.extend(tut_logs)
            new_mastery, xp_logs = self._award_pilot_xp(tut_xp, self.state.ship.mastery) if tut_xp > 0 else (self.state.ship.mastery, [])
            new_log.extend(xp_logs)

            new_ship = self._clone_ship(
                power=new_power,
                credits=self.state.ship.credits + tut_cr,
                mastery=new_mastery,
                relics=tuple(list(self.state.ship.relics) + tut_relics),
                tutorial=new_tut,
                flight_log=tuple(new_log[-20:]),
            )

            self.state = self._clone_state(ship=new_ship)

            return True, "Reactor power routed successfully."

    def trade(self, commodity_id: str, quantity: int, is_buy: bool) -> tuple[bool, str]:
        """Execute buy or sell commodity order at orbiting market."""
        with self.lock:
            body = self.orbiting_body
            if not body or not body.station_dockable:
                return False, "Docking authorization required: ship must orbit a station or habitable colony to trade."

            if quantity <= 0:
                return False, "Quantity must be greater than zero."

            comm = COMMODITY_MAP.get(commodity_id)
            if not comm:
                return False, f"Commodity '{commodity_id}' not traded here."

            quote = calculate_dynamic_market_quote(self.current_system, body, comm, self.state.economy)
            vol_per_unit = comm.volume

            cargo = dict(self.state.ship.cargo)
            stats = dict(self.state.stats)

            passives = calculate_passive_multipliers(self.state.ship)
            equipment = calculate_equipment_bonuses(self.state.ship)

            # Geopolitical faction & corporate commercial mechanics
            sys_faction_id = get_faction_id_from_name(self.current_system.faction)
            standing = self.state.ship.faction_standings.get(sys_faction_id, 0)
            faction_mod = calculate_faction_market_modifier(sys_faction_id, standing)
            faction_perks = get_faction_service_perks(sys_faction_id, standing)
            new_faction_standings = dict(self.state.ship.faction_standings)
            new_corp_standings = dict(self.state.ship.corp_standings)

            if is_buy:
                unit_price = int(quote.buy_price * faction_mod)
                total_cost = unit_price * quantity
                if self.state.ship.credits < total_cost:
                    return False, f"Insufficient credits: {total_cost} cr required, {self.state.ship.credits} cr available."

                current_cargo_volume = calculate_cargo_volume(cargo)
                needed_space = quantity * vol_per_unit
                if current_cargo_volume + needed_space > self.state.ship.cargo_capacity:
                    return False, f"Cargo hold capacity exceeded: cannot load {needed_space} units."

                new_credits = self.state.ship.credits - total_cost
                cargo[commodity_id] = cargo.get(commodity_id, 0) + quantity
                tariff_note = ""
                if faction_mod > 1.0:
                    tariff_note = f" (+{int((faction_mod - 1.0)*100)}% {self.current_system.faction} tariff)"
                elif faction_mod < 1.0:
                    tariff_note = f" (-{int((1.0 - faction_mod)*100)}% {self.current_system.faction} discount)"
                msg = f"Purchased {quantity}x {quote.name} for {total_cost} cr{tariff_note}."
            else:
                owned = cargo.get(commodity_id, 0)
                if owned < quantity:
                    return False, f"Insufficient inventory: you have {owned} units, tried to sell {quantity}."

                margin_mult = passives.get("trade_margin", 1.0) * (1.0 + equipment["trade_margin"] + len(self.state.ship.allies) * 0.05 + float(faction_perks["trade_margin"]))
                corp_mult = 1.0
                corp_note = ""
                dom_corp_id = self.current_system.dominant_corp
                if dom_corp_id:
                    corp = get_corporation(dom_corp_id)
                    if corp and corp.specialty_commodity == commodity_id:
                        corp_mult = 1.0 + corp.bonus_trade_margin
                        corp_note = f" [{corp.name} specialty: +{int(corp.bonus_trade_margin*100)}%]"
                        new_corp_standings[dom_corp_id] = min(100, new_corp_standings.get(dom_corp_id, 0) + 2)

                # Lawful commerce slightly boosts local faction relations
                new_faction_standings[sys_faction_id] = min(100, new_faction_standings.get(sys_faction_id, 0) + 1)

                revenue = int(quote.sell_price * quantity * margin_mult * corp_mult)
                new_credits = self.state.ship.credits + revenue
                cargo[commodity_id] = owned - quantity
                if cargo[commodity_id] == 0:
                    del cargo[commodity_id]
                stats["credits_earned"] += revenue
                msg = f"Sold {quantity}x {quote.name} for {revenue} cr (trade margin: x{margin_mult:.2f}){corp_note}."

            stats["trades"] += 1
            log_entry = f"Market transaction: {msg}"
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            # Progress trade contracts and award merchant pilot XP
            updated_contracts, contract_logs = self._progress_contracts("trade", 1)
            new_log.extend(contract_logs)
            new_mastery, xp_logs = self._award_pilot_xp(25, self.state.ship.mastery)
            new_log.extend(xp_logs)

            new_tut, tut_cr, tut_xp, tut_relics, tut_logs = self._progress_tutorial("trade")
            new_log.extend(tut_logs)
            if tut_xp > 0:
                new_mastery, tut_xp_logs = self._award_pilot_xp(tut_xp, new_mastery)
                new_log.extend(tut_xp_logs)

            new_ship = self._clone_ship(
                credits=new_credits + tut_cr,
                cargo=cargo,
                mastery=new_mastery,
                relics=tuple(list(self.state.ship.relics) + tut_relics),
                active_contracts=updated_contracts,
                tutorial=new_tut,
                faction_standings=new_faction_standings,
                corp_standings=new_corp_standings,
                flight_log=tuple(new_log[-20:]),
            )

            # Update local system stockpile in economy
            econ_markets = dict(self.state.economy.markets)
            sys_id = self.current_system.id
            if sys_id in econ_markets:
                sm = econ_markets[sys_id]
                new_stocks = dict(sm.stockpiles)
                if is_buy:
                    new_stocks[commodity_id] = max(MIN_STOCK, new_stocks.get(commodity_id, 50) - quantity)
                else:
                    new_stocks[commodity_id] = min(MAX_STOCK, new_stocks.get(commodity_id, 50) + quantity)
                econ_markets[sys_id] = SystemMarketState(
                    system_id=sys_id,
                    stockpiles=new_stocks,
                    production_rates=sm.production_rates,
                    consumption_rates=sm.consumption_rates,
                )
            new_economy = GlobalEconomyState(
                markets=econ_markets,
                active_events=self.state.economy.active_events,
                last_updated_tick=self.state.economy.last_updated_tick,
            )

            self.state = self._clone_state(ship=new_ship, stats=stats, economy=new_economy)

            return True, msg

    def buy_upgrade(self, upgrade_id: str) -> tuple[bool, str]:
        """Purchase and install a hardware upgrade module at an orbital station."""
        with self.lock:
            body = self.orbiting_body
            if not body or not body.station_dockable:
                return False, "Upgrade bay drydock requires docking at a station or colony."

            upgrade = get_upgrade(upgrade_id)
            if not upgrade:
                return False, f"Unknown hardware upgrade '{upgrade_id}'."

            if upgrade.slot in self.state.ship.equipped_upgrades:
                existing_id = self.state.ship.equipped_upgrades[upgrade.slot]
                if existing_id == upgrade_id:
                    return False, f"Module '{upgrade.name}' is already installed."
                existing = get_upgrade(existing_id)
                existing_name = existing.name if existing else existing_id
                return False, (
                    f"Slot '{upgrade.slot}' already houses {existing_name}. "
                    f"Sell the installed module before installing {upgrade.name}."
                )

            if self.state.ship.credits < upgrade.cost:
                return False, f"Insufficient credits: costs {upgrade.cost} cr, you have {self.state.ship.credits} cr."

            new_credits = self.state.ship.credits - upgrade.cost
            equipped = dict(self.state.ship.equipped_upgrades)
            equipped[upgrade.slot] = upgrade_id

            upg_list = list(self.state.ship.upgrades)
            if upgrade.name not in upg_list:
                upg_list.append(upgrade.name)

            # Determine base ship stats
            base_hull = 100
            base_shield = 100
            base_capacity = 40
            for c in CATALOG_CHASSIS:
                if c.ship_class == self.state.ship.ship_class:
                    base_hull = c.max_hull
                    base_shield = c.max_shield
                    base_capacity = c.cargo_capacity
                    break

            # Recompute stats based on chassis, equipped modules, and permanent relic/talent passives.
            passives = calculate_passive_multipliers(self.state.ship)
            total_hull = base_hull + int(passives["max_hull"])
            total_shield = base_shield + int(passives["shield_cap"])
            total_capacity = base_capacity
            for u_id in equipped.values():
                u = get_upgrade(u_id)
                if u:
                    if "max_hull" in u.stat_bonus:
                        total_hull += int(u.stat_bonus["max_hull"])
                    if "max_shield" in u.stat_bonus:
                        total_shield += int(u.stat_bonus["max_shield"])
                    if "cargo_capacity" in u.stat_bonus:
                        total_capacity += int(u.stat_bonus["cargo_capacity"])

            cur_hull = min(self.state.ship.hull, total_hull)
            if "max_hull" in upgrade.stat_bonus:
                cur_hull = total_hull
            cur_shield = min(self.state.ship.shield, total_shield)
            if "max_shield" in upgrade.stat_bonus:
                cur_shield = total_shield

            log_entry = f"Arsenal upgrade: Installed {upgrade.name} ({upgrade.slot.upper()}) for {upgrade.cost} cr."
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            new_ship = self._clone_ship(
                hull=cur_hull,
                max_hull=total_hull,
                shield=cur_shield,
                max_shield=total_shield,
                credits=new_credits,
                cargo_capacity=total_capacity,
                upgrades=tuple(upg_list),
                equipped_upgrades=equipped,
                flight_log=tuple(new_log),
            )

            self.state = self._clone_state(ship=new_ship)
            return True, f"Successfully installed {upgrade.name} in {upgrade.slot} slot."

    def sell_upgrade(self, slot: str) -> tuple[bool, str]:
        """Uninstall and sell an equipped hardware module back to shipyard for credits."""
        with self.lock:
            body = self.orbiting_body
            if not body or not body.station_dockable:
                return False, "Shipyard drydock authorization required: dock at a station or colony to uninstall modules."

            equipped = dict(self.state.ship.equipped_upgrades)
            if slot not in equipped:
                return False, f"No hardware module installed in {slot} slot."

            upg_id = equipped[slot]
            upg = get_upgrade(upg_id)
            trade_in_value = get_sell_value(upg_id)

            del equipped[slot]
            new_credits = self.state.ship.credits + trade_in_value

            # Determine base ship stats
            base_hull = 100
            base_shield = 100
            base_capacity = 40
            for c in CATALOG_CHASSIS:
                if c.ship_class == self.state.ship.ship_class:
                    base_hull = c.max_hull
                    base_shield = c.max_shield
                    base_capacity = c.cargo_capacity
                    break

            passives = calculate_passive_multipliers(self.state.ship)
            total_hull = base_hull + int(passives["max_hull"])
            total_shield = base_shield + int(passives["shield_cap"])
            total_capacity = base_capacity
            for u_id in equipped.values():
                u = get_upgrade(u_id)
                if u:
                    if "max_hull" in u.stat_bonus:
                        total_hull += int(u.stat_bonus["max_hull"])
                    if "max_shield" in u.stat_bonus:
                        total_shield += int(u.stat_bonus["max_shield"])
                    if "cargo_capacity" in u.stat_bonus:
                        total_capacity += int(u.stat_bonus["cargo_capacity"])

            cur_hull = min(self.state.ship.hull, total_hull)
            cur_shield = min(self.state.ship.shield, total_shield)

            upg_name = upg.name if upg else upg_id
            remaining_upgrades = tuple(n for n in self.state.ship.upgrades if n != upg_name)
            msg = f"Uninstalled {upg_name} from {slot} slot for {trade_in_value} cr trade-in value."
            new_log = list(self.state.ship.flight_log[-19:]) + [msg]

            new_ship = self._clone_ship(
                hull=cur_hull,
                max_hull=total_hull,
                shield=cur_shield,
                max_shield=total_shield,
                credits=new_credits,
                cargo_capacity=total_capacity,
                upgrades=remaining_upgrades,
                equipped_upgrades=equipped,
                flight_log=tuple(new_log),
            )
            self.state = self._clone_state(ship=new_ship)
            return True, msg

    def buy_ship_chassis(self, chassis_id: str) -> tuple[bool, str]:
        """Purchase and commission a new spacecraft hull chassis at an orbital shipyard."""
        with self.lock:
            body = self.orbiting_body
            if not body or not body.station_dockable:
                return False, "Shipyard drydock authorization required: dock at a station or colony to commission a new chassis."

            chassis = get_chassis(chassis_id)
            if not chassis:
                return False, f"Unknown ship chassis '{chassis_id}'."

            if chassis.cost <= 0:
                return False, f"'{chassis.name}' is the standard-issue starter hull and is not sold at shipyards."

            if chassis.ship_class == self.state.ship.ship_class:
                return False, f"Ship is already commissioned as a {chassis.name}."

            if self.state.ship.credits < chassis.cost:
                return False, f"Insufficient credits: {chassis.name} costs {chassis.cost} cr, you have {self.state.ship.credits} cr."

            new_credits = self.state.ship.credits - chassis.cost

            # Calculate stats with equipped upgrades
            bonus_capacity = 0
            bonus_shield = 0
            bonus_hull = 0
            for u_id in self.state.ship.equipped_upgrades.values():
                u = get_upgrade(u_id)
                if u:
                    if "cargo_capacity" in u.stat_bonus:
                        bonus_capacity += int(u.stat_bonus["cargo_capacity"])
                    if "max_shield" in u.stat_bonus:
                        bonus_shield += int(u.stat_bonus["max_shield"])
                    if "max_hull" in u.stat_bonus:
                        bonus_hull += int(u.stat_bonus["max_hull"])

            passives = calculate_passive_multipliers(self.state.ship)
            total_max_hull = chassis.max_hull + bonus_hull + int(passives["max_hull"])
            total_max_shield = chassis.max_shield + bonus_shield + int(passives["shield_cap"])
            total_cargo_capacity = chassis.cargo_capacity + bonus_capacity

            msg = f"Commissioned {chassis.name} ({chassis.ship_class}) at shipyard for {chassis.cost} cr! Perk: {chassis.specialty_perk}"
            new_log = list(self.state.ship.flight_log[-19:]) + [msg]

            new_ship = self._clone_ship(
                ship_class=chassis.ship_class,
                hull=total_max_hull,
                max_hull=total_max_hull,
                shield=total_max_shield,
                max_shield=total_max_shield,
                fuel=chassis.max_fuel,
                max_fuel=chassis.max_fuel,
                cargo_capacity=total_cargo_capacity,
                credits=new_credits,
                flight_log=tuple(new_log),
            )
            self.state = self._clone_state(ship=new_ship)
            return True, msg

    def use_item(self, item_id: str) -> tuple[bool, str]:
        """Consume a usable item from cargo (nanite repair paste, shield battery, fuel canister, decoy)."""
        with self.lock:
            cargo = dict(self.state.ship.cargo)
            if cargo.get(item_id, 0) <= 0:
                return False, f"Item '{item_id}' not found in cargo hold."

            item_info = get_item_info(item_id)
            if not item_info.is_usable:
                return False, f"'{item_info.name}' is a trade commodity and cannot be consumed directly."

            ship = self.state.ship
            new_hull = ship.hull
            new_shield = ship.shield
            new_fuel = ship.fuel
            combat = self.state.active_combat
            msg = ""

            if item_info.effect_type == "repair_hull":
                if ship.hull >= ship.max_hull:
                    return False, "Hull is already at maximum structural integrity."
                new_hull = min(ship.max_hull, ship.hull + item_info.effect_amount)
                msg = f"Applied {item_info.name}: restored +{new_hull - ship.hull} Hull integrity ({new_hull}/{ship.max_hull})."
            elif item_info.effect_type == "recharge_shield":
                if ship.shield >= ship.max_shield:
                    return False, "Deflector shields are already at maximum capacitance."
                new_shield = min(ship.max_shield, ship.shield + item_info.effect_amount)
                msg = f"Discharged {item_info.name}: boosted Deflector Shields by +{new_shield - ship.shield} MW ({new_shield}/{ship.max_shield})."
            elif item_info.effect_type == "refuel":
                if ship.fuel >= ship.max_fuel:
                    return False, "Hyperdrive fuel tanks are already completely full."
                new_fuel = min(ship.max_fuel, ship.fuel + item_info.effect_amount)
                msg = f"Injected {item_info.name}: loaded +{new_fuel - ship.fuel} Quantum Fuel units ({new_fuel}/{ship.max_fuel})."
            elif item_info.effect_type == "evade_combat":
                if not combat:
                    return False, "Decoy flare is only usable during active hostile combat engagements."
                combat = None
                msg = f"Deployed {item_info.name}! Scrambled hostile sensor lock and escaped combat encounter."
            else:
                return False, f"Unknown item effect '{item_info.effect_type}'."

            cargo[item_id] -= 1
            if cargo[item_id] <= 0:
                del cargo[item_id]

            new_log = list(ship.flight_log[-19:]) + [f"Item used: {msg}"]
            new_ship = self._clone_ship(
                hull=new_hull,
                shield=new_shield,
                fuel=new_fuel,
                cargo=cargo,
                flight_log=tuple(new_log),
            )
            self.state = self._clone_state(ship=new_ship, active_combat=combat)
            return True, msg

    def buy_item(self, item_id: str, quantity: int = 1) -> tuple[bool, str]:
        """Purchase consumable items from an orbital station terminal."""
        with self.lock:
            if quantity <= 0:
                return False, "Quantity must be greater than zero."

            body = self.orbiting_body
            if not body or not body.station_dockable:
                return False, "Station terminal requires docking at a station or colony."

            info = get_item_info(item_id)
            if info.category != "consumable" or not info.is_usable:
                return False, f"'{info.name}' is not sold at station terminals. Trade commodities via the local exchange instead."

            total_cost = info.base_price * quantity
            if self.state.ship.credits < total_cost:
                return False, f"Insufficient credits: {total_cost} cr required, {self.state.ship.credits} cr available."

            cargo = dict(self.state.ship.cargo)
            needed_volume = info.volume * quantity
            if calculate_cargo_volume(cargo) + needed_volume > self.state.ship.cargo_capacity:
                return False, f"Cargo hold capacity exceeded: cannot load {needed_volume} units."

            cargo[item_id] = cargo.get(item_id, 0) + quantity
            new_credits = self.state.ship.credits - total_cost
            msg = f"Purchased {quantity}x {info.name} for {total_cost} cr."
            new_log = list(self.state.ship.flight_log[-19:]) + [f"Station terminal: {msg}"]
            new_ship = self._clone_ship(credits=new_credits, cargo=cargo, flight_log=tuple(new_log))
            self.state = self._clone_state(ship=new_ship)
            return True, msg

    def jettison_cargo(self, item_id: str, quantity: int) -> tuple[bool, str]:
        """Jettison cargo into the cosmic vacuum to free hold space."""
        with self.lock:
            if quantity <= 0:
                return False, "Quantity must be greater than zero."
            cargo = dict(self.state.ship.cargo)
            owned = cargo.get(item_id, 0)
            if owned < quantity:
                return False, f"Cannot jettison {quantity} units: you only have {owned} in hold."

            cargo[item_id] = owned - quantity
            if cargo[item_id] <= 0:
                del cargo[item_id]

            item_info = get_item_info(item_id)
            freed_space = quantity * item_info.volume
            msg = f"Jettisoned {quantity}x {item_info.name} into space, freeing {freed_space} cargo hold units."
            new_log = list(self.state.ship.flight_log[-19:]) + [msg]
            new_ship = self._clone_ship(cargo=cargo, flight_log=tuple(new_log))
            self.state = self._clone_state(ship=new_ship)
            return True, msg

    def buy_drone(self, drone_type: str, assigned_system_id: str | None = None) -> tuple[bool, str]:
        """Purchase and commission an autonomous fleet drone."""
        with self.lock:
            body = self.orbiting_body
            if not body or not body.station_dockable:
                return False, "Drone commissioning hangar requires docking at a station or colony."

            template = CATALOG_DRONE_TEMPLATES.get(drone_type)
            if not template:
                return False, f"Unknown drone model '{drone_type}'. Choices: mining, scout, combat_escort."

            cost = template["cost"]
            if self.state.ship.credits < cost:
                return False, f"Insufficient credits: {template['name']} costs {cost} cr."

            target_sys = assigned_system_id or self.state.ship.current_system_id
            if target_sys not in self.state.systems:
                return False, f"Unknown star system '{target_sys}' for drone deployment."
            drone_id = f"drone_{drone_type}_{len(self.state.ship.fleet_drones) + 1}"
            new_drone = FleetDrone(
                id=drone_id,
                name=f"{template['name']} #{len(self.state.ship.fleet_drones) + 1}",
                drone_type=drone_type,
                assigned_system_id=target_sys,
                status="harvesting" if drone_type == "mining" else "patrolling",
            )

            new_credits = self.state.ship.credits - cost
            drones = list(self.state.ship.fleet_drones) + [new_drone]

            log_entry = f"Fleet expansion: Commissioned {new_drone.name} deployed to {target_sys}."
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            new_tut, tut_cr, tut_xp, tut_relics, tut_logs = self._progress_tutorial("drone")
            new_log.extend(tut_logs)
            new_mastery, xp_logs = self._award_pilot_xp(tut_xp, self.state.ship.mastery) if tut_xp > 0 else (self.state.ship.mastery, [])
            new_log.extend(xp_logs)

            new_ship = self._clone_ship(
                credits=new_credits + tut_cr,
                fleet_drones=tuple(drones),
                mastery=new_mastery,
                relics=tuple(list(self.state.ship.relics) + tut_relics),
                tutorial=new_tut,
                flight_log=tuple(new_log[-20:]),
            )

            self.state = self._clone_state(ship=new_ship)
            return True, f"Commissioned {new_drone.name} stationed in {target_sys}."

    def deploy_drone(self, drone_id: str, target_system_id: str) -> tuple[bool, str]:
        """Redeploy an autonomous fleet asset to a different star system."""
        with self.lock:
            if target_system_id not in self.state.systems:
                return False, f"Target star system '{target_system_id}' does not exist."

            found = False
            updated_drones = []
            for d in self.state.ship.fleet_drones:
                if d.id == drone_id:
                    found = True
                    updated_drones.append(
                        replace(
                            d,
                            assigned_system_id=target_system_id,
                            status="harvesting" if d.drone_type == "mining" else "patrolling",
                        )
                    )
                else:
                    updated_drones.append(d)

            if not found:
                return False, f"Drone with ID '{drone_id}' not found in fleet."

            new_ship = self._clone_ship(
                fleet_drones=tuple(updated_drones),
                flight_log=tuple(list(self.state.ship.flight_log[-19:]) + [f"Drone {drone_id} redeployed to {target_system_id}."]),
            )

            self.state = self._clone_state(ship=new_ship)

            return True, f"Drone '{drone_id}' redeployed to {target_system_id}."

    def collect_drone_yield(self, drone_id: str | None = None) -> tuple[bool, str, dict[str, Any]]:
        """Collect accumulated cargo and research credits from fleet drones."""
        with self.lock:
            total_cargo = 0
            total_credits = 0
            updated_drones = []

            for d in self.state.ship.fleet_drones:
                if drone_id is None or d.id == drone_id:
                    total_cargo += d.cargo_accumulated
                    total_credits += d.credits_accumulated
                    updated_drones.append(
                        replace(d, cargo_accumulated=0, credits_accumulated=0)
                    )
                else:
                    updated_drones.append(d)

            if total_cargo == 0 and total_credits == 0:
                return False, "No yield accumulated by fleet drones yet.", {"credits": 0, "cargo": 0}

            passives = calculate_passive_multipliers(self.state.ship)
            total_cargo = int(total_cargo * passives.get("drone_yield", 1.0))
            total_credits = int(total_credits * passives.get("drone_yield", 1.0))

            cargo = dict(self.state.ship.cargo)
            incoming_volume = calculate_cargo_volume({"titanium": total_cargo})
            free_volume = self.state.ship.cargo_capacity - calculate_cargo_volume(cargo)
            if incoming_volume > free_volume:
                return False, (
                    f"Cargo hold has {max(0, free_volume)} volume free but the harvest needs "
                    f"{incoming_volume}. Jettison cargo or expand the hold first."
                ), {"credits": 0, "cargo": 0}
            cargo["titanium"] = cargo.get("titanium", 0) + total_cargo
            new_credits = self.state.ship.credits + total_credits

            stats = dict(self.state.stats)
            stats["credits_earned"] += total_credits

            log_entry = f"Fleet harvest collected: +{total_credits} cr and +{total_cargo} titanium units (yield multiplier x{passives.get('drone_yield', 1.0):.2f})."
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            # Progress mining contracts and award fleet commander pilot XP
            updated_contracts, contract_logs = self._progress_contracts("mining", total_cargo)
            new_log.extend(contract_logs)
            new_mastery, xp_logs = self._award_pilot_xp(40, self.state.ship.mastery)
            new_log.extend(xp_logs)

            new_ship = self._clone_ship(
                credits=new_credits,
                cargo=cargo,
                fleet_drones=tuple(updated_drones),
                mastery=new_mastery,
                active_contracts=updated_contracts,
                flight_log=tuple(new_log[-20:]),
            )

            self.state = self._clone_state(
                ship=new_ship,
                stats=stats,
            )

            return True, f"Transferred {total_credits} cr and {total_cargo} units from fleet.", {
                "credits": total_credits,
                "cargo": total_cargo,
            }

    def combat_action(self, action: str) -> tuple[bool, str]:
        """Execute a tactical combat maneuver against an active hostile intercept."""
        with self.lock:
            combat = self.state.active_combat
            if not combat:
                return False, "No hostile ship in combat proximity."

            new_hull = self.state.ship.hull
            new_shield = self.state.ship.shield
            new_credits = self.state.ship.credits
            cargo = dict(self.state.ship.cargo)
            stats = dict(self.state.stats)
            passives = calculate_passive_multipliers(self.state.ship)
            equipment = calculate_equipment_bonuses(self.state.ship)
            mercenary_damage = sum(
                14 if d.specialty == "assault" else 8 if d.specialty == "evasion" else 4
                for d in self.state.ship.fleet_drones
                if d.drone_type == "mercenary"
            )
            mercenary_evasion = 0.10 if any(
                d.drone_type == "mercenary" and d.specialty == "evasion"
                for d in self.state.ship.fleet_drones
            ) else 0.0
            ally_damage = len(self.state.ship.allies) * 3

            new_combo = self.state.ship.tactical_combo
            new_streak = self.state.ship.streak
            enemy_rem_shield = combat.enemy_shield
            enemy_rem_hull = combat.enemy_hull
            enemy_rem_damage = combat.enemy_damage
            ability_cd = max(0, combat.ability_cooldown - 1)
            intent = combat.enemy_intent if combat.enemy_intent in {"fire", "brace", "evade", "execute", "ability"} else "fire"
            enemy_guard = 0.55 if intent == "brace" else 1.0
            damaging_actions = {"fire_lasers", "drone_strike", "target_subsystem", "target_weapons", "target_shields"}
            enemy_miss = action in damaging_actions and intent == "evade" and self.rng.random() < 0.35
            enemy_hull_before = enemy_rem_hull
            enemy_shield_before = enemy_rem_shield

            if action == "fire_lasers":
                wep_power = self.state.ship.power.weapons
                bonus_wep = int(equipment["combat_damage"])
                base_dmg = int((20 + int(wep_power * 0.75) + bonus_wep + mercenary_damage + ally_damage) * passives.get("laser_dmg", 1.0) * enemy_guard)

                new_combo += 1
                crit_text = ""
                if new_combo >= 3:
                    base_dmg = int(base_dmg * 1.5)
                    crit_text = f" (TACTICAL OVERCHARGE x{new_combo}: +50% CRIT DAMAGE!)"

                if enemy_rem_shield > 0:
                    if base_dmg <= enemy_rem_shield:
                        enemy_rem_shield -= base_dmg
                        strike_desc = f"Laser strike absorbed by enemy deflector shields ({base_dmg} MW damage dealt, Shield: {enemy_rem_shield}/{combat.enemy_max_shield}){crit_text}."
                    else:
                        overflow = base_dmg - enemy_rem_shield
                        enemy_rem_shield = 0
                        enemy_rem_hull -= overflow
                        strike_desc = f"Laser strike shattered enemy deflector shields! {overflow} overflow damage struck hull{crit_text}."
                else:
                    enemy_rem_hull -= base_dmg
                    strike_desc = f"Laser strike struck enemy hull directly for {base_dmg} damage{crit_text}."

            elif action == "drone_strike":
                has_escort = any(d.drone_type == "combat_escort" for d in self.state.ship.fleet_drones)
                has_scout = any(d.drone_type == "scout" for d in self.state.ship.fleet_drones)
                if not has_escort and not has_scout:
                    return False, "No tactical drones deployed. Deploy a Combat Escort or Scout drone first."

                new_combo += 1
                if has_escort:
                    torpedo_dmg = max(1, int(45 * enemy_guard))
                    enemy_rem_hull -= torpedo_dmg
                    strike_desc = f"Combat Escort Frigate launched armor-piercing kinetic torpedo! Inflicted {torpedo_dmg} damage directly to hull (bypassing shields)!"
                else:
                    sensor_burn = max(1, int(35 * enemy_guard))
                    enemy_rem_shield = max(0, enemy_rem_shield - sensor_burn)
                    strike_desc = f"Scout Drone focused beam telemetry! Collapsed {sensor_burn} MW of enemy deflector shields!"

            elif action in ("target_subsystem", "target_weapons", "target_shields"):
                subsystem = "shields" if action == "target_shields" else "weapons"
                new_combo += 1
                if subsystem == "weapons":
                    enemy_rem_damage = max(6, int(combat.enemy_damage * 0.60))
                    strike_dmg = max(1, int(15 * enemy_guard))
                    if enemy_rem_shield > 0:
                        enemy_rem_shield = max(0, enemy_rem_shield - strike_dmg)
                    else:
                        enemy_rem_hull -= strike_dmg
                    strike_desc = f"Targeted strike hit enemy weapon arrays! Disabled fire-control (-40% enemy firepower) and dealt {strike_dmg} damage!"
                else:
                    shield_ion = max(1, int(40 * enemy_guard))
                    enemy_rem_shield = max(0, enemy_rem_shield - shield_ion)
                    strike_desc = f"Ion pulse targeted enemy shield generators! EMP cascade drained {shield_ion} MW shields!"

            elif action == "shield_absorb":
                boost = 30 + (25 if "dreadnought_tactics" in self.state.ship.mastery.specializations else 0)
                new_shield = min(self.state.ship.max_shield, new_shield + boost)
                mitigated = max(1, int(combat.enemy_damage * 0.35 * (1.5 if intent == "execute" else 1.0)))
                if new_shield >= mitigated:
                    new_shield -= mitigated
                else:
                    new_hull = max(0, new_hull - (mitigated - new_shield))
                    new_shield = 0
                msg = f"Shield capacitors overcharged (+{boost} MW). Enemy barrage deflected, taking only {mitigated} damage."
                next_intent, next_telegraph = choose_enemy_intent(
                    profile=combat.ai_profile,
                    special_ability=combat.special_ability,
                    ability_ready=max(0, combat.ability_cooldown - 1) == 0,
                    enemy_hull=combat.enemy_hull,
                    enemy_max_hull=combat.enemy_max_hull,
                    enemy_shield=combat.enemy_shield,
                    enemy_max_shield=combat.enemy_max_shield,
                    player_hull=new_hull,
                    player_max_hull=self.state.ship.max_hull,
                    player_shield=new_shield,
                    player_max_shield=self.state.ship.max_shield,
                    player_combo=new_combo,
                )
                new_combat = CombatEncounter(
                    id=combat.id,
                    enemy_name=combat.enemy_name,
                    enemy_class=combat.enemy_class,
                    enemy_hull=combat.enemy_hull,
                    enemy_max_hull=combat.enemy_max_hull,
                    enemy_damage=combat.enemy_damage,
                    bounty_credits=combat.bounty_credits,
                    salvage_commodity=combat.salvage_commodity,
                    enemy_shield=combat.enemy_shield,
                    enemy_max_shield=combat.enemy_max_shield,
                    faction_id=combat.faction_id,
                    special_ability=combat.special_ability,
                    ability_cooldown=max(0, combat.ability_cooldown - 1),
                    telegraphed_action=next_telegraph,
                    ai_profile=combat.ai_profile,
                    enemy_intent=next_intent,
                    archetype_id=combat.archetype_id,
                )
                new_log = list(self.state.ship.flight_log[-19:]) + [msg]
                new_ship = self._clone_ship(hull=new_hull, shield=new_shield, tactical_combo=new_combo, streak=new_streak, flight_log=tuple(new_log[-20:]))
                self.state = self._clone_state(ship=new_ship, active_combat=new_combat)
                return True, msg

            elif action == "evasive_burn":
                eng = self.state.ship.power.engines
                chance = min(0.95, 0.50 + (eng / 25.0) * 0.20 + equipment["evasion"])
                if self.rng.random() < chance:
                    msg = "High-G burn successful! Evaded enemy weapon tracking and escaped hostile sector."
                    new_combat = None
                else:
                    dmg = combat.enemy_damage
                    if new_shield >= dmg:
                        new_shield -= dmg
                    else:
                        new_hull = max(0, new_hull - (dmg - new_shield))
                        new_shield = 0
                    msg = f"Evasive burn failed! Suffered {dmg} damage during high-G maneuver."
                    new_combat = combat
                new_log = list(self.state.ship.flight_log[-19:]) + [msg]
                new_ship = self._clone_ship(hull=new_hull, shield=new_shield, tactical_combo=new_combo, streak=new_streak, flight_log=tuple(new_log[-20:]))
                self.state = self._clone_state(ship=new_ship, active_combat=new_combat)
                return True, msg

            elif action == "flee":
                if self.state.ship.fuel < 8:
                    return False, "Insufficient fuel for emergency jump (8 units required)."
                new_fuel = self.state.ship.fuel - 8
                msg = "Emergency hyperspace micro-jump executed. Safely disengaged from hostile sector (expedition streak reset)."
                new_ship = self._clone_ship(hull=new_hull, shield=new_shield, fuel=new_fuel, streak=1, tactical_combo=0, flight_log=tuple(list(self.state.ship.flight_log[-19:]) + [msg]))
                self.state = self._clone_state(ship=new_ship, active_combat=None)
                return True, msg

            else:
                return False, f"Unknown combat action '{action}'. Choices: fire_lasers, drone_strike, target_subsystem, shield_absorb, evasive_burn, flee."

            if enemy_miss:
                enemy_rem_hull = enemy_hull_before
                enemy_rem_shield = enemy_shield_before
                strike_desc = "Enemy AI jinked out of your firing solution; the strike missed."

            # Check if enemy was neutralized
            if enemy_rem_hull <= 0:
                new_credits += combat.bounty_credits
                salvage_granted, salvage_overflow = self._grant_cargo(cargo, combat.salvage_commodity, 2)
                stats["combat_victories"] += 1
                stats["credits_earned"] += combat.bounty_credits
                if any(d.drone_type == "mercenary" and d.specialty == "repair" for d in self.state.ship.fleet_drones):
                    new_hull = min(self.state.ship.max_hull, new_hull + 8)

                salvage_relic, _ = roll_relic_drop(self.rng, bonus_prob=0.20, current_system=self.current_system.name)
                new_relics = list(self.state.ship.relics)
                relic_note = ""
                new_max_hull = self.state.ship.max_hull
                new_max_shield = self.state.ship.max_shield
                if salvage_relic:
                    new_relics.append(salvage_relic)
                    relic_note = f" Salvaged Precursor relic: [{salvage_relic.name}] ({salvage_relic.rarity.upper()})!"
                    new_hull, new_max_hull, new_shield, new_max_shield = self._apply_relic_stat_bonuses(
                        new_hull,
                        new_max_hull,
                        new_shield,
                        new_max_shield,
                        [salvage_relic],
                    )

                updated_contracts, contract_logs = self._progress_contracts("combat", 1)
                new_mastery, xp_logs = self._award_pilot_xp(200, self.state.ship.mastery)

                # Faction and corporate reputation shift upon victory
                new_faction_standings = dict(self.state.ship.faction_standings)
                new_corp_standings = dict(self.state.ship.corp_standings)
                rep_note = ""
                archetype = ENEMY_ARCHETYPES.get(combat.archetype_id)
                if archetype and archetype.rep_rewards:
                    shifts: list[str] = []
                    for entity_id, delta in archetype.rep_rewards.items():
                        if entity_id in CANONICAL_FACTIONS:
                            current = new_faction_standings.get(entity_id, 0)
                            new_faction_standings[entity_id] = max(-100, min(100, current + delta))
                            shifts.append(f"{CANONICAL_FACTIONS[entity_id].name} ({delta:+d})")
                        elif entity_id in CANONICAL_CORPORATIONS:
                            current = new_corp_standings.get(entity_id, 0)
                            new_corp_standings[entity_id] = max(-100, min(100, current + delta))
                            shifts.append(f"{CANONICAL_CORPORATIONS[entity_id].name} ({delta:+d})")
                    if shifts:
                        rep_note = " [Standing: " + ", ".join(shifts) + "]"
                elif combat.faction_id == "outlaw_corsairs":
                    new_faction_standings["sol_coalition"] = min(100, new_faction_standings.get("sol_coalition", 0) + 5)
                    new_faction_standings["nebula_collective"] = min(100, new_faction_standings.get("nebula_collective", 0) + 4)
                    new_faction_standings["vanguard_syndicate"] = min(100, new_faction_standings.get("vanguard_syndicate", 0) + 2)
                    new_faction_standings["outlaw_corsairs"] = max(-100, new_faction_standings.get("outlaw_corsairs", 0) - 10)
                    rep_note = " [Faction Standing: Sol Coalition (+5), Nebula Collective (+4), Void Corsairs (-10)]"
                elif combat.faction_id == "vanguard_syndicate":
                    new_faction_standings["sol_coalition"] = min(100, new_faction_standings.get("sol_coalition", 0) + 6)
                    new_faction_standings["vanguard_syndicate"] = max(-100, new_faction_standings.get("vanguard_syndicate", 0) - 8)
                    rep_note = " [Faction Standing: Sol Coalition (+6), Free Spacers Syndicate (-8)]"
                elif combat.faction_id == "hyperion_dynamics":
                    new_faction_standings["outlaw_corsairs"] = min(100, new_faction_standings.get("outlaw_corsairs", 0) + 6)
                    new_faction_standings["sol_coalition"] = max(-100, new_faction_standings.get("sol_coalition", 0) - 6)
                    rep_note = " [Faction Standing: Void Corsairs (+6), Sol Coalition (-6)]"
                elif combat.faction_id == "precursor_watch":
                    new_faction_standings["precursor_watch"] = min(100, new_faction_standings.get("precursor_watch", 0) + 8)
                    rep_note = " [Faction Standing: Precursor Watch (+8)]"

                msg = (
                    f"VICTORY: {combat.enemy_name} neutralized! "
                    f"Collected {combat.bounty_credits} cr bounty, salvaged {salvage_granted}x {combat.salvage_commodity}"
                    f"{f' ({salvage_overflow} jettisoned: hold full)' if salvage_overflow else ''}.{relic_note}{rep_note}"
                )
                log_entry = f"Combat outcome: {msg}"
                new_log = list(self.state.ship.flight_log[-19:]) + [log_entry] + contract_logs + xp_logs

                new_ship = self._clone_ship(
                    hull=new_hull,
                    max_hull=new_max_hull,
                    shield=new_shield,
                    max_shield=new_max_shield,
                    credits=new_credits,
                    cargo=cargo,
                    relics=tuple(new_relics),
                    mastery=new_mastery,
                    active_contracts=updated_contracts,
                    faction_standings=new_faction_standings,
                    corp_standings=new_corp_standings,
                    tactical_combo=0,
                    streak=new_streak,
                    flight_log=tuple(new_log[-20:]),
                )

                self.state = self._clone_state(
                    ship=new_ship,
                    active_combat=None,
                    stats=stats,
                )
                return True, msg

            # Enemy counter-attack and tactical abilities
            ability_note = ""
            if intent == "ability" and ability_cd == 0 and combat.special_ability != "none":
                if combat.special_ability == "shield_drain":
                    drain_amt = min(15, new_shield)
                    new_shield -= drain_amt
                    enemy_rem_shield = min(combat.enemy_max_shield, enemy_rem_shield + drain_amt)
                    ability_note = f" [ABILITY: Shield Drain siphoned {drain_amt} MW from your deflectors!]"
                    ability_cd = 2
                elif combat.special_ability == "emp_overload":
                    new_combo = 0
                    enemy_rem_damage += 8
                    ability_note = " [ABILITY: EMP Overload shockwave disrupted tactical systems!]"
                    ability_cd = 2
                elif combat.special_ability == "nanite_regen" and enemy_rem_shield > 0:
                    enemy_rem_hull = min(combat.enemy_max_hull, enemy_rem_hull + 20)
                    ability_note = " [ABILITY: Nanite Swarm regenerated +20 enemy Hull!]"
                    ability_cd = 2
                elif combat.special_ability == "tachyon_lance":
                    new_hull = max(0, new_hull - 15)
                    ability_note = " [ABILITY: Tachyon Lance phase-pierced your shields for 15 direct hull damage!]"
                    ability_cd = 2

            # Standard counter-battery
            inbound = int(enemy_rem_damage * (1.5 if intent == "execute" else 1.0))
            evasion_note = ""
            if inbound > 0 and (equipment["evasion"] + mercenary_evasion) > 0.0 and self.rng.random() < (equipment["evasion"] + mercenary_evasion):
                inbound = 0
                evasion_note = " [Ion afterburners and ECM escort evaded incoming fire!]"
            if new_shield >= inbound:
                new_shield -= inbound
            else:
                overflow = inbound - new_shield
                new_shield = 0
                new_hull = max(0, new_hull - overflow)
                new_combo = 0
                if new_hull < 50:
                    new_streak = max(1, self.state.ship.streak - 1)

            # AI selects the next maneuver from live hull, shield, combo, and profile state.
            next_intent, next_telegraph = choose_enemy_intent(
                profile=combat.ai_profile,
                special_ability=combat.special_ability,
                ability_ready=ability_cd == 0,
                enemy_hull=enemy_rem_hull,
                enemy_max_hull=combat.enemy_max_hull,
                enemy_shield=enemy_rem_shield,
                enemy_max_shield=combat.enemy_max_shield,
                player_hull=new_hull,
                player_max_hull=self.state.ship.max_hull,
                player_shield=new_shield,
                player_max_shield=self.state.ship.max_shield,
                player_combo=new_combo,
            )

            msg = f"{strike_desc} Inbound counter-battery dealt {inbound} damage.{evasion_note}{ability_note} (Enemy HP: {enemy_rem_hull}/{combat.enemy_max_hull}, Shield: {enemy_rem_shield}/{combat.enemy_max_shield})"

            new_combat = CombatEncounter(
                id=combat.id,
                enemy_name=combat.enemy_name,
                enemy_class=combat.enemy_class,
                enemy_hull=enemy_rem_hull,
                enemy_max_hull=combat.enemy_max_hull,
                enemy_damage=enemy_rem_damage,
                bounty_credits=combat.bounty_credits,
                salvage_commodity=combat.salvage_commodity,
                enemy_shield=enemy_rem_shield,
                enemy_max_shield=combat.enemy_max_shield,
                faction_id=combat.faction_id,
                special_ability=combat.special_ability,
                ability_cooldown=ability_cd,
                telegraphed_action=next_telegraph,
                ai_profile=combat.ai_profile,
                enemy_intent=next_intent,
                archetype_id=combat.archetype_id,
            )

            new_log = list(self.state.ship.flight_log[-19:]) + [msg]
            new_ship = self._clone_ship(
                hull=new_hull,
                shield=new_shield,
                tactical_combo=new_combo,
                streak=new_streak,
                flight_log=tuple(new_log[-20:]),
            )

            self.state = self._clone_state(
                ship=new_ship,
                active_combat=new_combat,
                stats=stats,
            )
            return True, msg

    def resolve_anomaly(self, choice_id: str) -> tuple[bool, str]:
        """Resolve current deep-space anomaly encounter with power-check validation."""
        with self.lock:
            anomaly = self.state.active_anomaly
            if not anomaly:
                return False, "No active spatial anomaly to resolve."

            choice = next((c for c in anomaly.choices if c.choice_id == choice_id), None)
            if not choice:
                return False, f"Unknown resolution option '{choice_id}'."

            # Verify power threshold
            power_val = 0
            if choice.required_power != "none":
                power_val = getattr(self.state.ship.power, choice.required_power, 0)
                if power_val < choice.min_power_threshold:
                    hull_loss = 15
                    new_hull = max(0, self.state.ship.hull - hull_loss)
                    log_entry = (
                        f"CRITICAL: Failed {choice.required_power.upper()} check ({power_val}% < {choice.min_power_threshold}%)! "
                        f"Hull suffered {hull_loss} damage during anomaly surge."
                    )
                    new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

                    new_ship = self._clone_ship(
                        hull=new_hull,
                        flight_log=tuple(new_log),
                    )

                    self.state = self._clone_state(
                        ship=new_ship,
                        active_anomaly=None,
                    )

                    return False, log_entry

            # Success outcome
            new_hull = min(self.state.ship.max_hull, max(0, self.state.ship.hull + choice.hull_delta))
            new_credits = max(0, self.state.ship.credits + choice.credits_delta)
            new_fuel = min(self.state.ship.max_fuel, max(0, self.state.ship.fuel + choice.fuel_delta))

            cargo = dict(self.state.ship.cargo)
            overflow_items: list[str] = []
            for item_k, item_v in choice.cargo_reward.items():
                granted, overflow = self._grant_cargo(cargo, item_k, item_v)
                if overflow:
                    overflow_items.append(f"{overflow}x {item_k}")

            log_entry = f"Anomaly resolved: {choice.outcome_text}"
            if overflow_items:
                log_entry += f" Hold full: jettisoned {', '.join(overflow_items)}."
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            new_ship = self._clone_ship(
                hull=new_hull,
                fuel=new_fuel,
                credits=new_credits,
                cargo=cargo,
                flight_log=tuple(new_log),
            )

            stats = dict(self.state.stats)
            stats["anomalies_resolved"] += 1
            if choice.credits_delta > 0:
                stats["credits_earned"] += choice.credits_delta

            self.state = self._clone_state(
                ship=new_ship,
                active_anomaly=None,
                stats=stats,
            )

            return True, choice.outcome_text

    def repair_hull(self, amount: int = 25) -> tuple[bool, str]:
        """Repair ship hull integrity at orbital station."""
        with self.lock:
            if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
                return False, "Repair amount must be a positive integer."
            body = self.orbiting_body
            if not body or not body.station_dockable:
                return False, "Repair drydocks available at orbital stations or colonies only."

            needed = self.state.ship.max_hull - self.state.ship.hull
            if needed <= 0:
                return False, "Hull integrity already at 100% capacity."

            actual = min(amount, needed)
            faction_id = get_faction_id_from_name(self.current_system.faction)
            perks = get_faction_service_perks(faction_id, self.state.ship.faction_standings.get(faction_id, 0))
            cost = max(0, int(actual * 4 * (1.0 - float(perks["repair_discount"]))))
            if self.state.ship.credits < cost:
                return False, f"Insufficient credits: repair costs {cost} cr ({actual} HP)."

            new_ship = self._clone_ship(
                hull=self.state.ship.hull + actual,
                credits=self.state.ship.credits - cost,
                flight_log=tuple(list(self.state.ship.flight_log[-19:]) + [f"Drydock repair: +{actual} HP for {cost} cr."]),
            )

            self.state = self._clone_state(ship=new_ship)
            return True, f"Repairs completed: +{actual} HP restored for {cost} cr."

    def refuel(self, amount: int = 20) -> tuple[bool, str]:
        """Refuel quantum drive at orbital station."""
        with self.lock:
            if not isinstance(amount, int) or isinstance(amount, bool) or amount <= 0:
                return False, "Refuel amount must be a positive integer."
            body = self.orbiting_body
            if not body or not body.station_dockable:
                return False, "Fuel refinery available at orbital stations or colonies only."

            needed = self.state.ship.max_fuel - self.state.ship.fuel
            if needed <= 0:
                return False, "Fuel reserves already at maximum capacity."

            actual = min(amount, needed)
            faction_id = get_faction_id_from_name(self.current_system.faction)
            perks = get_faction_service_perks(faction_id, self.state.ship.faction_standings.get(faction_id, 0))
            cost = 0 if perks["free_refuel"] else actual * 6
            if self.state.ship.credits < cost:
                return False, f"Insufficient credits: refueling costs {cost} cr ({actual} fuel)."

            new_ship = self._clone_ship(
                fuel=self.state.ship.fuel + actual,
                credits=self.state.ship.credits - cost,
                flight_log=tuple(list(self.state.ship.flight_log[-19:]) + [f"Refueled +{actual} quantum fuel for {cost} cr."]),
            )

            self.state = self._clone_state(ship=new_ship)

            return True, f"Fuel tanks replenished: +{actual} units for {cost} cr."

    def step_orbits(self, delta_time: float = 1.0) -> None:
        """Advance celestial bodies along orbital mechanics paths and cycle fleet drones."""
        with self.lock:
            updated_systems: dict[str, StarSystem] = {}
            for sys_id, sys_obj in self.state.systems.items():
                updated_bodies = []
                for b in sys_obj.bodies:
                    new_angle = (b.current_angle + b.orbit_speed * delta_time) % (2 * math.pi)
                    updated_bodies.append(replace(b, current_angle=new_angle))
                updated_systems[sys_id] = StarSystem(
                    id=sys_obj.id,
                    name=sys_obj.name,
                    seed=sys_obj.seed,
                    x=sys_obj.x,
                    y=sys_obj.y,
                    spectral_type=sys_obj.spectral_type,
                    color=sys_obj.color,
                    security=sys_obj.security,
                    faction=sys_obj.faction,
                    bodies=tuple(updated_bodies),
                    connections=sys_obj.connections,
                    dominant_corp=sys_obj.dominant_corp,
                )

            self.state = self._clone_state(systems=updated_systems)

    def claim_contract(self, contract_id: str) -> tuple[bool, str, dict[str, Any]]:
        """Claim rewards for a fulfilled contract and immediately draw a new assignment."""
        with self.lock:
            found = None
            for c in self.state.ship.active_contracts:
                if c.id == contract_id:
                    found = c
                    break

            if not found:
                return False, f"Contract '{contract_id}' not found in active assignments.", {}

            if not found.completed:
                return False, f"Contract '{found.title}' is not yet completed ({found.current_count}/{found.target_count}).", {}

            new_credits = self.state.ship.credits + found.reward_credits
            new_mastery, xp_logs = self._award_pilot_xp(found.reward_xp, self.state.ship.mastery)

            # Roll relic if tier specified
            relic = None
            new_relics = list(self.state.ship.relics)
            if found.reward_relic_tier:
                relic, _ = roll_relic_drop(self.rng, forced_tier=found.reward_relic_tier, current_system=self.current_system.name)
                if relic:
                    new_relics.append(relic)

            # Continuous Zeigarnik cycle: replace completed contract with a new task
            new_contract = generate_contract(self.rng, category=found.category)
            updated_contracts = tuple([c for c in self.state.ship.active_contracts if c.id != contract_id] + [new_contract])

            relic_msg = f" Discovered Precursor Relic [{relic.name}] ({relic.rarity.upper()})!" if relic else ""
            log_entry = f"CONTRACT CLAIMED: [{found.title}] rewarded {found.reward_credits} cr and {found.reward_xp} XP.{relic_msg}"
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry] + xp_logs

            stats = dict(self.state.stats)
            stats["credits_earned"] += found.reward_credits
            stats["contracts_completed"] = stats.get("contracts_completed", 0) + 1

            new_hull, new_max_hull, new_shield, new_max_shield = self._apply_relic_stat_bonuses(
                self.state.ship.hull,
                self.state.ship.max_hull,
                self.state.ship.shield,
                self.state.ship.max_shield,
                [relic] if relic else [],
            )

            new_ship = self._clone_ship(
                hull=new_hull,
                max_hull=new_max_hull,
                shield=new_shield,
                max_shield=new_max_shield,
                credits=new_credits,
                mastery=new_mastery,
                relics=tuple(new_relics),
                active_contracts=updated_contracts,
                flight_log=tuple(new_log[-20:]),
            )

            self.state = self._clone_state(ship=new_ship, stats=stats)

            return True, f"Claimed {found.title}: +{found.reward_credits} cr, +{found.reward_xp} XP.{relic_msg} New contract: [{new_contract.title}].", {
                "reward_credits": found.reward_credits,
                "reward_xp": found.reward_xp,
                "relic": relic.to_dict() if relic else None,
                "new_contract": new_contract.to_dict(),
            }

    def unlock_talent(self, talent_id: str) -> tuple[bool, str]:
        """Unlock a Pilot Specialization Perk using available talent points."""
        with self.lock:
            talent = PILOT_TALENTS.get(talent_id)
            if not talent:
                return False, f"Unknown pilot talent '{talent_id}'. Available: {', '.join(PILOT_TALENTS.keys())}."

            mastery = self.state.ship.mastery
            if mastery.talent_points < 1:
                return False, "Insufficient talent points (0 available). Advance Pilot Mastery level first."

            if talent_id in mastery.specializations:
                return False, f"Perk '{talent['name']}' is already unlocked."

            missing = [req for req in talent.get("requires", ()) if req not in mastery.specializations]
            if missing:
                names = ", ".join(PILOT_TALENTS[r]["name"] for r in missing if r in PILOT_TALENTS)
                return False, f"Prerequisite perk(s) required: {names}."

            new_specs = tuple(list(mastery.specializations) + [talent_id])
            new_mastery = PilotMastery(
                level=mastery.level,
                xp=mastery.xp,
                next_level_xp=mastery.next_level_xp,
                talent_points=mastery.talent_points - 1,
                specializations=new_specs,
            )

            log_entry = f"★ SPECIALIZATION UNLOCKED: Pilot mastered [{talent['name']}]! {talent['description']}"
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            new_ship = self._clone_ship(
                mastery=new_mastery,
                flight_log=tuple(new_log[-20:]),
            )

            self.state = self._clone_state(ship=new_ship)
            return True, f"Specialization unlocked: {talent['name']}."

    def make_story_choice(self, choice_id: str) -> tuple[bool, str]:
        """Resolve a branching story dilemma in the active campaign chapter."""
        with self.lock:
            story = self.state.ship.story
            if story.completed or story.current_chapter_index >= len(story.chapters):
                return False, "Campaign storyline is already complete."

            current_chapter = story.chapters[story.current_chapter_index]
            if current_chapter.completed:
                return False, f"Chapter '{current_chapter.title}' is already resolved."

            if current_chapter.target_system_id and self.state.ship.current_system_id != current_chapter.target_system_id:
                return False, f"Must be in {current_chapter.target_system_id.title()} System to resolve '{current_chapter.title}' (currently in {self.state.ship.current_system_id.title()})."

            found_choice = None
            for ch in current_chapter.choices:
                if ch.id == choice_id:
                    found_choice = ch
                    break

            if not found_choice:
                avail = ", ".join(c.id for c in current_chapter.choices)
                return False, f"Choice '{choice_id}' not found. Available choices: {avail}."

            cost = getattr(found_choice, "cost_credits", 0)
            if cost > 0 and self.state.ship.credits < cost:
                return False, f"Insufficient credits ({self.state.ship.credits} available, {cost} required)."

            new_credits = self.state.ship.credits + found_choice.reward_credits - cost
            new_relics = list(self.state.ship.relics)
            new_max_hull = self.state.ship.max_hull
            new_hull = self.state.ship.hull
            new_max_shield = self.state.ship.max_shield
            new_shield = self.state.ship.shield
            awarded_relic = None

            if found_choice.reward_relic_id and found_choice.reward_relic_id in STORY_RELICS:
                awarded_relic = STORY_RELICS[found_choice.reward_relic_id]
                existing_relic_ids = {r.id for r in new_relics}
                if awarded_relic.id not in existing_relic_ids:
                    new_relics.append(awarded_relic)
                    new_hull, new_max_hull, new_shield, new_max_shield = self._apply_relic_stat_bonuses(
                        new_hull,
                        new_max_hull,
                        new_shield,
                        new_max_shield,
                        [awarded_relic],
                    )

            new_rep = dict(story.reputation)
            align = found_choice.faction_alignment
            new_rep[align] = new_rep.get(align, 0) + 25

            standing_key = {
                "coalition": "sol_coalition",
                "syndicate": "vanguard_syndicate",
                "precursor": "precursor_watch",
            }.get(align)
            new_faction_standings = dict(self.state.ship.faction_standings)
            if standing_key:
                new_faction_standings[standing_key] = max(
                    -100, min(100, new_faction_standings.get(standing_key, 0) + 25)
                )

            updated_chapters = list(story.chapters)
            updated_chapters[story.current_chapter_index] = StoryChapter(
                chapter_index=current_chapter.chapter_index,
                title=current_chapter.title,
                target_system_id=current_chapter.target_system_id,
                objective=current_chapter.objective,
                transmission=current_chapter.transmission,
                choices=current_chapter.choices,
                completed=True,
                chosen_id=choice_id,
            )

            next_idx = story.current_chapter_index + 1
            is_campaign_done = next_idx >= len(story.chapters)
            new_transmissions = list(story.transmission_log)

            if not is_campaign_done:
                next_ch = updated_chapters[next_idx]
                new_transmissions.append(next_ch.transmission)

            new_story = StoryState(
                campaign_title=story.campaign_title,
                current_chapter_index=next_idx,
                chapters=tuple(updated_chapters),
                transmission_log=tuple(new_transmissions),
                reputation=new_rep,
                completed=is_campaign_done,
            )

            relic_msg = f" Acquired unique relic [{awarded_relic.name}]!" if awarded_relic else ""
            log_entry = f"STORY DECISION: [{found_choice.text}] resolved. +{found_choice.reward_credits} cr.{relic_msg}"
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            new_ship = self._clone_ship(
                hull=new_hull,
                max_hull=new_max_hull,
                shield=new_shield,
                max_shield=new_max_shield,
                credits=new_credits,
                relics=tuple(new_relics),
                story=new_story,
                faction_standings=new_faction_standings,
                flight_log=tuple(new_log[-20:]),
            )

            self.state = self._clone_state(ship=new_ship)
            msg = f"Decision resolved: {found_choice.outcome_text}{relic_msg}"
            if is_campaign_done:
                msg += " CAMPAIGN FINALE: The Precursor Cipher storyline concluded!"

            return True, msg

    def skip_tutorial(self) -> tuple[bool, str]:
        """Skip Cadet Flight Academy and unlock unrestricted operational status."""
        with self.lock:
            cur = self.state.ship.tutorial
            new_tut = TutorialState(
                active=False,
                current_step_index=cur.current_step_index,
                steps=cur.steps,
                completed=False,
                skipped=True,
            )
            new_log = list(self.state.ship.flight_log[-19:]) + ["ACADEMY: Cadet Flight Academy skipped by commander."]
            self.state = self._clone_state(ship=self._clone_ship(tutorial=new_tut, flight_log=tuple(new_log[-20:])))
            return True, "Cadet Flight Academy skipped. Full operational control active."

    def reset_tutorial(self) -> tuple[bool, str]:
        """Reset Cadet Flight Academy to step 1 for revision or retraining."""
        with self.lock:
            new_tut = generate_initial_tutorial()
            new_log = list(self.state.ship.flight_log[-19:]) + ["ACADEMY: Cadet Flight Academy restarted."]
            self.state = self._clone_state(ship=self._clone_ship(tutorial=new_tut, flight_log=tuple(new_log[-20:])))
            return True, "Cadet Flight Academy reset to Step 1."

    @property
    def current_chassis_id(self) -> str:
        """Id of the chassis matching the ship's commissioned class (falls back to the class name)."""
        return next(
            (c.id for c in CATALOG_CHASSIS if c.ship_class == self.state.ship.ship_class),
            self.state.ship.ship_class,
        )

    def get_status_snapshot(self) -> dict[str, Any]:
        """Produce a comprehensive JSON serializable telemetry snapshot for the HUD."""
        with self.lock:
            cur_sys = self.current_system
            orb_body = self.orbiting_body
            market_quotes = []
            if orb_body and orb_body.station_dockable:
                quotes = [
                    calculate_dynamic_market_quote(cur_sys, orb_body, c, self.state.economy)
                    for c in CANONICAL_COMMODITIES
                ]
                market_quotes = [
                    {
                        "commodity_id": q.commodity_id,
                        "name": q.name,
                        "category": q.category,
                        "buy_price": q.buy_price,
                        "sell_price": q.sell_price,
                        "supply": q.supply,
                        "demand": q.demand,
                    }
                    for q in quotes
                ]

            return {
                "ship": self.state.ship.to_dict(),
                "current_system": cur_sys.to_dict(),
                "orbiting_body": orb_body.to_dict() if orb_body else None,
                "visited_systems": list(self.state.visited_systems),
                "active_anomaly": self.state.active_anomaly.to_dict() if self.state.active_anomaly else None,
                "active_combat": self.state.active_combat.to_dict() if self.state.active_combat else None,
                "time": self.state.time.to_dict(),
                "stats": dict(self.state.stats),
                "equipment_bonuses": calculate_equipment_bonuses(self.state.ship),
                "market_quotes": market_quotes,
                "catalog_upgrades": [u.to_dict() for u in CATALOG_UPGRADES],
                "catalog_drones": CATALOG_DRONE_TEMPLATES,
                "catalog_talents": PILOT_TALENTS,
                "catalog_relics": [r.to_dict() for r in CATALOG_RELICS],
                "story_chapters": [c.to_dict() for c in CAMPAIGN_CHAPTERS],
                "story_chapters_map": {c.id: c.to_dict() for c in CAMPAIGN_CHAPTERS},
                "factions": {
                    fid: {
                        **f.to_dict(),
                        "standing": self.state.ship.faction_standings.get(fid, 0),
                        "standing_tier": get_faction_standing_tier(self.state.ship.faction_standings.get(fid, 0))[0],
                        "active_perk": get_faction_standing_tier(self.state.ship.faction_standings.get(fid, 0))[1],
                    }
                    for fid, f in CANONICAL_FACTIONS.items()
                },
                "corporations": {
                    cid: {
                        **c.to_dict(),
                        "standing": self.state.ship.corp_standings.get(cid, 0),
                    }
                    for cid, c in CANONICAL_CORPORATIONS.items()
                },
                "enemy_archetypes": {aid: asdict(a) for aid, a in ENEMY_ARCHETYPES.items()},
                "economy": self.state.economy.to_dict(),
                "inventory_manifest": get_inventory_manifest(self.state.ship.cargo),
                "trade_routes": get_galactic_trade_routes(self.state.systems, self.state.economy),
                "catalog_chassis": [c.to_dict() for c in CATALOG_CHASSIS],
                "available_chassis": [c.to_dict() for c in get_available_chassis(self.current_chassis_id)],
                "ai_captains": [c.to_dict() for c in self.state.ai_captains],
                "depots": [d.to_dict() for d in self.state.depots],
                "messages": [m.to_dict() for m in self.state.messages],
                "events": [e.to_dict() for e in self.state.events],
                "undismissed_events": [e.to_dict() for e in self.state.events if not e.dismissed],
                "travel": self.state.ship.travel.to_dict() if self.state.ship.travel else None,
                "allies": list(self.state.ship.allies),
                "quests": self.get_quests(),
                "mercenary_catalog": MERCENARY_CATALOG,
                "fleet_stats": [
                    {
                        **d.to_dict(),
                        "kind": "mercenary" if d.drone_type == "mercenary" else "fleet",
                        "yield_rate": round(d.efficiency * (0.5 + d.integrity / 200.0), 2),
                    }
                    for d in self.state.ship.fleet_drones
                ],
            }

    def get_quests(self) -> list[dict[str, Any]]:
        """Return a unified quest panel view of the story chapter and active contracts."""
        quests: list[dict[str, Any]] = []
        story = self.state.ship.story
        if not story.completed and story.current_chapter_index < len(story.chapters):
            chapter = story.chapters[story.current_chapter_index]
            quests.append({
                "id": f"story_{chapter.chapter_index}",
                "kind": "story",
                "title": chapter.title,
                "description": chapter.objective,
                "target": chapter.target_system_id,
                "progress": 0,
                "target_count": 1,
                "completed": chapter.completed,
                "reward": "Campaign progression",
            })
        for contract in self.state.ship.active_contracts:
            quests.append({
                "id": contract.id,
                "kind": "contract",
                "title": contract.title,
                "description": contract.description,
                "target": "",
                "progress": contract.current_count,
                "target_count": contract.target_count,
                "completed": contract.completed,
                "reward": f"{contract.reward_credits} cr / {contract.reward_xp} XP",
            })
        return quests

    def _find_ai_captain(self, captain_id: str) -> AICaptain | None:
        return next((c for c in self.state.ai_captains if c.id == captain_id), None)

    def _replace_ai_captain(self, captain: AICaptain) -> tuple[AICaptain, ...]:
        return tuple(captain if c.id == captain.id else c for c in self.state.ai_captains)

    def interact_ai(
        self,
        captain_id: str,
        action: str,
        commodity_id: str | None = None,
        quantity: int = 1,
    ) -> tuple[bool, str]:
        """Hail, trade with, hire, or ally with an autonomous captain."""
        with self.lock:
            captain = self._find_ai_captain(captain_id)
            if not captain:
                return False, f"Unknown AI captain '{captain_id}'."
            action = action.lower()
            if action == "hail":
                updated = replace(captain, trust=min(100, captain.trust + 2), standing=min(100, captain.standing + 1))
                self.state = self._clone_state(ai_captains=self._replace_ai_captain(updated))
                return True, f"{captain.name}: '{captain.description}' Quantum link trust increased."
            if action in ("buy", "sell"):
                if not commodity_id or commodity_id not in COMMODITY_MAP:
                    return False, "A valid commodity is required for captain trade."
                quantity = max(1, int(quantity))
                price = COMMODITY_MAP[commodity_id].base_price
                cargo = dict(self.state.ship.cargo)
                captain_cargo = dict(captain.cargo)
                if action == "buy":
                    available = captain_cargo.get(commodity_id, 0)
                    if available < quantity:
                        return False, f"{captain.name} has only {available} units of {commodity_id}."
                    cost = int(price * 1.10) * quantity
                    if self.state.ship.credits < cost:
                        return False, f"Insufficient credits: {cost} cr required."
                    incoming = calculate_cargo_volume({commodity_id: quantity})
                    if calculate_cargo_volume(cargo) + incoming > self.state.ship.cargo_capacity:
                        return False, "Cargo hold has insufficient free volume for this purchase."
                    captain_cargo[commodity_id] = available - quantity
                    cargo[commodity_id] = cargo.get(commodity_id, 0) + quantity
                    new_credits = self.state.ship.credits - cost
                    updated_captain = replace(captain, cargo=captain_cargo, credits=captain.credits + cost, trust=min(100, captain.trust + 1))
                    message = f"Purchased {quantity}x {commodity_id} from {captain.name} for {cost} cr."
                else:
                    available = cargo.get(commodity_id, 0)
                    if available < quantity:
                        return False, f"You have only {available} units of {commodity_id}."
                    revenue = int(price * 0.90) * quantity
                    cargo[commodity_id] = available - quantity
                    captain_cargo[commodity_id] = captain_cargo.get(commodity_id, 0) + quantity
                    new_credits = self.state.ship.credits + revenue
                    updated_captain = replace(captain, cargo=captain_cargo, credits=max(0, captain.credits - revenue), trust=min(100, captain.trust + 1))
                    message = f"Sold {quantity}x {commodity_id} to {captain.name} for {revenue} cr."
                new_ship = self._clone_ship(credits=new_credits, cargo=cargo)
                self.state = self._clone_state(ship=new_ship, ai_captains=self._replace_ai_captain(updated_captain))
                return True, message
            if action == "hire":
                if captain.archetype != "mercenary":
                    return False, f"{captain.name} is not a mercenary contractor."
                if captain.hired:
                    return False, f"{captain.name} is already under contract."
                cost = 2500
                if self.state.ship.credits < cost:
                    return False, f"Insufficient credits: {cost} cr required to hire {captain.name}."
                drone = FleetDrone(
                    id=f"merc_{captain.id}",
                    name=captain.name,
                    drone_type="mercenary",
                    assigned_system_id=self.state.ship.current_system_id,
                    status="idle",
                    efficiency=1.0,
                    integrity=100,
                    specialty="assault",
                )
                new_ship = self._clone_ship(
                    credits=self.state.ship.credits - cost,
                    fleet_drones=self.state.ship.fleet_drones + (drone,),
                )
                updated = replace(captain, hired=True, trust=min(100, captain.trust + 10))
                self.state = self._clone_state(ship=new_ship, ai_captains=self._replace_ai_captain(updated))
                return True, f"{captain.name} joined your fleet as a mercenary (+14 combat damage)."
            if action == "ally":
                if captain.ally or captain.id in self.state.ship.allies:
                    return False, f"{captain.name} is already an ally."
                if captain.trust < 50:
                    return False, f"{captain.name} requires 50 trust before an alliance (current: {captain.trust})."
                updated = replace(captain, ally=True, trust=100)
                new_ship = self._clone_ship(allies=self.state.ship.allies + (captain.id,))
                self.state = self._clone_state(ship=new_ship, ai_captains=self._replace_ai_captain(updated))
                return True, f"Alliance formed with {captain.name}. +5% trade margin and fleet support."
            return False, "Unknown AI action. Use hail, buy, sell, hire, or ally."

    def send_quantum_message(self, recipient: str, subject: str, body: str) -> tuple[bool, str]:
        """Send an intergalactic quantum-encrypted message."""
        with self.lock:
            if not recipient.strip() or not subject.strip() or not body.strip():
                return False, "Recipient, subject, and message body are required."
            message = QuantumMessage(
                id=f"msg_{self.state.time.tick}_{len(self.state.messages) + 1}",
                sender=self.state.ship.commander_name,
                recipient=recipient.strip(),
                subject=subject.strip()[:120],
                body=body.strip()[:2000],
                tick=self.state.time.tick,
            )
            self.state = self._clone_state(messages=self.state.messages + (message,))
            return True, f"Quantum message sent to {message.recipient}."

    def mark_message_read(self, message_id: str) -> tuple[bool, str]:
        with self.lock:
            message = next((m for m in self.state.messages if m.id == message_id), None)
            if not message:
                return False, f"Unknown message '{message_id}'."
            updated = tuple(replace(m, read=True) if m.id == message_id else m for m in self.state.messages)
            self.state = self._clone_state(messages=updated)
            return True, f"Message '{message.subject}' marked as read."

    def _depot_for_current_system(self) -> Depot | None:
        return next((d for d in self.state.depots if d.system_id == self.state.ship.current_system_id), None)

    def _require_docked(self) -> tuple[bool, str]:
        if self.state.active_combat is not None:
            return False, "Depot operations are unavailable during combat."
        body = self.orbiting_body
        if not body or not body.station_dockable:
            return False, "Dock at an orbital station or colony to access depot services."
        return True, ""

    def deposit_cargo(self, item_id: str, quantity: int = 1) -> tuple[bool, str]:
        with self.lock:
            ok, msg = self._require_docked()
            if not ok:
                return False, msg
            quantity = int(quantity)
            if quantity <= 0:
                return False, "Deposit quantity must be positive."
            depot = self._depot_for_current_system()
            if not depot:
                return False, "No depot is registered in this system."
            cargo = dict(self.state.ship.cargo)
            if cargo.get(item_id, 0) < quantity:
                return False, f"Cargo hold contains only {cargo.get(item_id, 0)} units of {item_id}."
            incoming = calculate_cargo_volume({item_id: quantity})
            if calculate_cargo_volume(depot.cargo) + incoming > depot.capacity:
                return False, "Depot capacity exceeded."
            cargo[item_id] -= quantity
            if cargo[item_id] <= 0:
                cargo.pop(item_id, None)
            depot_cargo = dict(depot.cargo)
            depot_cargo[item_id] = depot_cargo.get(item_id, 0) + quantity
            updated_depot = replace(depot, cargo=depot_cargo)
            depots = tuple(updated_depot if d.id == depot.id else d for d in self.state.depots)
            self.state = self._clone_state(ship=self._clone_ship(cargo=cargo), depots=depots)
            return True, f"Deposited {quantity}x {item_id} into {depot.name}."

    def withdraw_cargo(self, item_id: str, quantity: int = 1) -> tuple[bool, str]:
        with self.lock:
            ok, msg = self._require_docked()
            if not ok:
                return False, msg
            quantity = int(quantity)
            if quantity <= 0:
                return False, "Withdraw quantity must be positive."
            depot = self._depot_for_current_system()
            if not depot:
                return False, "No depot is registered in this system."
            if depot.cargo.get(item_id, 0) < quantity:
                return False, f"Depot contains only {depot.cargo.get(item_id, 0)} units of {item_id}."
            cargo = dict(self.state.ship.cargo)
            incoming = calculate_cargo_volume({item_id: quantity})
            if calculate_cargo_volume(cargo) + incoming > self.state.ship.cargo_capacity:
                return False, "Cargo hold has insufficient free volume."
            depot_cargo = dict(depot.cargo)
            depot_cargo[item_id] -= quantity
            if depot_cargo[item_id] <= 0:
                depot_cargo.pop(item_id, None)
            cargo[item_id] = cargo.get(item_id, 0) + quantity
            updated_depot = replace(depot, cargo=depot_cargo)
            depots = tuple(updated_depot if d.id == depot.id else d for d in self.state.depots)
            self.state = self._clone_state(ship=self._clone_ship(cargo=cargo), depots=depots)
            return True, f"Withdrew {quantity}x {item_id} from {depot.name}."

    def sell_from_depot(self, item_id: str, quantity: int = 1) -> tuple[bool, str]:
        with self.lock:
            ok, msg = self._require_docked()
            if not ok:
                return False, msg
            quantity = int(quantity)
            if quantity <= 0:
                return False, "Sale quantity must be positive."
            depot = self._depot_for_current_system()
            if not depot:
                return False, "No depot is registered in this system."
            if depot.cargo.get(item_id, 0) < quantity:
                return False, f"Depot contains only {depot.cargo.get(item_id, 0)} units of {item_id}."
            body = self.orbiting_body
            quotes = GalaxyGenerator.get_market_quotes(self.current_system, body)
            quote = next((q for q in quotes if q.commodity_id == item_id), None)
            if not quote:
                return False, f"No market quote is available for {item_id}."
            revenue = quote.sell_price * quantity
            depot_cargo = dict(depot.cargo)
            depot_cargo[item_id] -= quantity
            if depot_cargo[item_id] <= 0:
                depot_cargo.pop(item_id, None)
            updated_depot = replace(depot, cargo=depot_cargo)
            depots = tuple(updated_depot if d.id == depot.id else d for d in self.state.depots)
            stats = dict(self.state.stats)
            stats["trades"] = stats.get("trades", 0) + 1
            stats["credits_earned"] = stats.get("credits_earned", 0) + revenue
            self.state = self._clone_state(
                ship=self._clone_ship(credits=self.state.ship.credits + revenue),
                depots=depots,
                stats=stats,
            )
            return True, f"Sold {quantity}x {item_id} from {depot.name} for {revenue} cr."

    def land_on_body(self, body_id: str) -> tuple[bool, str]:
        """Land on a habitable body and collect surface discovery rewards."""
        with self.lock:
            body = next((b for b in self.current_system.bodies if b.id == body_id), None)
            if not body:
                return False, f"Unknown body '{body_id}' in {self.current_system.name}."
            if self.state.ship.orbiting_body_id != body_id:
                return False, "Establish orbit around the body before landing."
            if not body.landable:
                return False, f"{body.name} is not rated for habitable landing operations."
            if self.state.ship.landed_body_id == body_id:
                return False, f"Already landed on {body.name}."
            reward = 150 + int(body.radius_km / 1000) * 5
            stats = dict(self.state.stats)
            stats["landings"] = stats.get("landings", 0) + 1
            stats["credits_earned"] = stats.get("credits_earned", 0) + reward
            log_entry = f"SURFACE LANDING: Touched down on {body.name}. Survey reward +{reward} cr."
            new_ship = self._clone_ship(
                credits=self.state.ship.credits + reward,
                landed_body_id=body_id,
                flight_log=tuple(list(self.state.ship.flight_log[-19:]) + [log_entry]),
            )
            self.state = self._clone_state(ship=new_ship, stats=stats)
            return True, log_entry

    def hire_mercenary(self, merc_id: str) -> tuple[bool, str]:
        with self.lock:
            merc = MERCENARY_CATALOG.get(merc_id)
            if not merc:
                return False, f"Unknown mercenary '{merc_id}'."
            ok, msg = self._require_docked()
            if not ok:
                return False, msg
            if any(d.specialty == merc["specialty"] and d.drone_type == "mercenary" for d in self.state.ship.fleet_drones):
                return False, f"A {merc['specialty']} mercenary is already under contract."
            cost = int(merc["cost"])
            if self.state.ship.credits < cost:
                return False, f"Insufficient credits: {cost} cr required."
            drone = FleetDrone(
                id=f"merc_{merc_id}_{len(self.state.ship.fleet_drones) + 1}",
                name=str(merc["name"]),
                drone_type="mercenary",
                assigned_system_id=self.state.ship.current_system_id,
                status="idle",
                efficiency=1.0,
                integrity=100,
                specialty=str(merc["specialty"]),
            )
            new_ship = self._clone_ship(
                credits=self.state.ship.credits - cost,
                fleet_drones=self.state.ship.fleet_drones + (drone,),
            )
            self.state = self._clone_state(ship=new_ship)
            return True, f"Hired {merc['name']} for {cost} cr ({merc['description']})."

    def dismiss_fleet_unit(self, drone_id: str) -> tuple[bool, str]:
        with self.lock:
            drone = next((d for d in self.state.ship.fleet_drones if d.id == drone_id), None)
            if not drone:
                return False, f"Unknown fleet unit '{drone_id}'."
            remaining = tuple(d for d in self.state.ship.fleet_drones if d.id != drone_id)
            self.state = self._clone_state(ship=self._clone_ship(fleet_drones=remaining))
            return True, f"Fleet unit '{drone.name}' dismissed."

    def refit_fleet_unit(self, drone_id: str) -> tuple[bool, str]:
        with self.lock:
            ok, msg = self._require_docked()
            if not ok:
                return False, msg
            drone = next((d for d in self.state.ship.fleet_drones if d.id == drone_id), None)
            if not drone:
                return False, f"Unknown fleet unit '{drone_id}'."
            cost = 300
            if self.state.ship.credits < cost:
                return False, f"Insufficient credits: {cost} cr required for refit."
            updated = replace(
                drone,
                level=drone.level + 1,
                efficiency=min(1.75, drone.efficiency + 0.10),
                integrity=100,
            )
            drones = tuple(updated if d.id == drone_id else d for d in self.state.ship.fleet_drones)
            new_ship = self._clone_ship(credits=self.state.ship.credits - cost, fleet_drones=drones)
            self.state = self._clone_state(ship=new_ship)
            return True, f"Refit {drone.name} to level {updated.level} (efficiency {updated.efficiency:.2f})."

    def form_alliance(self, captain_id: str) -> tuple[bool, str]:
        return self.interact_ai(captain_id, "ally")

    def tick(self, num_ticks: int = 1) -> dict[str, Any]:
        """Advance the simulation universe by num_ticks."""
        with self.lock:
            if num_ticks <= 0:
                return {
                    "ticks_advanced": 0,
                    "stardate": round(self.state.time.stardate, 2),
                    "date": self.state.time.current_date,
                    "tick": self.state.time.tick,
                    "time_scale": self.state.time.time_scale,
                    "is_paused": self.state.time.is_paused,
                }

            cur_time = self.state.time
            new_tick = cur_time.tick + num_ticks
            new_days = cur_time.elapsed_days + num_ticks * 0.25
            new_stardate = 3042.0 + (new_days / 365.25)
            new_time = TimeState(
                tick=new_tick,
                stardate=new_stardate,
                speed=cur_time.speed,
                is_paused=cur_time.is_paused,
                time_scale=cur_time.time_scale,
                elapsed_days=new_days,
            )

            # 1. Orbital revolution: advance current_angle for every body in every star system
            updated_systems = {}
            for sys_id, system in self.state.systems.items():
                updated_bodies = []
                for body in system.bodies:
                    d_angle = body.orbit_speed * 0.05 * num_ticks
                    updated_bodies.append(
                        replace(body, current_angle=(body.current_angle + d_angle) % (2.0 * math.pi))
                    )
                updated_systems[sys_id] = StarSystem(
                    id=system.id,
                    name=system.name,
                    seed=system.seed,
                    x=system.x,
                    y=system.y,
                    spectral_type=system.spectral_type,
                    color=system.color,
                    security=system.security,
                    faction=system.faction,
                    bodies=tuple(updated_bodies),
                    connections=system.connections,
                    dominant_corp=system.dominant_corp,
                )

            # 2. Autonomous fleet drone harvesting over time
            cur_ship = self.state.ship
            new_drones = cur_ship.fleet_drones
            drone_cycles = max(1, num_ticks // 4) if num_ticks >= 4 else (1 if new_tick % 4 == 0 else 0)
            drone_cargo_harvested = 0
            drone_credits_harvested = 0
            if drone_cycles > 0 and cur_ship.fleet_drones:
                cargo_before = sum(d.cargo_accumulated for d in cur_ship.fleet_drones)
                credits_before = sum(d.credits_accumulated for d in cur_ship.fleet_drones)
                for _ in range(min(drone_cycles, 10)):
                    new_drones = self._process_drone_cycle(
                        self._clone_ship(fleet_drones=new_drones)
                    )
                drone_cargo_harvested = sum(d.cargo_accumulated for d in new_drones) - cargo_before
                drone_credits_harvested = sum(d.credits_accumulated for d in new_drones) - credits_before

            # 3. Passive shield capacitor regeneration
            equipment = calculate_equipment_bonuses(cur_ship)
            new_shield = cur_ship.shield
            shield_recharged = 0
            if not self.state.active_combat and cur_ship.shield < cur_ship.max_shield:
                shield_gain = int(max(1, (cur_ship.power.shields / 25.0) * num_ticks))
                shield_gain += int(equipment["shield_regen"] * num_ticks)
                new_shield = min(cur_ship.max_shield, cur_ship.shield + shield_gain)
                shield_recharged = new_shield - cur_ship.shield

            # 4. Combat ability cooldown decay
            new_combat = self.state.active_combat
            if new_combat and new_combat.ability_cooldown > 0:
                new_cooldown = max(0, new_combat.ability_cooldown - num_ticks)
                new_combat = replace(new_combat, ability_cooldown=new_cooldown)

            # 5. Advance global economy simulation and autonomous AI trade flows
            new_econ, econ_logs = tick_global_economy(self.state.economy, num_ticks, self.state.systems, self.rng)
            new_ai_captains, new_econ, ai_logs = simulate_ai_trade(
                self.state.ai_captains, new_econ, self.state.systems, self.rng
            )
            econ_logs.extend(ai_logs[-5:])

            # 6. Automated repair bay module passive hull healing
            new_hull = cur_ship.hull
            repair_per_tick = equipment["hull_repair_per_tick"]
            if repair_per_tick > 0:
                new_hull = min(cur_ship.max_hull, new_hull + int(repair_per_tick * num_ticks))

            new_flight_log = list(cur_ship.flight_log)
            if econ_logs:
                new_flight_log.extend(econ_logs)

            # 7. In-system transit progression and arrival
            new_orbiting_body_id = cur_ship.orbiting_body_id
            new_landed_body_id = cur_ship.landed_body_id
            new_travel = cur_ship.travel
            new_events = list(self.state.events)
            if cur_ship.travel is not None and new_tick >= cur_ship.travel.arrival_tick:
                new_orbiting_body_id = cur_ship.travel.destination_body_id
                new_landed_body_id = None
                new_travel = None
                cur_sys_obj = updated_systems.get(cur_ship.current_system_id, self.current_system)
                dest_name = new_orbiting_body_id
                for b in cur_sys_obj.bodies:
                    if b.id == new_orbiting_body_id:
                        dest_name = b.name
                        break
                arr_msg = f"Orbital capture achieved around {dest_name} after {cur_ship.travel.mode} transit."
                new_flight_log.append(arr_msg)
                evt_id = f"evt_{new_tick}_{len(new_events) + 1}"
                new_events.append(
                    GameEvent(
                        id=evt_id,
                        kind="arrival",
                        title=f"Orbital Capture: {dest_name}",
                        message=arr_msg,
                        tick=new_tick,
                        dismissed=False,
                    )
                )

            new_ship = self._clone_ship(
                hull=new_hull,
                shield=new_shield,
                orbiting_body_id=new_orbiting_body_id,
                landed_body_id=new_landed_body_id,
                travel=new_travel,
                fleet_drones=new_drones,
                flight_log=tuple(new_flight_log[-20:]),
            )

            self.state = self._clone_state(
                ship=new_ship,
                systems=updated_systems,
                active_combat=new_combat,
                time=new_time,
                economy=new_econ,
                ai_captains=new_ai_captains,
                events=tuple(new_events[-50:]),
            )

            return {
                "ticks_advanced": num_ticks,
                "stardate": round(new_stardate, 2),
                "date": new_time.current_date,
                "tick": new_tick,
                "elapsed_days": round(new_days, 2),
                "shield_recharged": shield_recharged,
                "drone_cargo_harvested": drone_cargo_harvested,
                "drone_credits_harvested": drone_credits_harvested,
                "time_scale": new_time.time_scale,
                "is_paused": new_time.is_paused,
            }

    def emit_event(self, kind: str, title: str, message: str) -> GameEvent:
        """Create and append a cockpit popup GameEvent."""
        with self.lock:
            cur_tick = self.state.time.tick
            evt = GameEvent(
                id=f"evt_{cur_tick}_{len(self.state.events) + 1}",
                kind=str(kind),
                title=str(title),
                message=str(message),
                tick=cur_tick,
                dismissed=False,
            )
            updated = list(self.state.events) + [evt]
            self.state = self._clone_state(events=tuple(updated[-50:]))
            return evt

    def dismiss_event(self, event_id: str) -> tuple[bool, str]:
        """Mark a cockpit popup GameEvent as dismissed."""
        with self.lock:
            target = str(event_id).strip()
            updated: list[GameEvent] = []
            found = False
            for evt in self.state.events:
                if evt.id == target:
                    updated.append(replace(evt, dismissed=True))
                    found = True
                else:
                    updated.append(evt)
            if not found:
                return False, f"Event '{target}' not found."
            self.state = self._clone_state(events=tuple(updated))
            return True, f"Event '{target}' dismissed."

    def pause_time(self) -> tuple[bool, str]:
        """Pause simulation temporal clock while preserving current playback rate."""
        with self.lock:
            cur = self.state.time
            saved_speed = cur.speed if cur.speed > 0.0 else 1.0
            new_time = TimeState(
                tick=cur.tick,
                stardate=cur.stardate,
                speed=saved_speed,
                is_paused=True,
                time_scale="PAUSED",
                elapsed_days=cur.elapsed_days,
            )
            self.state = self._clone_state(time=new_time)
            return True, "Simulation clock paused."

    def resume_time(self) -> tuple[bool, str]:
        """Resume simulation temporal clock restoring previous speed multiplier."""
        with self.lock:
            cur = self.state.time
            resumed_speed = cur.speed if cur.speed > 0.0 else 1.0
            scale_str = f"{int(resumed_speed)}x" if resumed_speed.is_integer() else f"{resumed_speed}x"
            new_time = TimeState(
                tick=cur.tick,
                stardate=cur.stardate,
                speed=resumed_speed,
                is_paused=False,
                time_scale=scale_str,
                elapsed_days=cur.elapsed_days,
            )
            self.state = self._clone_state(time=new_time)
            return True, f"Simulation clock resumed at {scale_str} speed."

    def set_time_speed(self, speed: float) -> tuple[bool, str]:
        """Set simulation speed multiplier (0.0x to 10.0x)."""
        with self.lock:
            cur = self.state.time
            clamped = max(0.0, min(10.0, float(speed)))
            is_paused = (clamped == 0.0)
            time_scale = "PAUSED" if is_paused else (f"{int(clamped)}x" if clamped.is_integer() else f"{clamped}x")
            new_time = TimeState(
                tick=cur.tick,
                stardate=cur.stardate,
                speed=clamped if not is_paused else (cur.speed if cur.speed > 0.0 else 1.0),
                is_paused=is_paused,
                time_scale=time_scale,
                elapsed_days=cur.elapsed_days,
            )
            self.state = self._clone_state(time=new_time)
            return True, f"Simulation clock speed set to {time_scale}."

    def step_time(self, num_ticks: int = 1) -> tuple[bool, str, dict[str, Any]]:
        """Advance simulation by a discrete number of ticks."""
        summary = self.tick(max(1, int(num_ticks)))
        return True, f"Advanced {summary['ticks_advanced']} tick(s). Date: {summary['date']} (Tick #{summary['tick']}).", summary

