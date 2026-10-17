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


if __name__ == "__main__":
    unittest.main()
