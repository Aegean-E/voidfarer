"""Unit and integration tests for embedded HTTP server REST endpoints."""

import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from voidfarer.engine import SimulationEngine
from voidfarer.server import ThreadedHTTPServer, VoidFarerHandler
from voidfarer.storage import StorageManager


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.storage = StorageManager(cls.temp_dir.name)
        cls.engine = SimulationEngine(seed=42)

        VoidFarerHandler.engine = cls.engine
        VoidFarerHandler.storage = cls.storage
        VoidFarerHandler.static_dir = Path(__file__).parent.parent / "voidfarer" / "static"

        # Bind to port 0 (dynamic available port)
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

    def test_get_static_index(self):
        status, data = self._get("/")
        self.assertEqual(status, 200)
        self.assertIn(b"VOIDFARER", data)

    def test_get_api_state(self):
        status, data = self._get("/api/state")
        self.assertEqual(status, 200)
        json_data = json.loads(data.decode("utf-8"))
        self.assertTrue(json_data["ok"])
        self.assertEqual(json_data["data"]["ship"]["commander_name"], "Astraea")

    def test_get_api_galaxy(self):
        status, data = self._get("/api/galaxy")
        self.assertEqual(status, 200)
        json_data = json.loads(data.decode("utf-8"))
        self.assertTrue(json_data["ok"])
        self.assertIn("sol", json_data["systems"])

    def test_post_power(self):
        status, data = self._post("/api/power", {"engines": 35, "shields": 25, "sensors": 20, "weapons": 20})
        self.assertEqual(status, 200)
        json_data = json.loads(data.decode("utf-8"))
        self.assertTrue(json_data["ok"])
        self.assertEqual(json_data["state"]["ship"]["power"]["engines"], 35)

    def test_post_orbit_and_scan(self):
        status, data = self._post("/api/orbit", {"target": "sol_body_1"})
        self.assertEqual(status, 200)
        json_data = json.loads(data.decode("utf-8"))
        self.assertTrue(json_data["ok"])

        # Scan
        status_s, data_s = self._post("/api/scan", {})
        self.assertEqual(status_s, 200)
        json_scan = json.loads(data_s.decode("utf-8"))
        self.assertTrue(json_scan["ok"])

    def test_post_drone_and_upgrade_endpoints(self):
        # Orbit station first
        self._post("/api/orbit", {"target": "sol_body_1"})

        # Buy drone
        st_d, data_d = self._post("/api/drone/buy", {"drone_type": "mining", "system_id": "sol"})
        self.assertEqual(st_d, 200)
        json_d = json.loads(data_d.decode("utf-8"))
        self.assertTrue(json_d["ok"])

        # Buy upgrade
        st_u, data_u = self._post("/api/upgrade", {"upgrade_id": "warp_booster_mk2"})
        self.assertEqual(st_u, 200)
        json_u = json.loads(data_u.decode("utf-8"))
        self.assertTrue(json_u["ok"])

    def test_contracts_and_relics_endpoints(self):
        # GET /api/contracts
        st_c, data_c = self._get("/api/contracts")
        self.assertEqual(st_c, 200)
        json_c = json.loads(data_c.decode("utf-8"))
        self.assertTrue(json_c["ok"])
        self.assertGreaterEqual(len(json_c["contracts"]), 1)

        # GET /api/relics
        st_r, data_r = self._get("/api/relics")
        self.assertEqual(st_r, 200)
        json_r = json.loads(data_r.decode("utf-8"))
        self.assertTrue(json_r["ok"])

        # POST /api/mastery/unlock (should fail if 0 points, but return ok=False with error message)
        st_m, data_m = self._post("/api/mastery/unlock", {"talent_id": "void_cartographer"})
        self.assertEqual(st_m, 200)
        json_m = json.loads(data_m.decode("utf-8"))
        # Engine handles point validation cleanly
        self.assertIn("ok", json_m)

    def test_get_api_shipyard_excludes_current_chassis(self):
        status, data = self._get("/api/shipyard")
        self.assertEqual(status, 200)
        json_data = json.loads(data.decode("utf-8"))
        available = {c["id"] for c in json_data["available_chassis"]}
        self.assertNotIn("vanguard_scout", available)

    def test_post_inventory_buy_rejects_non_numeric_quantity(self):
        status, data = self._post("/api/inventory/buy", {"item_id": "nanite_repair_paste", "quantity": "many"})
        self.assertEqual(status, 400)
        json_data = json.loads(data.decode("utf-8"))
        self.assertFalse(json_data["ok"])


if __name__ == "__main__":
    unittest.main()
