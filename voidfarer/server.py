"""Zero-dependency embedded HTTP server and REST API for the VoidFarer Web Cockpit."""

from __future__ import annotations

import json
import mimetypes
import os
import sys
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from socketserver import ThreadingMixIn
from typing import Any

from voidfarer.engine import SimulationEngine
from voidfarer.storage import StorageManager


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Multi-threaded HTTP server handling concurrent HUD telemetry requests."""
    daemon_threads = True


class VoidFarerHandler(BaseHTTPRequestHandler):
    """Handles REST API actions and serves static cockpit assets."""

    engine: SimulationEngine
    storage: StorageManager
    static_dir: Path

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress standard access logs for clean terminal output."""
        return

    def _send_json(self, data: Any, status: int = 200) -> None:
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(payload)

    def _send_error_json(self, message: str, status: int = 400) -> None:
        self._send_json({"ok": False, "error": message}, status=status)

    def _read_body_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        path = self.path.split("?")[0]

        if path == "/api/state":
            snapshot = self.engine.get_status_snapshot()
            self._send_json({"ok": True, "data": snapshot})
            return

        if path == "/api/galaxy":
            with self.engine.lock:
                systems_data = {
                    sid: s.to_dict() for sid, s in self.engine.state.systems.items()
                }
            self._send_json({"ok": True, "systems": systems_data})
            return

        if path == "/api/contracts":
            with self.engine.lock:
                contracts = [c.to_dict() for c in self.engine.state.ship.active_contracts]
            self._send_json({"ok": True, "contracts": contracts})
            return

        if path == "/api/relics":
            with self.engine.lock:
                relics = [r.to_dict() for r in self.engine.state.ship.relics]
            self._send_json({"ok": True, "relics": relics})
            return

        if path == "/api/tutorial":
            with self.engine.lock:
                tut = self.engine.state.ship.tutorial.to_dict()
            self._send_json({"ok": True, "tutorial": tut})
            return

        if path == "/api/story":
            with self.engine.lock:
                story = self.engine.state.ship.story.to_dict()
            self._send_json({"ok": True, "story": story})
            return

        if path == "/api/time":
            with self.engine.lock:
                time_data = self.engine.state.time.to_dict()
            self._send_json({"ok": True, "time": time_data})
            return

        # Serve static assets
        if path == "/" or path == "":
            rel_path = "index.html"
        else:
            rel_path = path.lstrip("/")

        file_path = (self.static_dir / rel_path).resolve()
        # Security check to prevent directory traversal
        try:
            file_path.relative_to(self.static_dir.resolve())
        except ValueError:
            self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
            return

        if not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Asset not found")
            return

        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = "application/octet-stream"

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except OSError:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, "Error reading file")

    def do_POST(self) -> None:
        path = self.path.split("?")[0]
        body = self._read_body_json()

        if path == "/api/jump":
            target = body.get("target")
            if not target:
                self._send_error_json("Target system ID required")
                return
            ok, msg = self.engine.jump(str(target))
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/orbit":
            target = body.get("target")
            if not target:
                self._send_error_json("Target body ID required")
                return
            ok, msg = self.engine.orbit(str(target))
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/scan":
            ok, msg, info = self.engine.scan()
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "discovery": info, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/power":
            eng = int(body.get("engines", 25))
            shd = int(body.get("shields", 25))
            sen = int(body.get("sensors", 25))
            wep = int(body.get("weapons", 25))
            ok, msg = self.engine.route_power(eng, shd, sen, wep)
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/trade":
            comm_id = str(body.get("commodity_id", ""))
            qty = int(body.get("quantity", 0))
            is_buy = bool(body.get("is_buy", True))
            ok, msg = self.engine.trade(comm_id, qty, is_buy)
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/anomaly":
            choice_id = str(body.get("choice_id", ""))
            ok, msg = self.engine.resolve_anomaly(choice_id)
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/repair":
            amount = int(body.get("amount", 25))
            ok, msg = self.engine.repair_hull(amount)
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/refuel":
            amount = int(body.get("amount", 20))
            ok, msg = self.engine.refuel(amount)
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/upgrade":
            upgrade_id = str(body.get("upgrade_id", ""))
            ok, msg = self.engine.buy_upgrade(upgrade_id)
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/drone/buy":
            drone_type = str(body.get("drone_type", "mining"))
            sys_id = body.get("system_id")
            ok, msg = self.engine.buy_drone(drone_type, sys_id)
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/drone/deploy":
            drone_id = str(body.get("drone_id", ""))
            sys_id = str(body.get("system_id", ""))
            ok, msg = self.engine.deploy_drone(drone_id, sys_id)
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/drone/collect":
            drone_id = body.get("drone_id")
            ok, msg, info = self.engine.collect_drone_yield(drone_id)
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "yield": info, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/combat":
            action = str(body.get("action", "fire_lasers"))
            ok, msg = self.engine.combat_action(action)
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/contract/claim":
            contract_id = str(body.get("contract_id", ""))
            ok, msg, info = self.engine.claim_contract(contract_id)
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "claim_info": info, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/mastery/unlock":
            talent_id = str(body.get("talent_id", ""))
            ok, msg = self.engine.unlock_talent(talent_id)
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/step":
            dt = float(body.get("delta_time", 1.0))
            self.engine.step_orbits(dt)
            self._send_json({"ok": True, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/tutorial/skip":
            ok, msg = self.engine.skip_tutorial()
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/tutorial/reset":
            ok, msg = self.engine.reset_tutorial()
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/story/choice":
            choice_id = str(body.get("choice_id", ""))
            ok, msg = self.engine.make_story_choice(choice_id)
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/time/step":
            ticks = int(body.get("ticks", 1))
            ok, msg, summary = self.engine.step_time(ticks)
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "summary": summary, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/time/speed":
            speed = float(body.get("speed", 1.0))
            ok, msg = self.engine.set_time_speed(speed)
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/time/pause":
            ok, msg = self.engine.pause_time()
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/time/resume":
            ok, msg = self.engine.resume_time()
            self.storage.save(self.engine.state)
            self._send_json({"ok": ok, "message": msg, "state": self.engine.get_status_snapshot()})
            return

        if path == "/api/reset":
            seed = int(body.get("seed", 42))
            self.engine.state = self.engine._create_initial_state(seed)
            self.storage.save(self.engine.state)
            self._send_json({"ok": True, "message": "Simulation reset to factory state.", "state": self.engine.get_status_snapshot()})
            return

        self._send_error_json("Invalid API endpoint", status=HTTPStatus.NOT_FOUND)



def run_server(
    engine: SimulationEngine,
    storage: StorageManager,
    port: int = 8080,
    host: str = "127.0.0.1",
    open_browser: bool = False,
    enable_ticker: bool = True,
) -> None:
    """Start local cockpit HTTP server daemon with background temporal ticker."""
    static_dir = Path(__file__).parent / "static"
    VoidFarerHandler.engine = engine
    VoidFarerHandler.storage = storage
    VoidFarerHandler.static_dir = static_dir

    server = ThreadedHTTPServer((host, port), VoidFarerHandler)
    url = f"http://{host}:{port}"
    print(f"\n=======================================================")
    print(f"🚀 VOIDFARER HOLOGRAPHIC COCKPIT ACTIVE")
    print(f"📡 Cockpit HUD URL: {url}")
    print(f"⏱️ Cosmic Time: SD {round(engine.state.time.stardate, 2)} (Tick #{engine.state.time.tick})")
    print(f"⚡ Press Ctrl+C to disconnect sub-space uplink")
    print(f"=======================================================\n")

    ticker_stop = threading.Event()

    def _ticker_loop() -> None:
        save_counter = 0
        while not ticker_stop.is_set():
            time_obj = engine.state.time
            if not time_obj.is_paused and time_obj.speed > 0:
                interval = max(0.1, 1.0 / time_obj.speed)
                if ticker_stop.wait(interval):
                    break
                engine.tick(1)
                save_counter += 1
                if save_counter >= 10:
                    storage.save(engine.state)
                    save_counter = 0
            else:
                if ticker_stop.wait(0.2):
                    break

    if enable_ticker:
        ticker = threading.Thread(target=_ticker_loop, daemon=True)
        ticker.start()

    if open_browser:
        import webbrowser

        def _launch():
            try:
                getattr(webbrowser, "open")(url)
            except Exception:
                pass

        threading.Timer(0.4, _launch).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down sub-space uplink...")
    finally:
        ticker_stop.set()
        try:
            server.shutdown()
        except Exception:
            pass
        try:
            server.server_close()
        except Exception:
            pass

