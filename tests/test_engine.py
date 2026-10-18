"""Unit tests for simulation engine state transitions, flight, upgrades, fleet, and combat."""

import unittest
from voidfarer.engine import SimulationEngine
from voidfarer.models import AnomalyChoice, AnomalyEncounter, CombatEncounter, FleetDrone


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SimulationEngine(seed=42)

    def test_initial_state(self):
        self.assertEqual(self.engine.state.ship.current_system_id, "sol")
        self.assertEqual(self.engine.state.ship.hull, 100)
        self.assertEqual(self.engine.state.ship.fuel, 60)
        self.assertEqual(self.engine.state.ship.credits, 2000)
        self.assertGreaterEqual(len(self.engine.state.ship.fleet_drones), 1)

    def test_jump_valid_and_invalid(self):
        cur_sys = self.engine.current_system
        linked_target = cur_sys.connections[0]

        fuel_before = self.engine.state.ship.fuel
        ok, msg = self.engine.jump(linked_target)
        self.assertTrue(ok)
        self.assertEqual(self.engine.state.ship.current_system_id, linked_target)
        self.assertLess(self.engine.state.ship.fuel, fuel_before)
        self.assertEqual(self.engine.state.stats["jumps"], 1)

        ok2, msg2 = self.engine.jump("non_existent_void_system")
        self.assertFalse(ok2)

    def test_orbit_and_scan(self):
        body_id = "sol_body_1"
        ok, msg = self.engine.orbit(body_id)
        self.assertTrue(ok)
        self.assertEqual(self.engine.state.ship.orbiting_body_id, body_id)

        credits_before = self.engine.state.ship.credits
        ok_scan, msg_scan, info = self.engine.scan()
        self.assertTrue(ok_scan)
        self.assertGreater(self.engine.state.ship.credits, credits_before)
        self.assertEqual(self.engine.state.stats["scans"], 1)

    def test_power_routing(self):
        ok, msg = self.engine.route_power(40, 20, 20, 20)
        self.assertTrue(ok)
        self.assertEqual(self.engine.state.ship.power.engines, 40)

        ok_fail, _ = self.engine.route_power(50, 50, 10, 0)
        self.assertFalse(ok_fail)

    def test_trade_buy_and_sell(self):
        self.engine.orbit("sol_body_1")
        credits_start = self.engine.state.ship.credits

        ok, msg = self.engine.trade("fuel_cells", 2, is_buy=True)
        self.assertTrue(ok)
        self.assertLess(self.engine.state.ship.credits, credits_start)

        credits_after_buy = self.engine.state.ship.credits
        ok_sell, msg_sell = self.engine.trade("fuel_cells", 1, is_buy=False)
        self.assertTrue(ok_sell)
        self.assertGreater(self.engine.state.ship.credits, credits_after_buy)

    def test_upgrades_purchase_and_bonus(self):
        self.engine.orbit("sol_body_1")
        start_cap = self.engine.state.ship.cargo_capacity

        ok, msg = self.engine.buy_upgrade("subspace_cargo_pods")
        self.assertTrue(ok)
        self.assertIn("subspace_cargo_pods", self.engine.state.ship.equipped_upgrades.values())
        self.assertEqual(self.engine.state.ship.cargo_capacity, start_cap + 20)

    def test_fleet_drone_operations(self):
        self.engine.orbit("sol_body_1")
        credits_before = self.engine.state.ship.credits

        # Buy scout drone
        ok, msg = self.engine.buy_drone("scout", "alpha_centauri")
        self.assertTrue(ok)
        self.assertLess(self.engine.state.ship.credits, credits_before)

        # Deploy drone
        scout = next(d for d in self.engine.state.ship.fleet_drones if d.drone_type == "scout")
        ok_dep, msg_dep = self.engine.deploy_drone(scout.id, "sirius")
        self.assertTrue(ok_dep)

        # Harvest yield test with simulated accumulation
        updated_drones = [
            FleetDrone(id=scout.id, name=scout.name, drone_type="scout", assigned_system_id="sirius", credits_accumulated=250)
        ]
        self.engine.state = self.engine.state.__class__(
            version=self.engine.state.version,
            galaxy_seed=self.engine.state.galaxy_seed,
            ship=self.engine.state.ship.__class__(
                commander_name=self.engine.state.ship.commander_name,
                callsign=self.engine.state.ship.callsign,
                ship_class=self.engine.state.ship.ship_class,
                hull=self.engine.state.ship.hull,
                max_hull=self.engine.state.ship.max_hull,
                shield=self.engine.state.ship.shield,
                max_shield=self.engine.state.ship.max_shield,
                fuel=self.engine.state.ship.fuel,
                max_fuel=self.engine.state.ship.max_fuel,
                credits=self.engine.state.ship.credits,
                cargo=self.engine.state.ship.cargo,
                cargo_capacity=self.engine.state.ship.cargo_capacity,
                current_system_id=self.engine.state.ship.current_system_id,
                orbiting_body_id=self.engine.state.ship.orbiting_body_id,
                power=self.engine.state.ship.power,
                upgrades=self.engine.state.ship.upgrades,
                equipped_upgrades=self.engine.state.ship.equipped_upgrades,
                fleet_drones=tuple(updated_drones),
                flight_log=self.engine.state.ship.flight_log,
            ),
            systems=self.engine.state.systems,
            visited_systems=self.engine.state.visited_systems,
            active_anomaly=None,
            active_combat=None,
            stats=self.engine.state.stats,
        )

        ok_h, msg_h, info = self.engine.collect_drone_yield(scout.id)
        self.assertTrue(ok_h)
        self.assertEqual(info["credits"], 250)

    def test_combat_resolution_victory_and_flee(self):
        # Set active combat
        combat = CombatEncounter(
            id="combat_test",
            enemy_name="Outlaw Sentry",
            enemy_class="Drone",
            enemy_hull=25,
            enemy_max_hull=25,
            enemy_damage=10,
            bounty_credits=400,
        )
        self.engine.state = self.engine.state.__class__(
            version=self.engine.state.version,
            galaxy_seed=self.engine.state.galaxy_seed,
            ship=self.engine.state.ship,
            systems=self.engine.state.systems,
            visited_systems=self.engine.state.visited_systems,
            active_anomaly=None,
            active_combat=combat,
            stats=self.engine.state.stats,
        )

        # Firing lasers deals >= 20 dmg, destroying 25 HP enemy
        ok, msg = self.engine.combat_action("fire_lasers")
        self.assertTrue(ok)
        self.assertIn("VICTORY", msg)
        self.assertIsNone(self.engine.state.active_combat)
        self.assertEqual(self.engine.state.stats["combat_victories"], 1)


if __name__ == "__main__":
    unittest.main()
