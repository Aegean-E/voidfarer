"""Tests for in-system transit (TravelState), planetary civilization metadata, and cockpit GameEvents."""

from __future__ import annotations

import unittest

from voidfarer.engine import SimulationEngine
from voidfarer.galaxy import GalaxyGenerator
from voidfarer.models import CelestialBody, GameEvent, GameState, TravelState


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


if __name__ == "__main__":
    unittest.main()

