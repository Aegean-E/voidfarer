"""Unit tests for command-line arguments and subcommands."""

import io
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch

from voidfarer.cli import cmd_inventory, cmd_repl, main
from voidfarer.engine import SimulationEngine
from voidfarer.storage import StorageManager


class TestCLI(unittest.TestCase):
    def test_cli_help(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main([])
            self.assertEqual(code, 0)
            self.assertIn("voidfarer", mock_out.getvalue().lower())

    def test_cli_status(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main(["status"])
            self.assertEqual(code, 0)
            output = mock_out.getvalue()
            self.assertIn("Astraea", output)
            self.assertIn("VF-Vanguard", output)

    def test_cli_chart(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main(["chart"])
            self.assertEqual(code, 0)
            output = mock_out.getvalue()
            self.assertIn("GALAXY SECTOR", output)
            self.assertIn("Sol System", output)

    def test_cli_power(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main(["power", "25", "25", "25", "25"])
            self.assertEqual(code, 0)

    def test_cli_fleet_list(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main(["fleet", "list"])
            self.assertEqual(code, 0)
            self.assertIn("FLEET COMMAND", mock_out.getvalue())

    def test_cli_upgrades_list(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main(["upgrades", "list"])
            self.assertEqual(code, 0)
            self.assertIn("STATION ARSENAL", mock_out.getvalue())

    def test_cli_contracts_list(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main(["contracts", "list"])
            self.assertEqual(code, 0)
            self.assertIn("ACTIVE SECTOR BOUNTIES", mock_out.getvalue())

    def test_cli_mastery_status(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main(["mastery", "status"])
            self.assertEqual(code, 0)
            self.assertIn("PILOT MASTERY", mock_out.getvalue())
            self.assertIn("Void Cartographer", mock_out.getvalue())

    def test_cli_relics(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main(["relics"])
            self.assertEqual(code, 0)
            self.assertIn("PRECURSOR RELICS VAULT", mock_out.getvalue())

    def test_cli_streak(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main(["streak"])
            self.assertEqual(code, 0)
            self.assertIn("EXPEDITION JUMP STREAK", mock_out.getvalue())


class TestCLIStabilization(unittest.TestCase):
    """Regression tests for numeric guards and the station consumable terminal."""

    def setUp(self):
        self._tmp = TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.storage = StorageManager(self._tmp.name)

    def test_inventory_jettison_non_numeric_quantity_is_handled(self):
        engine = SimulationEngine(seed=42)
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = cmd_inventory(engine, self.storage, ["inventory", "jettison", "titanium", "abc"])
        self.assertEqual(code, 1)
        self.assertIn("integer", mock_out.getvalue().lower())

    def test_inventory_buy_usage_without_item_id(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = main(["inventory", "buy"])
        self.assertEqual(code, 1)
        self.assertIn("usage", mock_out.getvalue().lower())

    def test_inventory_buy_consumable_at_station(self):
        engine = SimulationEngine(seed=42)
        engine.orbit("sol_body_1")
        engine.state = engine._clone_state(ship=engine._clone_ship(credits=5000))
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            code = cmd_inventory(engine, self.storage, ["inventory", "buy", "nanite_repair_paste"])
        self.assertEqual(code, 0)
        self.assertIn("Purchased", mock_out.getvalue())
        self.assertEqual(engine.state.ship.cargo.get("nanite_repair_paste"), 1)

    def test_repl_repair_and_refuel_reject_non_numeric_amounts(self):
        engine = SimulationEngine(seed=42)
        with patch("builtins.input", side_effect=["repair abc", "refuel xyz", "exit"]):
            with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
                code = cmd_repl(engine, self.storage)
        self.assertEqual(code, 0)
        output = mock_out.getvalue().lower()
        self.assertEqual(output.count("must be an integer"), 2)
        self.assertNotIn("traceback", output)


if __name__ == "__main__":
    unittest.main()
