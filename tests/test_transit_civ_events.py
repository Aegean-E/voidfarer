"""Tests for in-system transit (TravelState), planetary civilization metadata, and cockpit GameEvents."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from voidfarer.cli import main as cli_main
from voidfarer.engine import SimulationEngine
from voidfarer.galaxy import GalaxyGenerator
from voidfarer.models import CelestialBody, GameEvent, GameState, TravelState
from voidfarer.server import ThreadedHTTPServer, VoidFarerHTTPHandler
from voidfarer.storage import StorageManager


class TestTransitCivEvents(unittest.TestCase):
    """Verify TravelState, planetary faction/population/government, and GameEvent lifecycles."""

    def setUp(self) -> None:
        self.engine = SimulationEngine(seed=42)

    def test_gamestate_roundtrip_preserves_events_travel_and_civ_metadata(self) -> None:
        travel = TravelState(
            origin_body_id="sol_body_1",
            destination_body_id="sol_body_2",
            mode="sublight",
            started_tick=2,
            arrival_tick=5,
            distance_au=2.7,
            duration_ticks=3,
        )
        self.assertAlmostEqual(travel.progress(2), 0.0)
        self.assertAlmostEqual(travel.progress(5), 1.0)

        evt = GameEvent(
            id="evt_2_1",
            kind="arrival",
            title="Orbital Capture",
            message="Arrived at Sol B.",
            tick=2,
            dismissed=False,
        )
        ship = self.engine._clone_ship(travel=travel)
        state = self.engine._clone_state(ship=ship, events=(evt,))
        restored = GameState.from_dict(state.to_dict())

        self.assertIsNotNone(restored.ship.travel)
        self.assertEqual(restored.ship.travel.destination_body_id, "sol_body_2")
        self.assertEqual(restored.ship.travel.mode, "sublight")
        self.assertEqual(len(restored.events), 1)
        self.assertEqual(restored.events[0].id, "evt_2_1")
        self.assertEqual(restored.events[0].title, "Orbital Capture")

    def test_galaxy_generates_planetary_civilization_metadata(self) -> None:
        systems = GalaxyGenerator(seed=42).generate_galaxy()
        sol = systems["sol"]
        star = sol.bodies[0]
        self.assertEqual(star.body_type, "star")
        self.assertEqual(star.population, 0)
        self.assertEqual(star.government, "None")

        inhabited = [b for b in sol.bodies[1:] if b.station_dockable or b.landable]
        self.assertTrue(len(inhabited) >= 1)
        for body in inhabited:
            self.assertGreater(body.population, 0)
            self.assertNotEqual(body.government, "None")
            self.assertNotEqual(body.faction, "Unclaimed")

    def test_sublight_transit_progresses_and_completes_on_tick(self) -> None:
        self.engine.orbit("sol_body_1")
        target_id = "sol_body_3"
        fuel_before = self.engine.state.ship.fuel

        ok, msg = self.engine.start_travel(target_id, mode="sublight")
        self.assertTrue(ok, msg)
        self.assertEqual(self.engine.state.ship.fuel, fuel_before)
        travel = self.engine.state.ship.travel
        self.assertIsNotNone(travel)
        self.assertEqual(travel.destination_body_id, target_id)
        self.assertEqual(travel.mode, "sublight")
        self.assertGreaterEqual(travel.duration_ticks, 1)

        # Advance ticks to arrival
        self.engine.tick(travel.duration_ticks)
        self.assertIsNone(self.engine.state.ship.travel)
        self.assertEqual(self.engine.state.ship.orbiting_body_id, target_id)
        self.assertTrue(any(e.kind == "arrival" for e in self.engine.state.events))

    def test_quantum_in_system_transit_consumes_fuel_and_arrives_next_tick(self) -> None:
        self.engine.orbit("sol_body_1")
        target_id = "sol_body_4"
        fuel_before = self.engine.state.ship.fuel

        ok, msg = self.engine.start_travel(target_id, mode="quantum")
        self.assertTrue(ok, msg)
        self.assertLess(self.engine.state.ship.fuel, fuel_before)
        travel = self.engine.state.ship.travel
        self.assertIsNotNone(travel)
        self.assertEqual(travel.mode, "quantum")
        self.assertEqual(travel.duration_ticks, 1)

        self.engine.tick(1)
        self.assertIsNone(self.engine.state.ship.travel)
        self.assertEqual(self.engine.state.ship.orbiting_body_id, target_id)

    def test_start_travel_validation_guards(self) -> None:
        ok_bad_body, _ = self.engine.start_travel("nonexistent_body", mode="sublight")
        self.assertFalse(ok_bad_body)

        ok_bad_mode, _ = self.engine.start_travel("sol_body_2", mode="wormhole")
        self.assertFalse(ok_bad_mode)

        # Insufficient fuel for quantum transit
        self.engine.state = self.engine._clone_state(
            ship=self.engine._clone_ship(fuel=0)
        )
        ok_no_fuel, _ = self.engine.start_travel("sol_body_4", mode="quantum")
        self.assertFalse(ok_no_fuel)

    def test_event_emission_and_dismissal(self) -> None:
        evt = self.engine.emit_event("alert", "Test Alert", "Hull integrity warning.")
        snap = self.engine.get_status_snapshot()
        self.assertEqual(len(snap["undismissed_events"]), 1)
        self.assertEqual(snap["undismissed_events"][0]["id"], evt.id)

        ok, _ = self.engine.dismiss_event(evt.id)
        self.assertTrue(ok)
        snap_after = self.engine.get_status_snapshot()
        self.assertEqual(len(snap_after["undismissed_events"]), 0)

    def test_cli_travel_and_events(self) -> None:
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        save_path = Path(tmp_dir.name) / "save.json"

        rc_travel = cli_main(["--save-path", str(save_path), "travel", "sol_body_2", "--mode", "sublight"])
        self.assertEqual(rc_travel, 0)

        rc_events = cli_main(["--save-path", str(save_path), "events", "list"])
        self.assertEqual(rc_events, 0)
        self.assertIsNotNone(VoidFarerHTTPHandler)


if __name__ == "__main__":
    unittest.main()

