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


if __name__ == "__main__":
    unittest.main()
