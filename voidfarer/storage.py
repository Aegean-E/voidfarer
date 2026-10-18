"""Crash-resilient storage engine and atomic persistence for VoidFarer."""

from __future__ import annotations

import json
import os
import shutil
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from voidfarer.models import GameState


class StorageManager:
    """Manages power-loss safe atomic persistence and shadow backups."""

    def __init__(self, data_dir: Path | str) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.save_file = self.data_dir / "voidfarer_save.json"
        self._write_lock = threading.Lock()

    def _write_atomic(self, target_path: Path, data: dict[str, Any]) -> Path:
        """Write JSON payload atomically using a unique temporary file, fsync, and shadow backup."""
        with self._write_lock:
            # Check free disk space (> 10MB)
            try:
                stat = shutil.disk_usage(self.data_dir)
                if stat.free < 10 * 1024 * 1024:
                    raise OSError("Insufficient disk space (< 10MB free)")
            except AttributeError:
                pass

            token = uuid.uuid4().hex
            temp_path = self.data_dir / f".tmp_{target_path.name}_{token}"
            backup_path = target_path.with_suffix(".bak")

            payload = json.dumps(data, indent=2)
            with open(temp_path, "w", encoding="utf-8") as f:
                f.write(payload)
                f.flush()
                os.fsync(f.fileno())

            if target_path.exists():
                backup_temp = self.data_dir / f".tmp_{backup_path.name}_{token}"
                try:
                    shutil.copy2(target_path, backup_temp)
                    with open(backup_temp, "rb+") as bf:
                        os.fsync(bf.fileno())
                    os.replace(backup_temp, backup_path)
                except OSError:
                    backup_temp.unlink(missing_ok=True)

            last_error: OSError | None = None
            for _ in range(5):
                try:
                    os.replace(temp_path, target_path)
                    break
                except OSError as exc:
                    last_error = exc
                    time.sleep(0.02)
            else:
                temp_path.unlink(missing_ok=True)
                raise OSError(f"Atomic save failed for {target_path}") from last_error

            return target_path

    def _read_json_file(self, target_path: Path) -> dict[str, Any] | None:
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else None
        except (json.JSONDecodeError, OSError, UnicodeDecodeError):
            return None

    def _quarantine(self, target_path: Path) -> None:
        if not target_path.exists():
            return
        corrupt_path = self.data_dir / f"{target_path.name}.corrupt_{int(time.time())}"
        try:
            shutil.move(target_path, corrupt_path)
        except OSError:
            pass

    def save(self, state: GameState) -> Path:
        """Atomically persist universe and ship state."""
        return self._write_atomic(self.save_file, state.to_dict())

    def load(self) -> GameState | None:
        """Load game state from disk, quarantining corrupt primary data and trying the backup."""
        primary = self.save_file
        data = self._read_json_file(primary)
        if data is None:
            if primary.exists():
                self._quarantine(primary)
        else:
            try:
                return GameState.from_dict(data)
            except (KeyError, TypeError, ValueError, AttributeError):
                self._quarantine(primary)

        backup_data = self._read_json_file(primary.with_suffix(".bak"))
        if backup_data is None:
            return None
        try:
            return GameState.from_dict(backup_data)
        except (KeyError, TypeError, ValueError, AttributeError):
            return None

    def clear(self) -> None:
        """Remove save file and shadow backup."""
        self.save_file.unlink(missing_ok=True)
        self.save_file.with_suffix(".bak").unlink(missing_ok=True)
