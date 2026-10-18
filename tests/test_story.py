"""Unit and integration tests for Cadet Flight Academy and The Precursor Cipher story campaign."""

import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from voidfarer.cli import cmd_story, cmd_tutorial, main
from voidfarer.engine import SimulationEngine
from voidfarer.models import ShipState, StoryState, TutorialState
from voidfarer.server import ThreadedHTTPServer, VoidFarerHandler
from voidfarer.storage import StorageManager
from voidfarer.story import (
    CAMPAIGN_CHAPTERS,
    INITIAL_TUTORIAL_STEPS,
    STORY_RELICS,
    create_initial_story_state,
    create_initial_tutorial_state,
)


class TestStoryAndTutorial(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.storage = StorageManager(self.temp_dir.name)
        self.engine = SimulationEngine(seed=42)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_tutorial_initial_state(self):
        tut = self.engine.state.ship.tutorial
        self.assertFalse(tut.completed)
        self.assertFalse(tut.skipped)
        self.assertTrue(tut.is_active)
        self.assertEqual(tut.current_step_index, 0)
        self.assertEqual(tut.current_step.action_target, "orbit")
        self.assertEqual(len(tut.steps), 6)

    def test_tutorial_progressive_milestones(self):
        start_credits = self.engine.state.ship.credits
        start_xp = self.engine.state.ship.mastery.xp

        # Step 0: Orbit
        first_body = self.engine.current_system.bodies[1]  # planet
        ok, msg = self.engine.orbit(first_body.id)
        self.assertTrue(ok)
        tut = self.engine.state.ship.tutorial
        self.assertEqual(tut.current_step_index, 1)
        self.assertTrue(tut.steps[0].completed)
        self.assertGreater(self.engine.state.ship.credits, start_credits)
        self.assertGreater(self.engine.state.ship.mastery.xp, start_xp)

        # Step 1: Scan
        step1_credits = self.engine.state.ship.credits
        ok, msg, _ = self.engine.scan()
        self.assertTrue(ok)
        tut = self.engine.state.ship.tutorial
        self.assertEqual(tut.current_step_index, 2)
        self.assertTrue(tut.steps[1].completed)
        self.assertGreater(self.engine.state.ship.credits, step1_credits)

        # Step 2: Power Routing
        ok, msg = self.engine.route_power(30, 30, 20, 20)
        self.assertTrue(ok)
        tut = self.engine.state.ship.tutorial
        self.assertEqual(tut.current_step_index, 3)
        self.assertTrue(tut.steps[2].completed)

        # Step 3: Trade (must orbit station first)
        station = [b for b in self.engine.current_system.bodies if b.station_dockable][0]
        self.engine.orbit(station.id)
        from voidfarer.galaxy import GalaxyGenerator
        quotes = GalaxyGenerator.get_market_quotes(self.engine.current_system, station)
        ok, msg = self.engine.trade(quotes[0].commodity_id, 1, is_buy=True)
        self.assertTrue(ok)
        tut = self.engine.state.ship.tutorial
        self.assertEqual(tut.current_step_index, 4)
        self.assertTrue(tut.steps[3].completed)

        # Step 4: Fleet Drone
        with self.engine.lock:
            from voidfarer.models import GameState
            self.engine.state = GameState(
                version=self.engine.state.version,
                galaxy_seed=self.engine.state.galaxy_seed,
                ship=self.engine._clone_ship(credits=self.engine.state.ship.credits + 1000),
                systems=self.engine.state.systems,
                visited_systems=self.engine.state.visited_systems,
                active_anomaly=self.engine.state.active_anomaly,
                active_combat=self.engine.state.active_combat,
                stats=self.engine.state.stats,
            )
        ok, msg = self.engine.buy_drone("scout")
        self.assertTrue(ok)
        tut = self.engine.state.ship.tutorial
        self.assertEqual(tut.current_step_index, 5)
        self.assertTrue(tut.steps[4].completed)

        # Step 5: Jump & Graduation
        pre_grad_credits = self.engine.state.ship.credits
        target_sys = self.engine.current_system.connections[0]
        ok, msg = self.engine.jump(target_sys)
        self.assertTrue(ok)
        tut = self.engine.state.ship.tutorial
        self.assertTrue(tut.completed)
        self.assertFalse(tut.is_active)
        self.assertGreaterEqual(self.engine.state.ship.credits, pre_grad_credits + 1500)

        # Check Cadet Wings relic
        relic_ids = [r.id for r in self.engine.state.ship.relics]
        self.assertIn("relic_cadet_wings", relic_ids)

    def test_tutorial_skip_and_reset(self):
        self.assertTrue(self.engine.state.ship.tutorial.is_active)

        ok, msg = self.engine.skip_tutorial()
        self.assertTrue(ok)
        self.assertTrue(self.engine.state.ship.tutorial.skipped)
        self.assertFalse(self.engine.state.ship.tutorial.is_active)

        # Reset tutorial
        ok, msg = self.engine.reset_tutorial()
        self.assertTrue(ok)
        tut = self.engine.state.ship.tutorial
        self.assertFalse(tut.skipped)
        self.assertFalse(tut.completed)
        self.assertEqual(tut.current_step_index, 0)
        self.assertTrue(tut.is_active)

    def test_story_initialization_and_first_chapter(self):
        story = self.engine.state.ship.story
        self.assertEqual(story.active_act, 1)
        self.assertEqual(story.current_chapter_id, "act1_ghost_signal")
        chap = story.current_chapter
        self.assertEqual(chap.target_system_id, "sol")
        self.assertFalse(chap.completed)
        self.assertGreater(len(story.transmission_log), 0)

    def test_story_arrival_transmissions(self):
        initial_log_len = len(self.engine.state.ship.story.transmission_log)
        self.assertEqual(initial_log_len, 1)

        # Resolve Act 1 first to unlock Act 2 (Sirius)
        ok, msg = self.engine.make_story_choice("choice_vance_telemetry")
        self.assertTrue(ok)
        self.assertGreater(len(self.engine.state.ship.story.transmission_log), initial_log_len)

        # Jump to sirius (Act 2 target)
        ok, msg = self.engine.jump("sirius")
        self.assertTrue(ok)
        new_story = self.engine.state.ship.story
        speakers = [tx.speaker for tx in new_story.transmission_log]
        self.assertTrue(any("Cipher" in s for s in speakers))

    def test_story_choices_and_factions(self):
        story = self.engine.state.ship.story
        ship = self.engine.state.ship

        # Invalid choice test
        ok, msg = self.engine.make_story_choice("invalid_choice_999")
        self.assertFalse(ok)

        # Valid choice: choice_cipher_leak
        ok, msg = self.engine.make_story_choice("choice_cipher_leak")
        self.assertTrue(ok)
        self.assertIn("Decryption Key", msg)

        # Faction reputation verified
        updated_ship = self.engine.state.ship
        self.assertGreater(updated_ship.story.faction_reputation["syndicate"], 0)
        self.assertEqual(updated_ship.story.active_act, 2)
        self.assertEqual(updated_ship.story.current_chapter_id, "act2_sirius_forge")

        # Check Relic award
        relic_ids = [r.id for r in updated_ship.relics]
        self.assertIn("relic_cipher_key", relic_ids)

    def test_story_serialization_roundtrip(self):
        ship = self.engine.state.ship
        data = ship.to_dict()
        restored_ship = ShipState.from_dict(data)

        self.assertEqual(restored_ship.tutorial.current_step_index, ship.tutorial.current_step_index)
        self.assertEqual(restored_ship.story.active_act, ship.story.active_act)
        self.assertEqual(len(restored_ship.story.transmission_log), len(ship.story.transmission_log))

    def test_cli_tutorial_and_story_commands(self):
        # cmd_tutorial status
        res = cmd_tutorial(self.engine, self.storage, ["tutorial"])
        self.assertEqual(res, 0)

        # cmd_tutorial skip
        res = cmd_tutorial(self.engine, self.storage, ["tutorial", "skip"])
        self.assertEqual(res, 0)
        self.assertTrue(self.engine.state.ship.tutorial.skipped)

        # cmd_tutorial reset
        res = cmd_tutorial(self.engine, self.storage, ["tutorial", "reset"])
        self.assertEqual(res, 0)
        self.assertFalse(self.engine.state.ship.tutorial.skipped)

        # cmd_story status
        res = cmd_story(self.engine, self.storage, ["story"])
        self.assertEqual(res, 0)

        # Choose via CLI
        res = cmd_story(self.engine, self.storage, ["story", "choose", "choice_vance_telemetry"])
        self.assertEqual(res, 0)
        self.assertGreater(self.engine.state.ship.story.faction_reputation["coalition"], 0)

    def test_cli_main_entrypoint(self):
        res = main(["tutorial", "status"])
        self.assertEqual(res, 0)

        res = main(["story", "status"])
        self.assertEqual(res, 0)


class TestServerStoryAndTutorial(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.storage = StorageManager(cls.temp_dir.name)
        cls.engine = SimulationEngine(seed=42)

        VoidFarerHandler.engine = cls.engine
        VoidFarerHandler.storage = cls.storage
        VoidFarerHandler.static_dir = Path(__file__).parent.parent / "voidfarer" / "static"

        cls.server = ThreadedHTTPServer(("127.0.0.1", 0), VoidFarerHandler)
        cls.port = cls.server.server_port

        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.temp_dir.cleanup()

    def _get(self, path: str):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=2)
        conn.request("GET", path)
        res = conn.getresponse()
        data = res.read()
        conn.close()
        return res.status, data

    def _post(self, path: str, body: dict):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=2)
        payload = json.dumps(body)
        conn.request("POST", path, body=payload, headers={"Content-Type": "application/json"})
        res = conn.getresponse()
        data = res.read()
        conn.close()
        return res.status, data

    def test_server_tutorial_endpoints(self):
        # GET /api/tutorial
        status, data = self._get("/api/tutorial")
        self.assertEqual(status, 200)
        json_data = json.loads(data.decode("utf-8"))
        self.assertTrue(json_data["ok"])
        self.assertEqual(json_data["tutorial"]["current_step_index"], 0)

        # POST /api/tutorial/skip
        status, data = self._post("/api/tutorial/skip", {})
        self.assertEqual(status, 200)
        json_data = json.loads(data.decode("utf-8"))
        self.assertTrue(json_data["ok"])

        # POST /api/tutorial/reset
        status, data = self._post("/api/tutorial/reset", {})
        self.assertEqual(status, 200)
        json_data = json.loads(data.decode("utf-8"))
        self.assertTrue(json_data["ok"])

    def test_server_story_endpoints(self):
        # GET /api/story
        status, data = self._get("/api/story")
        self.assertEqual(status, 200)
        json_data = json.loads(data.decode("utf-8"))
        self.assertTrue(json_data["ok"])
        self.assertEqual(json_data["story"]["active_act"], 1)

        # POST /api/story/choice (invalid)
        status, data = self._post("/api/story/choice", {"choice_id": "nonexistent"})
        self.assertEqual(status, 200)
        json_data = json.loads(data.decode("utf-8"))
        self.assertFalse(json_data["ok"])

        # POST /api/story/choice (valid)
        status, data = self._post("/api/story/choice", {"choice_id": "choice_vance_telemetry"})
        self.assertEqual(status, 200)
        json_data = json.loads(data.decode("utf-8"))
        self.assertTrue(json_data["ok"])


if __name__ == "__main__":
    unittest.main()
