"""Unit tests for command-line arguments and subcommands."""

import io
import unittest
from unittest.mock import patch

from voidfarer.cli import main


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


if __name__ == "__main__":
    unittest.main()
