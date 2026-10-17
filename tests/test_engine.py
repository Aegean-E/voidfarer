"""Unit tests for simulation engine state transitions, flight, combat/anomalies, and commerce."""

import unittest
from voidfarer.engine import SimulationEngine
from voidfarer.models import AnomalyChoice, AnomalyEncounter


class TestEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SimulationEngine(seed=42)

    def test_initial_state(self):
        self.assertEqual(self.engine.state.ship.current_system_id, "sol")
        self.assertEqual(self.engine.state.ship.hull, 100)
        self.assertEqual(self.engine.state.ship.fuel, 60)
        self.assertEqual(self.engine.state.ship.credits, 2000)

    def test_jump_valid_and_invalid(self):
        cur_sys = self.engine.current_system
        linked_target = cur_sys.connections[0]

        # Valid jump
        fuel_before = self.engine.state.ship.fuel
        ok, msg = self.engine.jump(linked_target)
        self.assertTrue(ok)
        self.assertEqual(self.engine.state.ship.current_system_id, linked_target)
        self.assertLess(self.engine.state.ship.fuel, fuel_before)
        self.assertEqual(self.engine.state.stats["jumps"], 1)

        # Invalid jump to non-connected or unknown system
        ok2, msg2 = self.engine.jump("non_existent_void_system")
        self.assertFalse(ok2)


    def test_orbit_and_scan(self):
        body_id = "sol_body_1"
        ok, msg = self.engine.orbit(body_id)
        self.assertTrue(ok)
        self.assertEqual(self.engine.state.ship.orbiting_body_id, body_id)

        # Scan
        credits_before = self.engine.state.ship.credits
        ok_scan, msg_scan, info = self.engine.scan()
        self.assertTrue(ok_scan)
        self.assertGreater(self.engine.state.ship.credits, credits_before)
        self.assertEqual(self.engine.state.stats["scans"], 1)

    def test_power_routing(self):
        ok, msg = self.engine.route_power(40, 20, 20, 20)
        self.assertTrue(ok)
        self.assertEqual(self.engine.state.ship.power.engines, 40)

        # Total > 100 should fail
        ok_fail, _ = self.engine.route_power(50, 50, 10, 0)
        self.assertFalse(ok_fail)

    def test_trade_buy_and_sell(self):
        # Orbit dockable station
        self.engine.orbit("sol_body_1")
        credits_start = self.engine.state.ship.credits

        # Buy 2 fuel cells
        ok, msg = self.engine.trade("fuel_cells", 2, is_buy=True)
        self.assertTrue(ok)
        self.assertLess(self.engine.state.ship.credits, credits_start)
        self.assertGreaterEqual(self.engine.state.ship.cargo["fuel_cells"], 7)

        # Sell 1 fuel cell
        credits_after_buy = self.engine.state.ship.credits
        ok_sell, msg_sell = self.engine.trade("fuel_cells", 1, is_buy=False)
        self.assertTrue(ok_sell)
        self.assertGreater(self.engine.state.ship.credits, credits_after_buy)

    def test_anomaly_resolution(self):
        # Setup manual encounter
        choice = AnomalyChoice(
            choice_id="safe_probe",
            text="Launch passive probe",
            required_power="sensors",
            min_power_threshold=10,
            outcome_text="Telemetry captured.",
            credits_delta=200,
        )
        anomaly = AnomalyEncounter(
            id="test_anom",
            title="Spatial Anomaly",
            description="Mysterious nebula rift.",
            severity="minor",
            choices=(choice,),
        )
        self.engine.state = self.engine.state.__class__(
            version=self.engine.state.version,
            galaxy_seed=self.engine.state.galaxy_seed,
            ship=self.engine.state.ship,
            systems=self.engine.state.systems,
            visited_systems=self.engine.state.visited_systems,
            active_anomaly=anomaly,
            stats=self.engine.state.stats,
        )

        ok, msg = self.engine.resolve_anomaly("safe_probe")
        self.assertTrue(ok)
        self.assertIsNone(self.engine.state.active_anomaly)
        self.assertEqual(self.engine.state.stats["anomalies_resolved"], 1)


if __name__ == "__main__":
    unittest.main()
