"""Crash-resilient storage engine and atomic persistence for VoidFarer."""

from __future__ import annotations

import json
import os
import shutil
import time
from pathlib import Path
from typing import Any

from voidfarer.models import GameState


class StorageManager:
    """Manages power-loss safe atomic persistence and shadow backups."""

    def __init__(self, data_dir: Path | str) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.save_file = self.data_dir / "voidfarer_save.json"

    def _write_atomic(self, target_path: Path, data: dict[str, Any]) -> Path:
        """Write JSON payload atomically using temporary file, fsync, and shadow backup."""
        # Check free disk space (> 10MB)
        try:
            stat = shutil.disk_usage(self.data_dir)
            if stat.free < 10 * 1024 * 1024:
                raise OSError("Insufficient disk space (< 10MB free)")
        except AttributeError:
            pass

        temp_path = self.data_dir / f".tmp_{target_path.name}_{int(time.time() * 1000)}"
        backup_path = target_path.with_suffix(".bak")

        payload = json.dumps(data, indent=2)
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())

        if target_path.exists():
            shutil.copy2(target_path, backup_path)

        for _ in range(5):
            try:
                os.replace(temp_path, target_path)
                return target_path
            except OSError:
                time.sleep(0.02)

        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        return target_path

    def _read_json_with_backup(self, target_path: Path) -> dict[str, Any] | None:
        """Read JSON safely, quarantining corrupt data and falling back to backup."""
        backup_path = target_path.with_suffix(".bak")

        if target_path.exists():
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                corrupt_path = self.data_dir / f"{target_path.name}.corrupt_{int(time.time())}"
                try:
                    shutil.move(target_path, corrupt_path)
                except OSError:
                    pass

        if backup_path.exists():
            try:
                with open(backup_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass

        return None

    def save(self, state: GameState) -> Path:
        """Atomically persist universe and ship state."""
        return self._write_atomic(self.save_file, state.to_dict())

    def load(self) -> GameState | None:
        """Load game state from disk with corrupt fallback."""
        data = self._read_json_with_backup(self.save_file)
        if not data or not isinstance(data, dict):
            return None
        try:
            return GameState.from_dict(data)
        except (KeyError, TypeError, ValueError):
            return None

    def clear(self) -> None:
        """Remove save file and shadow backup."""
        self.save_file.unlink(missing_ok=True)
        self.save_file.with_suffix(".bak").unlink(missing_ok=True)
