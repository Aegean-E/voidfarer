"""Unit tests for domain state models and frozen DTO serialization."""

import unittest
from voidfarer.models import (
    CelestialBody,
    CombatEncounter,
    FleetDrone,
    GameState,
    ShipPower,
    ShipState,
    ShipUpgrade,
    StarSystem,
)


class TestModels(unittest.TestCase):
    def test_ship_power_validation(self):
        p = ShipPower(engines=30, shields=30, sensors=20, weapons=20)
        self.assertEqual(p.engines + p.shields + p.sensors + p.weapons, 100)

        with self.assertRaises(ValueError):
            ShipPower(engines=50, shields=50, sensors=10, weapons=0)

        with self.assertRaises(ValueError):
            ShipPower(engines=-5, shields=30, sensors=30, weapons=20)

    def test_celestial_body_serialization(self):
        body = CelestialBody(
            id="sol_body_1",
            name="Earth Citadel",
            body_type="orbital_station",
            orbit_radius=1.0,
            orbit_speed=0.05,
            current_angle=0.25,
            radius_km=6371.0,
            color="#00f0ff",
            hazards=("space_debris",),
            station_dockable=True,
            market_archetype="high_tech",
            scan_completed=True,
            scan_discovery="Automated orbital fabricators.",
        )
        d = body.to_dict()
        restored = CelestialBody.from_dict(d)
        self.assertEqual(restored.id, body.id)
        self.assertEqual(restored.name, body.name)
        self.assertTrue(restored.station_dockable)
        self.assertEqual(restored.market_archetype, "high_tech")

    def test_star_system_serialization(self):
        body = CelestialBody(
            id="test_star",
            name="Test Star",
            body_type="star",
            orbit_radius=0.0,
            orbit_speed=0.0,
            current_angle=0.0,
            radius_km=696340.0,
            color="#ffd700",
        )
        system = StarSystem(
            id="test_sys",
            name="Test System",
            seed=1234,
            x=10.5,
            y=-20.5,
            spectral_type="G",
            color="#ffd700",
            security=0.85,
            faction="Test Faction",
            bodies=(body,),
            connections=("sol", "vega"),
        )
        d = system.to_dict()
        restored = StarSystem.from_dict(d)
        self.assertEqual(restored.id, "test_sys")
        self.assertEqual(len(restored.bodies), 1)
        self.assertEqual(restored.connections, ("sol", "vega"))

    def test_fleet_drone_serialization(self):
        drone = FleetDrone(
            id="drone_mining_1",
            name="Mining Sentry Alpha",
            drone_type="mining",
            assigned_system_id="sol",
            status="harvesting",
            cargo_accumulated=8,
            credits_accumulated=150,
        )
        d = drone.to_dict()
        restored = FleetDrone.from_dict(d)
        self.assertEqual(restored.id, drone.id)
        self.assertEqual(restored.drone_type, "mining")
        self.assertEqual(restored.cargo_accumulated, 8)

    def test_ship_upgrade_serialization(self):
        upg = ShipUpgrade(
            id="warp_booster_mk2",
            name="Hyperdrive Booster MK-II",
            slot="engines",
            cost=850,
            description="Quantum field accelerator.",
            stat_bonus={"fuel_efficiency": 0.35},
        )
        d = upg.to_dict()
        restored = ShipUpgrade.from_dict(d)
        self.assertEqual(restored.id, "warp_booster_mk2")
        self.assertEqual(restored.slot, "engines")
        self.assertEqual(restored.cost, 850)

    def test_combat_encounter_serialization(self):
        combat = CombatEncounter(
            id="combat_123",
            enemy_name="Outlaw Raider",
            enemy_class="Corsair",
            enemy_hull=75,
            enemy_max_hull=80,
            enemy_damage=15,
            bounty_credits=500,
        )
        d = combat.to_dict()
        restored = CombatEncounter.from_dict(d)
        self.assertEqual(restored.id, "combat_123")
        self.assertEqual(restored.enemy_name, "Outlaw Raider")
        self.assertEqual(restored.bounty_credits, 500)

    def test_game_state_roundtrip(self):
        ship = ShipState(
            commander_name="Astraea",
            callsign="VF-Vanguard",
            ship_class="Corvette",
            hull=100,
            max_hull=100,
            shield=90,
            max_shield=100,
            fuel=45,
            max_fuel=50,
            credits=3500,
            cargo={"fuel_cells": 3},
            cargo_capacity=30,
            current_system_id="sol",
            orbiting_body_id=None,
            equipped_upgrades={"cargo": "subspace_cargo_pods"},
            fleet_drones=(
                FleetDrone(
                    id="d1",
                    name="Drone 1",
                    drone_type="scout",
                    assigned_system_id="sol",
                ),
            ),
        )
        state = GameState(
            version=1,
            galaxy_seed=42,
            ship=ship,
            systems={},
            visited_systems=("sol",),
        )
        d = state.to_dict()
        restored = GameState.from_dict(d)
        self.assertEqual(restored.version, 1)
        self.assertEqual(restored.ship.commander_name, "Astraea")
        self.assertEqual(restored.ship.credits, 3500)
        self.assertEqual(len(restored.ship.fleet_drones), 1)


if __name__ == "__main__":
    unittest.main()
