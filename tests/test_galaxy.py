"""Unit tests for procedural galaxy generation, hyperlane mesh, and market quotes."""

import unittest
from voidfarer.galaxy import CANONICAL_COMMODITIES, GalaxyGenerator


class TestGalaxy(unittest.TestCase):
    def test_galaxy_generation_determinism(self):
        gen1 = GalaxyGenerator(seed=1337)
        g1 = gen1.generate_galaxy()

        gen2 = GalaxyGenerator(seed=1337)
        g2 = gen2.generate_galaxy()

        self.assertEqual(len(g1), len(g2))
        self.assertIn("sol", g1)
        self.assertEqual(g1["sol"].connections, g2["sol"].connections)

    def test_hyperlane_connectivity(self):
        gen = GalaxyGenerator(seed=42)
        galaxy = gen.generate_galaxy()

        # Verify that all systems have at least 2 connections
        for sid, system in galaxy.items():
            self.assertGreaterEqual(len(system.connections), 2, f"System {sid} has insufficient links")
            for conn_id in system.connections:
                self.assertIn(conn_id, galaxy)
                # Symmetrical link
                self.assertIn(sid, galaxy[conn_id].connections)

    def test_market_quotes_calculation(self):
        gen = GalaxyGenerator(seed=42)
        galaxy = gen.generate_galaxy()
        sol = galaxy["sol"]
        station = next(b for b in sol.bodies if b.station_dockable)

        quotes = GalaxyGenerator.get_market_quotes(sol, station)
        self.assertEqual(len(quotes), len(CANONICAL_COMMODITIES))
        for q in quotes:
            self.assertGreater(q.buy_price, q.sell_price)
            self.assertGreater(q.sell_price, 0)
            self.assertGreater(q.supply, 0)
            self.assertGreater(q.demand, 0)

    def test_random_anomaly_generation(self):
        anomaly = GalaxyGenerator.get_random_anomaly(seed=999)
        self.assertTrue(anomaly.title)
        self.assertGreaterEqual(len(anomaly.choices), 2)


if __name__ == "__main__":
    unittest.main()
