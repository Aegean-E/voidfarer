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
    CelestialBody,
    GameState,
    MarketQuote,
    ShipPower,
    ShipState,
    StarSystem,
)


class SimulationEngine:
    """Coordinates space flight, star navigation, market economics, and anomalies."""

    def __init__(self, seed: int = 42, state: GameState | None = None) -> None:
        self.lock = threading.Lock()
        self.seed = seed
        self.rng = random.Random(seed)

        if state is not None:
            self.state = state
        else:
            self.state = self._create_initial_state(seed)

    def _create_initial_state(self, seed: int) -> GameState:
        """Construct a fresh universe state rooted at Sol System."""
        generator = GalaxyGenerator(seed=seed)
        systems = generator.generate_galaxy()

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
            flight_log=("Command initialization verified at Sol Starport.",),
        )

        return GameState(
            version=1,
            galaxy_seed=seed,
            ship=ship,
            systems=systems,
            visited_systems=("sol",),
            active_anomaly=None,
            stats={
                "jumps": 0,
                "scans": 0,
                "trades": 0,
                "anomalies_resolved": 0,
                "credits_earned": 0,
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

    def jump(self, target_system_id: str) -> tuple[bool, str]:
        """Execute a hyperspace jump to an adjacent star system."""
        with self.lock:
            if self.state.active_anomaly is not None:
                return False, "Hyperspace drive locked: unresolved spatial anomaly in proximity!"

            cur_sys = self.current_system
            if target_system_id not in cur_sys.connections:
                return False, f"System '{target_system_id}' is not linked via hyperlane corridor."

            target_sys = self.state.systems.get(target_system_id)
            if not target_sys:
                return False, f"Unknown system target '{target_system_id}'."

            # Calculate fuel cost
            eng_pwr = self.state.ship.power.engines
            base_fuel = 8
            if eng_pwr >= 40:
                fuel_cost = max(3, base_fuel - 3)
            elif eng_pwr < 20:
                fuel_cost = base_fuel + 4
            else:
                fuel_cost = base_fuel

            if self.state.ship.fuel < fuel_cost:
                return False, f"Insufficient Quantum Fuel: {fuel_cost} units required, {self.state.ship.fuel} available."

            # Execute jump
            new_fuel = self.state.ship.fuel - fuel_cost
            visited = set(self.state.visited_systems)
            visited.add(target_system_id)

            log_entry = f"Hyperspace jump completed to {target_sys.name} (fuel consumed: {fuel_cost})."
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            # 35% chance to encounter deep-space anomaly during jump
            anomaly = None
            if self.rng.random() < 0.35:
                anomaly = GalaxyGenerator.get_random_anomaly(self.rng.randint(1, 99999))
                new_log.append(f"WARNING: Deep-space anomaly detected! [{anomaly.title}]")

            new_ship = ShipState(
                commander_name=self.state.ship.commander_name,
                callsign=self.state.ship.callsign,
                ship_class=self.state.ship.ship_class,
                hull=self.state.ship.hull,
                max_hull=self.state.ship.max_hull,
                shield=self.state.ship.shield,
                max_shield=self.state.ship.max_shield,
                fuel=new_fuel,
                max_fuel=self.state.ship.max_fuel,
                credits=self.state.ship.credits,
                cargo=dict(self.state.ship.cargo),
                cargo_capacity=self.state.ship.cargo_capacity,
                current_system_id=target_system_id,
                orbiting_body_id=target_sys.bodies[0].id if target_sys.bodies else None,
                power=self.state.ship.power,
                upgrades=self.state.ship.upgrades,
                flight_log=tuple(new_log),
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
                stats=stats,
            )

            return True, f"Jump successful: arrived in {target_sys.name}."

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

            new_ship = ShipState(
                commander_name=self.state.ship.commander_name,
                callsign=self.state.ship.callsign,
                ship_class=self.state.ship.ship_class,
                hull=self.state.ship.hull,
                max_hull=self.state.ship.max_hull,
                shield=self.state.ship.shield,
                max_shield=self.state.ship.max_shield,
                fuel=self.state.ship.fuel,
                max_fuel=self.state.ship.max_fuel,
                credits=self.state.ship.credits,
                cargo=dict(self.state.ship.cargo),
                cargo_capacity=self.state.ship.cargo_capacity,
                current_system_id=self.state.ship.current_system_id,
                orbiting_body_id=body_id,
                power=self.state.ship.power,
                upgrades=self.state.ship.upgrades,
                flight_log=tuple(new_log),
            )

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
                stats=self.state.stats,
            )

            return True, f"Now in orbit around {matched.name}."

    def scan(self) -> tuple[bool, str, dict[str, Any]]:
        """Perform sensor sweep of current body or local space."""
        with self.lock:
            body = self.orbiting_body
            if not body:
                return False, "Cannot scan: ship must establish orbit around a celestial body first.", {}

            pwr = self.state.ship.power.sensors
            credit_bounty = int(100 * (pwr / 25.0))

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
            log_entry = f"Sensor scan completed for {body.name}: awarded {credit_bounty} cr scientific research bounty."
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            new_ship = ShipState(
                commander_name=self.state.ship.commander_name,
                callsign=self.state.ship.callsign,
                ship_class=self.state.ship.ship_class,
                hull=self.state.ship.hull,
                max_hull=self.state.ship.max_hull,
                shield=self.state.ship.shield,
                max_shield=self.state.ship.max_shield,
                fuel=self.state.ship.fuel,
                max_fuel=self.state.ship.max_fuel,
                credits=new_credits,
                cargo=dict(self.state.ship.cargo),
                cargo_capacity=self.state.ship.cargo_capacity,
                current_system_id=self.state.ship.current_system_id,
                orbiting_body_id=self.state.ship.orbiting_body_id,
                power=self.state.ship.power,
                upgrades=self.state.ship.upgrades,
                flight_log=tuple(new_log),
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

            new_ship = ShipState(
                commander_name=self.state.ship.commander_name,
                callsign=self.state.ship.callsign,
                ship_class=self.state.ship.ship_class,
                hull=self.state.ship.hull,
                max_hull=self.state.ship.max_hull,
                shield=self.state.ship.shield,
                max_shield=self.state.ship.max_shield,
                fuel=self.state.ship.fuel,
                max_fuel=self.state.ship.max_fuel,
                credits=self.state.ship.credits,
                cargo=dict(self.state.ship.cargo),
                cargo_capacity=self.state.ship.cargo_capacity,
                current_system_id=self.state.ship.current_system_id,
                orbiting_body_id=self.state.ship.orbiting_body_id,
                power=new_power,
                upgrades=self.state.ship.upgrades,
                flight_log=tuple(new_log),
            )

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
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

                revenue = quote.sell_price * quantity
                new_credits = self.state.ship.credits + revenue
                cargo[commodity_id] = owned - quantity
                if cargo[commodity_id] == 0:
                    del cargo[commodity_id]
                stats["credits_earned"] += revenue
                msg = f"Sold {quantity}x {quote.name} for {revenue} cr."

            stats["trades"] += 1
            log_entry = f"Market transaction: {msg}"
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            new_ship = ShipState(
                commander_name=self.state.ship.commander_name,
                callsign=self.state.ship.callsign,
                ship_class=self.state.ship.ship_class,
                hull=self.state.ship.hull,
                max_hull=self.state.ship.max_hull,
                shield=self.state.ship.shield,
                max_shield=self.state.ship.max_shield,
                fuel=self.state.ship.fuel,
                max_fuel=self.state.ship.max_fuel,
                credits=new_credits,
                cargo=cargo,
                cargo_capacity=self.state.ship.cargo_capacity,
                current_system_id=self.state.ship.current_system_id,
                orbiting_body_id=self.state.ship.orbiting_body_id,
                power=self.state.ship.power,
                upgrades=self.state.ship.upgrades,
                flight_log=tuple(new_log),
            )

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
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

                    new_ship = ShipState(
                        commander_name=self.state.ship.commander_name,
                        callsign=self.state.ship.callsign,
                        ship_class=self.state.ship.ship_class,
                        hull=new_hull,
                        max_hull=self.state.ship.max_hull,
                        shield=self.state.ship.shield,
                        max_shield=self.state.ship.max_shield,
                        fuel=self.state.ship.fuel,
                        max_fuel=self.state.ship.max_fuel,
                        credits=self.state.ship.credits,
                        cargo=dict(self.state.ship.cargo),
                        cargo_capacity=self.state.ship.cargo_capacity,
                        current_system_id=self.state.ship.current_system_id,
                        orbiting_body_id=self.state.ship.orbiting_body_id,
                        power=self.state.ship.power,
                        upgrades=self.state.ship.upgrades,
                        flight_log=tuple(new_log),
                    )

                    self.state = GameState(
                        version=self.state.version,
                        galaxy_seed=self.state.galaxy_seed,
                        ship=new_ship,
                        systems=self.state.systems,
                        visited_systems=self.state.visited_systems,
                        active_anomaly=None,
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

            new_ship = ShipState(
                commander_name=self.state.ship.commander_name,
                callsign=self.state.ship.callsign,
                ship_class=self.state.ship.ship_class,
                hull=new_hull,
                max_hull=self.state.ship.max_hull,
                shield=self.state.ship.shield,
                max_shield=self.state.ship.max_shield,
                fuel=new_fuel,
                max_fuel=self.state.ship.max_fuel,
                credits=new_credits,
                cargo=cargo,
                cargo_capacity=self.state.ship.cargo_capacity,
                current_system_id=self.state.ship.current_system_id,
                orbiting_body_id=self.state.ship.orbiting_body_id,
                power=self.state.ship.power,
                upgrades=self.state.ship.upgrades,
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

            new_ship = ShipState(
                commander_name=self.state.ship.commander_name,
                callsign=self.state.ship.callsign,
                ship_class=self.state.ship.ship_class,
                hull=self.state.ship.hull + actual,
                max_hull=self.state.ship.max_hull,
                shield=self.state.ship.shield,
                max_shield=self.state.ship.max_shield,
                fuel=self.state.ship.fuel,
                max_fuel=self.state.ship.max_fuel,
                credits=self.state.ship.credits - cost,
                cargo=dict(self.state.ship.cargo),
                cargo_capacity=self.state.ship.cargo_capacity,
                current_system_id=self.state.ship.current_system_id,
                orbiting_body_id=self.state.ship.orbiting_body_id,
                power=self.state.ship.power,
                upgrades=self.state.ship.upgrades,
                flight_log=tuple(list(self.state.ship.flight_log[-19:]) + [f"Drydock repair: +{actual} HP for {cost} cr."]),
            )

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
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

            new_ship = ShipState(
                commander_name=self.state.ship.commander_name,
                callsign=self.state.ship.callsign,
                ship_class=self.state.ship.ship_class,
                hull=self.state.ship.hull,
                max_hull=self.state.ship.max_hull,
                shield=self.state.ship.shield,
                max_shield=self.state.ship.max_shield,
                fuel=self.state.ship.fuel + actual,
                max_fuel=self.state.ship.max_fuel,
                credits=self.state.ship.credits - cost,
                cargo=dict(self.state.ship.cargo),
                cargo_capacity=self.state.ship.cargo_capacity,
                current_system_id=self.state.ship.current_system_id,
                orbiting_body_id=self.state.ship.orbiting_body_id,
                power=self.state.ship.power,
                upgrades=self.state.ship.upgrades,
                flight_log=tuple(list(self.state.ship.flight_log[-19:]) + [f"Refueled +{actual} quantum fuel for {cost} cr."]),
            )

            self.state = GameState(
                version=self.state.version,
                galaxy_seed=self.state.galaxy_seed,
                ship=new_ship,
                systems=self.state.systems,
                visited_systems=self.state.visited_systems,
                active_anomaly=self.state.active_anomaly,
                stats=self.state.stats,
            )

            return True, f"Fuel tanks replenished: +{actual} units for {cost} cr."

    def step_orbits(self, delta_time: float = 1.0) -> None:
        """Advance celestial bodies along orbital mechanics paths."""
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
                stats=self.state.stats,
            )

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
                "stats": dict(self.state.stats),
                "market_quotes": market_quotes,
            }
