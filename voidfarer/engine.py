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
    CombatEncounter,
    FleetDrone,
    GameState,
    MarketQuote,
    ShipPower,
    ShipState,
    ShipUpgrade,
    StarSystem,
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

            # Calculate fuel cost (with warp booster upgrade bonus)
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

            if self.state.ship.fuel < fuel_cost:
                return False, f"Insufficient Quantum Fuel: {fuel_cost} units required, {self.state.ship.fuel} available."

            # Execute jump
            new_fuel = self.state.ship.fuel - fuel_cost
            visited = set(self.state.visited_systems)
            visited.add(target_system_id)

            log_entry = f"Hyperspace jump completed to {target_sys.name} (fuel consumed: {fuel_cost})."
            new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

            # Process autonomous fleet drone cycle
            updated_drones = self._process_drone_cycle(self.state.ship)

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
                equipped_upgrades=self.state.ship.equipped_upgrades,
                fleet_drones=updated_drones,
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
                equipped_upgrades=self.state.ship.equipped_upgrades,
                fleet_drones=self.state.ship.fleet_drones,
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

            pwr = self.state.ship.power.sensors
            credit_bounty = int(100 * (pwr / 25.0))
            if "deep_core_scanner" in self.state.ship.equipped_upgrades.values():
                credit_bounty = int(credit_bounty * 1.5)

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
                equipped_upgrades=self.state.ship.equipped_upgrades,
                fleet_drones=self.state.ship.fleet_drones,
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
                equipped_upgrades=self.state.ship.equipped_upgrades,
                fleet_drones=self.state.ship.fleet_drones,
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
                equipped_upgrades=self.state.ship.equipped_upgrades,
                fleet_drones=self.state.ship.fleet_drones,
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

            new_ship = ShipState(
                commander_name=self.state.ship.commander_name,
                callsign=self.state.ship.callsign,
                ship_class=self.state.ship.ship_class,
                hull=self.state.ship.hull,
                max_hull=self.state.ship.max_hull,
                shield=new_shield,
                max_shield=new_max_shield,
                fuel=self.state.ship.fuel,
                max_fuel=self.state.ship.max_fuel,
                credits=new_credits,
                cargo=dict(self.state.ship.cargo),
                cargo_capacity=new_capacity,
                current_system_id=self.state.ship.current_system_id,
                orbiting_body_id=self.state.ship.orbiting_body_id,
                power=self.state.ship.power,
                upgrades=tuple(upg_list),
                equipped_upgrades=equipped,
                fleet_drones=self.state.ship.fleet_drones,
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
                equipped_upgrades=self.state.ship.equipped_upgrades,
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
                power=self.state.ship.power,
                upgrades=self.state.ship.upgrades,
                equipped_upgrades=self.state.ship.equipped_upgrades,
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

            cargo = dict(self.state.ship.cargo)
            # Add cargo (titanium)
            cargo["titanium"] = cargo.get("titanium", 0) + total_cargo
            new_credits = self.state.ship.credits + total_credits

            stats = dict(self.state.stats)
            stats["credits_earned"] += total_credits

            log_entry = f"Fleet harvest collected: +{total_credits} cr and +{total_cargo} titanium units."
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
                equipped_upgrades=self.state.ship.equipped_upgrades,
                fleet_drones=tuple(updated_drones),
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

            if action == "fire_lasers":
                # Calculate player strike damage
                wep_power = self.state.ship.power.weapons
                base_dmg = 20 + int(wep_power * 0.75)
                if "pulse_cannon_array" in self.state.ship.equipped_upgrades.values():
                    base_dmg += 15

                enemy_remaining = combat.enemy_hull - base_dmg

                if enemy_remaining <= 0:
                    # Enemy destroyed
                    new_credits += combat.bounty_credits
                    cargo[combat.salvage_commodity] = cargo.get(combat.salvage_commodity, 0) + 2
                    stats["combat_victories"] += 1
                    stats["credits_earned"] += combat.bounty_credits

                    msg = (
                        f"VICTORY: {combat.enemy_name} neutralized! "
                        f"Collected {combat.bounty_credits} cr bounty and salvaged 2x {combat.salvage_commodity}."
                    )
                    log_entry = f"Combat outcome: {msg}"
                    new_log = list(self.state.ship.flight_log[-19:]) + [log_entry]

                    new_ship = ShipState(
                        commander_name=self.state.ship.commander_name,
                        callsign=self.state.ship.callsign,
                        ship_class=self.state.ship.ship_class,
                        hull=new_hull,
                        max_hull=self.state.ship.max_hull,
                        shield=new_shield,
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
                        equipped_upgrades=self.state.ship.equipped_upgrades,
                        fleet_drones=self.state.ship.fleet_drones,
                        flight_log=tuple(new_log),
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
                if new_shield >= inbound:
                    new_shield -= inbound
                else:
                    overflow = inbound - new_shield
                    new_shield = 0
                    new_hull = max(0, new_hull - overflow)

                msg = f"Laser barrage dealt {base_dmg} damage (Enemy HP: {enemy_remaining}/{combat.enemy_max_hull}). Inbound counter-battery dealt {inbound} damage."
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
                # Emergency shield boost
                new_shield = min(self.state.ship.max_shield, new_shield + 30)
                mitigated = max(1, int(combat.enemy_damage * 0.35))
                if new_shield >= mitigated:
                    new_shield -= mitigated
                else:
                    new_hull = max(0, new_hull - (mitigated - new_shield))
                    new_shield = 0
                msg = f"Shield capacitors overcharged (+30 MW). Enemy barrage deflected, taking only {mitigated} damage."
                new_combat = combat

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

            elif action == "flee":
                if self.state.ship.fuel < 8:
                    return False, "Insufficient fuel for emergency jump (8 units required)."
                new_fuel = self.state.ship.fuel - 8
                msg = "Emergency hyperspace micro-jump executed. Safely disengaged from hostile sector."
                new_combat = None
                new_ship = ShipState(
                    commander_name=self.state.ship.commander_name,
                    callsign=self.state.ship.callsign,
                    ship_class=self.state.ship.ship_class,
                    hull=new_hull,
                    max_hull=self.state.ship.max_hull,
                    shield=new_shield,
                    max_shield=self.state.ship.max_shield,
                    fuel=new_fuel,
                    max_fuel=self.state.ship.max_fuel,
                    credits=self.state.ship.credits,
                    cargo=dict(self.state.ship.cargo),
                    cargo_capacity=self.state.ship.cargo_capacity,
                    current_system_id=self.state.ship.current_system_id,
                    orbiting_body_id=self.state.ship.orbiting_body_id,
                    power=self.state.ship.power,
                    upgrades=self.state.ship.upgrades,
                    equipped_upgrades=self.state.ship.equipped_upgrades,
                    fleet_drones=self.state.ship.fleet_drones,
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
            new_ship = ShipState(
                commander_name=self.state.ship.commander_name,
                callsign=self.state.ship.callsign,
                ship_class=self.state.ship.ship_class,
                hull=new_hull,
                max_hull=self.state.ship.max_hull,
                shield=new_shield,
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
                equipped_upgrades=self.state.ship.equipped_upgrades,
                fleet_drones=self.state.ship.fleet_drones,
                flight_log=tuple(new_log),
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
                        equipped_upgrades=self.state.ship.equipped_upgrades,
                        fleet_drones=self.state.ship.fleet_drones,
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
                equipped_upgrades=self.state.ship.equipped_upgrades,
                fleet_drones=self.state.ship.fleet_drones,
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
                equipped_upgrades=self.state.ship.equipped_upgrades,
                fleet_drones=self.state.ship.fleet_drones,
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
                equipped_upgrades=self.state.ship.equipped_upgrades,
                fleet_drones=self.state.ship.fleet_drones,
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
            }
