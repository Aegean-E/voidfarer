"""Deterministic state machine and simulation engine for VoidFarer."""

from __future__ import annotations

import math
import random
import threading
from typing import Any

from voidfarer.galaxy import (
    COMMODITY_MAP,
    GalaxyGenerator,
)
from voidfarer.models import (
    BountyContract,
    CelestialBody,
    CombatEncounter,
    FleetDrone,
    GameState,
    MarketQuote,
    PilotMastery,
    PrecursorRelic,
    ShipPower,
    ShipState,
    ShipUpgrade,
    StarSystem,
)
from voidfarer.retention import (
    CATALOG_RELICS,
    PILOT_TALENTS,
    calculate_passive_multipliers,
    generate_contract,
    generate_initial_contracts,
    roll_relic_drop,
)
from voidfarer.upgrades import (
    CATALOG_DRONE_TEMPLATES,
    CATALOG_UPGRADES,
    UPGRADE_MAP,
    get_available_upgrades,
    get_upgrade,
)


class SimulationEngine:
    """Coordinates space flight, star navigation, fleet drones, upgrades, and tactical combat."""

    def __init__(self, seed: int = 42, state: GameState | None = None) -> None:
        self.lock = threading.Lock()
        self.seed = seed
        self.rng = random.Random(seed)

        if state is not None:
            self.state = state
        else:
            self.state = self._create_initial_state(seed)

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
        )

    def _award_pilot_xp(self, amount: int, current_mastery: PilotMastery) -> tuple[PilotMastery, list[str]]:
        """Award experience points and compute level promotions and talent points."""
        new_xp = current_mastery.xp + amount
        level = current_mastery.level
        next_xp = current_mastery.next_level_xp
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
        )

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
            if d.drone_type == "mining":
                new_cargo = d.cargo_accumulated + 2
                updated_drones.append(
                    FleetDrone(
                        id=d.id,
                        name=d.name,
                        drone_type=d.drone_type,
                        assigned_system_id=d.assigned_system_id,
                        status="harvesting",
                        cargo_accumulated=new_cargo,
                        credits_accumulated=d.credits_accumulated,
                    )
                )
            elif d.drone_type == "scout":
                new_credits = d.credits_accumulated + 75
                updated_drones.append(
                    FleetDrone(
                        id=d.id,
                        name=d.name,
                        drone_type=d.drone_type,
                        assigned_system_id=d.assigned_system_id,
                        status="patrolling",
                        cargo_accumulated=d.cargo_accumulated,
                        credits_accumulated=new_credits,
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
            eng_pwr = self.state.ship.power.engines
            base_fuel = 8
            if eng_pwr >= 40:
                fuel_cost = max(3, base_fuel - 3)
            elif eng_pwr < 20:
                fuel_cost = base_fuel + 4
            else:
                fuel_cost = base_fuel

            if "warp_booster_mk2" in self.state.ship.equipped_upgrades.values():
                fuel_cost = max(2, int(fuel_cost * 0.65))

            fuel_cost = max(1, int(fuel_cost * passives["fuel_efficiency"]))

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

            # Check low security ambush
            has_escort = any(d.drone_type == "combat_escort" for d in self.state.ship.fleet_drones)
            if target_sys.security < 0.35:
                if has_escort:
                    new_log.append("TACTICAL: Combat escort frigate dispersed hostile ambush.")
                elif self.rng.random() < 0.40:
                    combat = CombatEncounter(
                        id=f"combat_{target_system_id}_{self.rng.randint(100, 999)}",
                        enemy_name=f"{target_sys.faction} Corsair",
                        enemy_class="Pirate Raider",
                        enemy_hull=80,
                        enemy_max_hull=80,
                        enemy_damage=18,
                        bounty_credits=650,
                        salvage_commodity="titanium",
                    )
                    new_log.append(f"ALERT: Intercepted by hostile {combat.enemy_name}! Weapons locked.")

            if not combat and self.rng.random() < 0.35:
                anomaly = GalaxyGenerator.get_random_anomaly(self.rng.randint(1, 99999))
                new_log.append(f"WARNING: Deep-space anomaly detected! [{anomaly.title}]")

            new_ship = self._clone_ship(
                fuel=new_fuel,
                current_system_id=target_system_id,
                orbiting_body_id=target_sys.bodies[0].id if target_sys.bodies else None,
                fleet_drones=updated_drones,
                flight_log=tuple(new_log[-20:]),
                streak=new_streak,
                mastery=new_mastery,
                active_contracts=updated_contracts,
                tactical_combo=0,
            )

            stats = dict(self.state.stats)
            stats["jumps"] += 1

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=tuple(sorted(visited)),
                active_anomaly=anomaly,
                active_combat=combat,
                stats=stats,
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

            new_ship = self._clone_ship(
                orbiting_body_id=body_id,
                flight_log=tuple(new_log),
            )

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
                active_combat=self.state.active_combat,
                stats=self.state.stats,
            )

            return True, f"Now in orbit around {matched.name}."

    def scan(self) -> tuple[bool, str, dict[str, Any]]:
        """Perform sensor sweep of current body or local space."""
        with self.lock:
            body = self.orbiting_body
            if not body:
                return False, "Cannot scan: ship must establish orbit around a celestial body first.", {}

            passives = calculate_passive_multipliers(self.state.ship)
            pwr = self.state.ship.power.sensors
            credit_bounty = int(100 * (pwr / 25.0))
            if "deep_core_scanner" in self.state.ship.equipped_upgrades.values():
                credit_bounty = int(credit_bounty * 1.5)
            credit_bounty = int(credit_bounty * passives["scan_bounty"])

            # Mark scan completed on body
            updated_bodies = []
            for b in self.current_system.bodies:
                if b.id == body.id:
                    scanned = CelestialBody(
                        id=b.id,
                        name=b.name,
                        body_type=b.body_type,
                        orbit_radius=b.orbit_radius,
                        orbit_speed=b.orbit_speed,
                        current_angle=b.current_angle,
                        radius_km=b.radius_km,
                        color=b.color,
                        hazards=b.hazards,
                        station_dockable=b.station_dockable,
                        market_archetype=b.market_archetype,
                        scan_completed=True,
                        scan_discovery=b.scan_discovery,
                    )
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
            )

            systems = dict(self.state.systems)
            systems[cur_sys.id] = new_sys

            # Award credit bounty
            new_credits = self.state.ship.credits + credit_bounty

            # Variable Ratio relic drop and near-miss feedback
            relic_bonus = passives["relic_find"] + self.state.ship.near_miss_scanner_bonus
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
            new_mastery, xp_logs = self._award_pilot_xp(50, self.state.ship.mastery)
            new_log.extend(xp_logs)

            new_ship = self._clone_ship(
                credits=new_credits,
                relics=tuple(new_relics),
                near_miss_scanner_bonus=new_near_miss,
                mastery=new_mastery,
                active_contracts=updated_contracts,
                flight_log=tuple(new_log[-20:]),
            )

            stats = dict(self.state.stats)
            stats["scans"] += 1
            stats["credits_earned"] += credit_bounty

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
                active_combat=self.state.active_combat,
                stats=stats,
            )

            discovery_info = {
                "body_name": body.name,
                "body_type": body.body_type,
                "discovery": body.scan_discovery,
                "bounty": credit_bounty,
                "market_archetype": body.market_archetype,
                "hazards": list(body.hazards),
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

            new_ship = self._clone_ship(
                power=new_power,
                flight_log=tuple(new_log),
            )

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
                active_combat=self.state.active_combat,
                stats=self.state.stats,
            )

            return True, "Reactor power routed successfully."

    def trade(self, commodity_id: str, quantity: int, is_buy: bool) -> tuple[bool, str]:
        """Execute buy or sell commodity order at orbiting market."""
        with self.lock:
            body = self.orbiting_body
            if not body or not body.station_dockable:
                return False, "Docking authorization required: ship must orbit a station or habitable colony to trade."

            if quantity <= 0:
                return False, "Quantity must be greater than zero."

            quotes = GalaxyGenerator.get_market_quotes(self.current_system, body)
            quote = next((q for q in quotes if q.commodity_id == commodity_id), None)
            if not quote:
                return False, f"Commodity '{commodity_id}' not traded here."

            comm = COMMODITY_MAP.get(commodity_id)
            vol_per_unit = comm.volume if comm else 1

            cargo = dict(self.state.ship.cargo)
            stats = dict(self.state.stats)

            passives = calculate_passive_multipliers(self.state.ship)

            if is_buy:
                total_cost = quote.buy_price * quantity
                if self.state.ship.credits < total_cost:
                    return False, f"Insufficient credits: {total_cost} cr required, {self.state.ship.credits} cr available."

                current_cargo_units = sum(cargo.values())
                needed_space = quantity * vol_per_unit
                if current_cargo_units + needed_space > self.state.ship.cargo_capacity:
                    return False, f"Cargo hold capacity exceeded: cannot load {needed_space} units."

                new_credits = self.state.ship.credits - total_cost
                cargo[commodity_id] = cargo.get(commodity_id, 0) + quantity
                msg = f"Purchased {quantity}x {quote.name} for {total_cost} cr."
            else:
                owned = cargo.get(commodity_id, 0)
                if owned < quantity:
                    return False, f"Insufficient inventory: you have {owned} units, tried to sell {quantity}."

                margin_mult = passives.get("trade_margin", 1.0)
                revenue = int(quote.sell_price * quantity * margin_mult)
                new_credits = self.state.ship.credits + revenue
                cargo[commodity_id] = owned - quantity
                if cargo[commodity_id] == 0:
                    del cargo[commodity_id]
                stats["credits_earned"] += revenue
                msg = f"Sold {quantity}x {quote.name} for {revenue} cr (trade margin: x{margin_mult:.2f})."

            stats["trades"] += 1
            log_entry = f"Market transaction: {msg}"
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            # Progress trade contracts and award merchant pilot XP
            updated_contracts, contract_logs = self._progress_contracts("trade", 1)
            new_log.extend(contract_logs)
            new_mastery, xp_logs = self._award_pilot_xp(25, self.state.ship.mastery)
            new_log.extend(xp_logs)

            new_ship = self._clone_ship(
                credits=new_credits,
                cargo=cargo,
                mastery=new_mastery,
                active_contracts=updated_contracts,
                flight_log=tuple(new_log[-20:]),
            )

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
                active_combat=self.state.active_combat,
                stats=stats,
            )

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
                if self.state.ship.equipped_upgrades[upgrade.slot] == upgrade_id:
                    return False, f"Module '{upgrade.name}' is already installed."

            if self.state.ship.credits < upgrade.cost:
                return False, f"Insufficient credits: costs {upgrade.cost} cr, you have {self.state.ship.credits} cr."

            new_credits = self.state.ship.credits - upgrade.cost
            equipped = dict(self.state.ship.equipped_upgrades)
            equipped[upgrade.slot] = upgrade_id

            upg_list = list(self.state.ship.upgrades)
            if upgrade.name not in upg_list:
                upg_list.append(upgrade.name)

            # Apply stat bonuses
            new_capacity = self.state.ship.cargo_capacity
            new_max_shield = self.state.ship.max_shield
            new_shield = self.state.ship.shield

            if "cargo_capacity" in upgrade.stat_bonus:
                new_capacity += int(upgrade.stat_bonus["cargo_capacity"])
            if "max_shield" in upgrade.stat_bonus:
                new_max_shield += int(upgrade.stat_bonus["max_shield"])
                new_shield = new_max_shield

            log_entry = f"Arsenal upgrade: Installed {upgrade.name} ({upgrade.slot.upper()}) for {upgrade.cost} cr."
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            new_ship = self._clone_ship(
                shield=new_shield,
                max_shield=new_max_shield,
                credits=new_credits,
                cargo_capacity=new_capacity,
                upgrades=tuple(upg_list),
                equipped_upgrades=equipped,
                flight_log=tuple(new_log),
            )

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
                active_combat=self.state.active_combat,
                stats=self.state.stats,
            )

            return True, f"Successfully installed {upgrade.name} in {upgrade.slot} slot."

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

            new_ship = self._clone_ship(
                credits=new_credits,
                fleet_drones=tuple(drones),
                flight_log=tuple(new_log),
            )

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
                active_combat=self.state.active_combat,
                stats=self.state.stats,
            )

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
                        FleetDrone(
                            id=d.id,
                            name=d.name,
                            drone_type=d.drone_type,
                            assigned_system_id=target_system_id,
                            status="harvesting" if d.drone_type == "mining" else "patrolling",
                            cargo_accumulated=d.cargo_accumulated,
                            credits_accumulated=d.credits_accumulated,
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

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
                active_combat=self.state.active_combat,
                stats=self.state.stats,
            )

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
                        FleetDrone(
                            id=d.id,
                            name=d.name,
                            drone_type=d.drone_type,
                            assigned_system_id=d.assigned_system_id,
                            status=d.status,
                            cargo_accumulated=0,
                            credits_accumulated=0,
                        )
                    )
                else:
                    updated_drones.append(d)

            if total_cargo == 0 and total_credits == 0:
                return False, "No yield accumulated by fleet drones yet.", {"credits": 0, "cargo": 0}

            passives = calculate_passive_multipliers(self.state.ship)
            total_cargo = int(total_cargo * passives.get("drone_yield", 1.0))
            total_credits = int(total_credits * passives.get("drone_yield", 1.0))

            cargo = dict(self.state.ship.cargo)
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

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
                active_combat=self.state.active_combat,
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

            if action == "fire_lasers":
                # Calculate player strike damage with upgrades, relics, and pilot talents
                wep_power = self.state.ship.power.weapons
                bonus_wep = 15 if "pulse_cannon_array" in self.state.ship.equipped_upgrades.values() else 0
                base_dmg = int((20 + int(wep_power * 0.75) + bonus_wep) * passives.get("laser_dmg", 1.0))

                # Tactical Combo Overcharge loop (Flow & rhythmic attention)
                new_combo = self.state.ship.tactical_combo + 1
                crit_text = ""
                if new_combo >= 3:
                    base_dmg = int(base_dmg * 1.5)
                    crit_text = f" (TACTICAL OVERCHARGE x{new_combo}: +50% CRIT DAMAGE!)"

                enemy_remaining = combat.enemy_hull - base_dmg

                if enemy_remaining <= 0:
                    # Enemy destroyed
                    new_credits += combat.bounty_credits
                    cargo[combat.salvage_commodity] = cargo.get(combat.salvage_commodity, 0) + 2
                    stats["combat_victories"] += 1
                    stats["credits_earned"] += combat.bounty_credits

                    # Variable Ratio salvage drop from hostile wreckage
                    salvage_relic, _ = roll_relic_drop(self.rng, bonus_prob=0.20, current_system=self.current_system.name)
                    new_relics = list(self.state.ship.relics)
                    relic_note = ""
                    if salvage_relic:
                        new_relics.append(salvage_relic)
                        relic_note = f" Salvaged Precursor relic: [{salvage_relic.name}] ({salvage_relic.rarity.upper()})!"

                    # Progress combat contracts and award pilot combat XP
                    updated_contracts, contract_logs = self._progress_contracts("combat", 1)
                    new_mastery, xp_logs = self._award_pilot_xp(200, self.state.ship.mastery)

                    msg = (
                        f"VICTORY: {combat.enemy_name} neutralized! "
                        f"Collected {combat.bounty_credits} cr bounty, salvaged 2x {combat.salvage_commodity}.{relic_note}"
                    )
                    log_entry = f"Combat outcome: {msg}"
                    new_log = list(self.state.ship.flight_log[-19:]) + [log_entry] + contract_logs + xp_logs

                    new_ship = self._clone_ship(
                        hull=new_hull,
                        shield=new_shield,
                        credits=new_credits,
                        cargo=cargo,
                        relics=tuple(new_relics),
                        mastery=new_mastery,
                        active_contracts=updated_contracts,
                        tactical_combo=0,
                        flight_log=tuple(new_log[-20:]),
                    )

                    self.state = GameState(
                        version=self.state.version,
                        galaxy_seed=self.state.galaxy_seed,
                        ship=new_ship,
                        systems=self.state.systems,
                        visited_systems=self.state.visited_systems,
                        active_anomaly=self.state.active_anomaly,
                        active_combat=None,
                        stats=stats,
                    )
                    return True, msg

                # Enemy counter-attack
                inbound = combat.enemy_damage
                new_streak = self.state.ship.streak
                if new_shield >= inbound:
                    new_shield -= inbound
                else:
                    overflow = inbound - new_shield
                    new_shield = 0
                    new_hull = max(0, new_hull - overflow)
                    new_combo = 0  # Combo disrupted on hull breach
                    if new_hull < 50:
                        new_streak = max(1, self.state.ship.streak - 1)

                msg = f"Laser strike dealt {base_dmg} damage{crit_text} (Enemy HP: {enemy_remaining}/{combat.enemy_max_hull}). Inbound counter-battery dealt {inbound} damage."
                new_combat = CombatEncounter(
                    id=combat.id,
                    enemy_name=combat.enemy_name,
                    enemy_class=combat.enemy_class,
                    enemy_hull=enemy_remaining,
                    enemy_max_hull=combat.enemy_max_hull,
                    enemy_damage=combat.enemy_damage,
                    bounty_credits=combat.bounty_credits,
                    salvage_commodity=combat.salvage_commodity,
                )

            elif action == "shield_absorb":
                # Emergency shield boost with Dreadnought mastery talent bonus
                boost = 30 + (25 if "dreadnought_tactics" in self.state.ship.mastery.specializations else 0)
                new_shield = min(self.state.ship.max_shield, new_shield + boost)
                mitigated = max(1, int(combat.enemy_damage * 0.35))
                if new_shield >= mitigated:
                    new_shield -= mitigated
                else:
                    new_hull = max(0, new_hull - (mitigated - new_shield))
                    new_shield = 0
                msg = f"Shield capacitors overcharged (+{boost} MW). Enemy barrage deflected, taking only {mitigated} damage."
                new_combat = combat
                new_combo = self.state.ship.tactical_combo
                new_streak = self.state.ship.streak

            elif action == "evasive_burn":
                # Thruster evasion
                eng = self.state.ship.power.engines
                chance = 0.50 + (eng / 25.0) * 0.20
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
                new_combo = self.state.ship.tactical_combo
                new_streak = self.state.ship.streak

            elif action == "flee":
                if self.state.ship.fuel < 8:
                    return False, "Insufficient fuel for emergency jump (8 units required)."
                new_fuel = self.state.ship.fuel - 8
                msg = "Emergency hyperspace micro-jump executed. Safely disengaged from hostile sector (expedition streak reset)."
                new_ship = self._clone_ship(
                    hull=new_hull,
                    shield=new_shield,
                    fuel=new_fuel,
                    streak=1,
                    tactical_combo=0,
                    flight_log=tuple(list(self.state.ship.flight_log[-19:]) + [msg]),
                )
                self.state = GameState(
                    version=self.state.version,
                    galaxy_seed=self.state.galaxy_seed,
                    ship=new_ship,
                    systems=self.state.systems,
                    visited_systems=self.state.visited_systems,
                    active_anomaly=self.state.active_anomaly,
                    active_combat=None,
                    stats=self.state.stats,
                )
                return True, msg
            else:
                return False, f"Unknown combat action '{action}'."

            new_log = list(self.state.ship.flight_log[-19:]) + [msg]
            new_ship = self._clone_ship(
                hull=new_hull,
                shield=new_shield,
                tactical_combo=new_combo,
                streak=new_streak,
                flight_log=tuple(new_log[-20:]),
            )

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
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

                    self.state = GameState(
                        version=self.state.version,
                        galaxy_seed=self.state.galaxy_seed,
                        ship=new_ship,
                        systems=self.state.systems,
                        visited_systems=self.state.visited_systems,
                        active_anomaly=None,
                        active_combat=self.state.active_combat,
                        stats=self.state.stats,
                    )

                    return False, log_entry

            # Success outcome
            new_hull = min(self.state.ship.max_hull, max(0, self.state.ship.hull + choice.hull_delta))
            new_credits = max(0, self.state.ship.credits + choice.credits_delta)
            new_fuel = min(self.state.ship.max_fuel, max(0, self.state.ship.fuel + choice.fuel_delta))

            cargo = dict(self.state.ship.cargo)
            for item_k, item_v in choice.cargo_reward.items():
                cargo[item_k] = cargo.get(item_k, 0) + item_v

            log_entry = f"Anomaly resolved: {choice.outcome_text}"
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

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=None,
                active_combat=self.state.active_combat,
                stats=stats,
            )

            return True, choice.outcome_text

    def repair_hull(self, amount: int = 25) -> tuple[bool, str]:
        """Repair ship hull integrity at orbital station."""
        with self.lock:
            body = self.orbiting_body
            if not body or not body.station_dockable:
                return False, "Repair drydocks available at orbital stations or colonies only."

            needed = self.state.ship.max_hull - self.state.ship.hull
            if needed <= 0:
                return False, "Hull integrity already at 100% capacity."

            actual = min(amount, needed)
            cost = actual * 4
            if self.state.ship.credits < cost:
                return False, f"Insufficient credits: repair costs {cost} cr ({actual} HP)."

            new_ship = self._clone_ship(
                hull=self.state.ship.hull + actual,
                credits=self.state.ship.credits - cost,
                flight_log=tuple(list(self.state.ship.flight_log[-19:]) + [f"Drydock repair: +{actual} HP for {cost} cr."]),
            )

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
                active_combat=self.state.active_combat,
                stats=self.state.stats,
            )

            return True, f"Repairs completed: +{actual} HP restored for {cost} cr."

    def refuel(self, amount: int = 20) -> tuple[bool, str]:
        """Refuel quantum drive at orbital station."""
        with self.lock:
            body = self.orbiting_body
            if not body or not body.station_dockable:
                return False, "Fuel refinery available at orbital stations or colonies only."

            needed = self.state.ship.max_fuel - self.state.ship.fuel
            if needed <= 0:
                return False, "Fuel reserves already at maximum capacity."

            actual = min(amount, needed)
            cost = actual * 6
            if self.state.ship.credits < cost:
                return False, f"Insufficient credits: refueling costs {cost} cr ({actual} fuel)."

            new_ship = self._clone_ship(
                fuel=self.state.ship.fuel + actual,
                credits=self.state.ship.credits - cost,
                flight_log=tuple(list(self.state.ship.flight_log[-19:]) + [f"Refueled +{actual} quantum fuel for {cost} cr."]),
            )

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
                active_combat=self.state.active_combat,
                stats=self.state.stats,
            )

            return True, f"Fuel tanks replenished: +{actual} units for {cost} cr."

    def step_orbits(self, delta_time: float = 1.0) -> None:
        """Advance celestial bodies along orbital mechanics paths and cycle fleet drones."""
        with self.lock:
            updated_systems: dict[str, StarSystem] = {}
            for sys_id, sys_obj in self.state.systems.items():
                updated_bodies = []
                for b in sys_obj.bodies:
                    new_angle = (b.current_angle + b.orbit_speed * delta_time) % (2 * math.pi)
                    updated_bodies.append(
                        CelestialBody(
                            id=b.id,
                            name=b.name,
                            body_type=b.body_type,
                            orbit_radius=b.orbit_radius,
                            orbit_speed=b.orbit_speed,
                            current_angle=new_angle,
                            radius_km=b.radius_km,
                            color=b.color,
                            hazards=b.hazards,
                            station_dockable=b.station_dockable,
                            market_archetype=b.market_archetype,
                            scan_completed=b.scan_completed,
                            scan_discovery=b.scan_discovery,
                        )
                    )
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
                )

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=self.state.ship,
                systems=updated_systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
                active_combat=self.state.active_combat,
                stats=self.state.stats,
            )

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

            new_ship = self._clone_ship(
                credits=new_credits,
                mastery=new_mastery,
                relics=tuple(new_relics),
                active_contracts=updated_contracts,
                flight_log=tuple(new_log[-20:]),
            )

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
                active_combat=self.state.active_combat,
                stats=stats,
            )

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

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
                active_combat=self.state.active_combat,
                stats=self.state.stats,
            )

            return True, f"Specialization unlocked: {talent['name']}."

    def get_status_snapshot(self) -> dict[str, Any]:
        """Produce a comprehensive JSON serializable telemetry snapshot for the HUD."""
        with self.lock:
            cur_sys = self.current_system
            orb_body = self.orbiting_body
            market_quotes = []
            if orb_body and orb_body.station_dockable:
                quotes = GalaxyGenerator.get_market_quotes(cur_sys, orb_body)
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
                "stats": dict(self.state.stats),
                "market_quotes": market_quotes,
                "catalog_upgrades": [u.to_dict() for u in CATALOG_UPGRADES],
                "catalog_drones": CATALOG_DRONE_TEMPLATES,
                "catalog_talents": PILOT_TALENTS,
                "catalog_relics": [r.to_dict() for r in CATALOG_RELICS],
            }
