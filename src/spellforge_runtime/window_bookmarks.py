from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .diagnostics import get_logger
from .engine import RuntimeResult

_logger = get_logger("spellforge.window_bookmarks")


class WindowBookmarks:
    def __init__(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self._slots: Dict[int, dict] = {}
        self._load()

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            payload = json.loads(self.storage_path.read_text(encoding="utf-8"))
            raw = payload.get("slots", {}) if isinstance(payload, dict) else {}
            self._slots = {
                int(k): {
                    "windowId": str(v.get("windowId", "")),
                    "appId": str(v.get("appId", "")),
                    "name": str(v.get("name", "")),
                }
                for k, v in raw.items()
                if str(k).isdigit()
            }
        except Exception:
            _logger.exception("Spellforge: loading window bookmarks at %s failed", self.storage_path)
            self._slots = {}

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "slots": {str(k): v for k, v in sorted(self._slots.items())},
        }
        self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def assign(self, slot: int, *, window_id: str, app_id: str, name: str = "") -> RuntimeResult:
        s = int(slot)
        if s < 1 or s > 10:
            return RuntimeResult(ok=False, message="Bookmark slot must be between 1 and 10.")
        if not window_id.strip():
            return RuntimeResult(ok=False, message="windowId is required.")

        label = name.strip() or f"{app_id.strip() or 'window'}-{s}"
        self._slots[s] = {
            "windowId": window_id.strip(),
            "appId": app_id.strip(),
            "name": label,
        }
        self._save()
        return RuntimeResult(ok=True, message="Window bookmark assigned.", payload={"slot": s, "name": label})

    def recall(self, slot: int) -> RuntimeResult:
        s = int(slot)
        entry = self._slots.get(s)
        if entry is None:
            return RuntimeResult(
                ok=False,
                message="No window bookmark in that slot.",
                next_steps=["Assign a bookmark to this slot first."],
            )
        return RuntimeResult(
            ok=True,
            message="Window bookmark recalled.",
            payload={"slot": s, **entry},
        )

    def rename(self, slot: int, name: str) -> RuntimeResult:
        s = int(slot)
        entry = self._slots.get(s)
        if entry is None:
            return RuntimeResult(ok=False, message="No window bookmark in that slot.")
        new_name = name.strip()
        if not new_name:
            return RuntimeResult(ok=False, message="Bookmark name is required.")
        entry["name"] = new_name
        self._save()
        return RuntimeResult(ok=True, message="Window bookmark renamed.", payload={"slot": s, "name": new_name})

    def list_slots(self) -> RuntimeResult:
        rows = [{"slot": s, **entry} for s, entry in sorted(self._slots.items())]
        return RuntimeResult(ok=True, message="Window bookmark list ready.", payload={"items": rows, "count": len(rows)})
