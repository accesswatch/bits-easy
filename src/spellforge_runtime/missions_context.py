from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .diagnostics import get_logger
from .engine import AppContext, RuntimeResult

_logger = get_logger("spellforge.missions_context")


class MissionsContextService:
    def __init__(self, storage_path: Path | str | None = None):
        self._storage_path = Path(storage_path) if storage_path else None
        self._missions = {
            "beginner": [
                "capture-note",
                "route-capture",
                "read-fallbacks",
                "select-range",
                "clips-core",
                "notes-core",
                "author-template",
                "author-polish",
            ],
            "balanced": [
                "capture-note",
                "create-task",
                "open-health",
                "select-range",
                "clips-core",
                "cuts-core",
                "notes-core",
                "diary-core",
                "author-template",
                "author-polish",
                "author-html-preview",
                "author-html-apply",
                "author-undo",
            ],
            "expert": [
                "chain-command",
                "virtualize-result",
                "rollback-action",
                "select-range",
                "clips-core",
                "cuts-core",
                "notes-core",
                "diary-core",
                "author-template",
                "author-polish",
                "author-html-preview",
                "author-html-apply",
                "author-undo",
            ],
        }
        self._progress: Dict[str, List[str]] = {}
        self._load()

    def _save(self) -> None:
        if not self._storage_path:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_path.write_text(json.dumps({"progress": self._progress}, ensure_ascii=True, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if not self._storage_path or not self._storage_path.exists():
            return
        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except Exception:
            _logger.exception("Spellforge: loading missions progress at %s failed", self._storage_path)
            return
        self._progress = payload.get("progress", {}) if isinstance(payload.get("progress", {}), dict) else {}

    def where_am_i(self, context: AppContext, last_action: str, mode: str) -> RuntimeResult:
        has_selection = bool(context.buffer and 0 <= context.caret <= len(context.buffer))
        return RuntimeResult(
            ok=True,
            message="Context readout ready.",
            payload={
                "appId": context.app_id,
                "controlId": context.control_id,
                "selectionState": "available" if has_selection else "none",
                "mode": mode,
                "lastAction": last_action,
            },
        )

    def missions_start(self, profile_id: str) -> RuntimeResult:
        profile = profile_id.strip().lower() or "balanced"
        seq = list(self._missions.get(profile, self._missions["balanced"]))
        done = self._progress.get(profile, [])
        next_item = next((x for x in seq if x not in done), "")
        return RuntimeResult(ok=True, message="Mission sequence ready.", payload={"profile": profile, "missions": seq, "next": next_item})

    def missions_complete(self, profile_id: str, mission_id: str) -> RuntimeResult:
        profile = profile_id.strip().lower() or "balanced"
        mid = mission_id.strip().lower()
        seq = self._missions.get(profile, [])
        if mid not in seq:
            return RuntimeResult(ok=False, message="Mission is not part of this profile sequence.")
        done = self._progress.setdefault(profile, [])
        if mid not in done:
            done.append(mid)
        self._save()
        next_item = next((x for x in seq if x not in done), "")
        return RuntimeResult(ok=True, message="Mission completed.", payload={"profile": profile, "completed": list(done), "next": next_item})

    def missions_status(self, profile_id: str) -> RuntimeResult:
        profile = profile_id.strip().lower() or "balanced"
        seq = list(self._missions.get(profile, self._missions["balanced"]))
        done = list(self._progress.get(profile, []))
        return RuntimeResult(ok=True, message="Mission status ready.", payload={"profile": profile, "missions": seq, "completed": done})
