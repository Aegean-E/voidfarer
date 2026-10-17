"""Unit tests for atomic persistence, crash safety, and shadow backup recovery."""

import tempfile
import unittest
from pathlib import Path

from voidfarer.engine import SimulationEngine
from voidfarer.storage import StorageManager


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.storage = StorageManager(self.temp_dir.name)
        self.engine = SimulationEngine(seed=42)

    def test_save_and_load(self):
        saved_path = self.storage.save(self.engine.state)
        self.assertTrue(saved_path.exists())

        loaded_state = self.storage.load()
        self.assertIsNotNone(loaded_state)
        self.assertEqual(loaded_state.ship.commander_name, self.engine.state.ship.commander_name)
        self.assertEqual(loaded_state.ship.credits, self.engine.state.ship.credits)

    def test_corrupt_file_quarantine_and_backup_recovery(self):
        # 1. Save valid state
        self.storage.save(self.engine.state)

        # 2. Modify state and save again to create shadow .bak
        new_ship = self.engine.state.ship.__class__(
            commander_name="Astraea-Prime",
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
            flight_log=self.engine.state.ship.flight_log,
        )
        self.engine.state = self.engine.state.__class__(
            version=self.engine.state.version,
            galaxy_seed=self.engine.state.galaxy_seed,
            ship=new_ship,
            systems=self.engine.state.systems,
            visited_systems=self.engine.state.visited_systems,
            active_anomaly=self.engine.state.active_anomaly,
            stats=self.engine.state.stats,
        )
        self.storage.save(self.engine.state)


        # 3. Corrupt primary save file
        with open(self.storage.save_file, "w", encoding="utf-8") as f:
            f.write("{ INVALID JSON CORRUPTION ...")

        # 4. Loading should quarantine corrupt file and recover from .bak
        recovered = self.storage.load()
        self.assertIsNotNone(recovered)
        self.assertEqual(recovered.ship.callsign, self.engine.state.ship.callsign)

        # Check quarantine file was generated
        corrupt_files = list(Path(self.temp_dir.name).glob("*.corrupt_*"))
        self.assertEqual(len(corrupt_files), 1)


if __name__ == "__main__":
    unittest.main()
