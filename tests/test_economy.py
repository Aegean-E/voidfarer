"""Unit tests for the dynamic galactic economy, stockpiles, events, and trade routes."""

import random
import unittest

from voidfarer.engine import SimulationEngine
from voidfarer.economy import (
    calculate_dynamic_market_quote,
    get_galactic_trade_routes,
    tick_global_economy,
)
from voidfarer.galaxy import COMMODITY_MAP


class TestInitialEconomy(unittest.TestCase):
    """Verify baseline economy generation across the galaxy."""

    def setUp(self):
        self.engine = SimulationEngine(seed=42)

    def test_every_system_has_a_market(self):
        econ = self.engine.state.economy
        self.assertEqual(set(econ.markets.keys()), set(self.engine.state.systems.keys()))

    def test_stockpiles_are_positive(self):
        for market in self.engine.state.economy.markets.values():
            for stock in market.stockpiles.values():
                self.assertGreaterEqual(stock, 10)

    def test_initial_event_is_seeded(self):
        ids = {evt.id for evt in self.engine.state.economy.active_events}
        self.assertIn("evt_medical_crisis_alpha_centauri", ids)


class TestTickGlobalEconomy(unittest.TestCase):
    """Verify production, consumption, event decay, and last-updated tracking."""

    def setUp(self):
        self.engine = SimulationEngine(seed=42)
        self.econ = self.engine.state.economy
        self.systems = self.engine.state.systems

    def test_production_and_consumption_rates_apply(self):
        before = dict(self.econ.markets["sol"].stockpiles)
        after_econ, _ = tick_global_economy(self.econ, 8, self.systems, random.Random(1))
        after = after_econ.markets["sol"].stockpiles

        # Production is applied first, then consumption, sequentially per market.
        market = self.econ.markets["sol"]
        expected = dict(before)
        for comm_id, rate in market.production_rates.items():
            growth = int((rate * 8) / 4)
            expected[comm_id] = min(300, expected.get(comm_id, 50) + growth)
        for comm_id, rate in market.consumption_rates.items():
            shrink = int((rate * 8) / 4)
            expected[comm_id] = max(5, expected.get(comm_id, 50) - shrink)
        self.assertEqual(after, expected)

    def test_last_updated_tick_advances(self):
        self.assertEqual(self.econ.last_updated_tick, 0)
        updated, _ = tick_global_economy(self.econ, 5, self.systems, random.Random(1))
        self.assertEqual(updated.last_updated_tick, 5)

    def test_events_decay_and_expire(self):
        decayed, _ = tick_global_economy(self.econ, 10, self.systems, random.Random(7))
        event = next((e for e in decayed.active_events if e.id == "evt_medical_crisis_alpha_centauri"), None)
        self.assertIsNotNone(event)
        self.assertEqual(event.duration_ticks, 40)

        expired, logs = tick_global_economy(decayed, 999, self.systems, random.Random(7))
        self.assertFalse(any(e.id == "evt_medical_crisis_alpha_centauri" for e in expired.active_events))
        self.assertTrue(any("MARKET STABILIZED" in line for line in logs))


class TestDynamicMarketQuotes(unittest.TestCase):
    """Verify localized quote computation and profitable route discovery."""

    def setUp(self):
        self.engine = SimulationEngine(seed=42)

    def test_quote_has_positive_spread(self):
        system = self.engine.current_system
        body = next(b for b in system.bodies if b.station_dockable)
        quote = calculate_dynamic_market_quote(system, body, COMMODITY_MAP["titanium"], self.engine.state.economy)
        self.assertGreater(quote.buy_price, quote.sell_price)
        self.assertGreaterEqual(quote.sell_price, 1)

    def test_events_shift_local_prices(self):
        system = self.engine.state.systems["alpha_centauri"]
        body = next(b for b in system.bodies if b.station_dockable)
        quote = calculate_dynamic_market_quote(system, body, COMMODITY_MAP["medicines"], self.engine.state.economy)
        base_price = COMMODITY_MAP["medicines"].base_price
        self.assertGreater(quote.buy_price, base_price)

    def test_trade_routes_are_sorted_and_cross_system(self):
        routes = get_galactic_trade_routes(self.engine.state.systems, self.engine.state.economy)
        self.assertTrue(routes)
        for route in routes:
            self.assertNotEqual(route["buy_system_id"], route["sell_system_id"])
            self.assertGreater(route["profit_per_unit"], 0)
        profits = [route["profit_per_unit"] for route in routes]
        self.assertEqual(profits, sorted(profits, reverse=True))


if __name__ == "__main__":
    unittest.main()
