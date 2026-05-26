from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .diagnostics import get_logger
from .engine import RuntimeResult

_logger = get_logger("bits_easy.utility_ops")


class UtilityOpsService:
    def __init__(self, storage_path: Path | str | None = None):
        self._storage_path = Path(storage_path) if storage_path else None
        self._rules: Dict[str, Any] = {}
        self._rules_backup: Dict[str, Any] = {}
        self._audio = {"speechPan": 0, "appPan": 0, "cardIndex": 0, "cards": ["default", "hdmi", "usb"]}
        self._load()

    def _save(self) -> None:
        if not self._storage_path:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"rules": self._rules, "rulesBackup": self._rules_backup, "audio": self._audio}
        self._storage_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if not self._storage_path or not self._storage_path.exists():
            return
        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except Exception:
            _logger.exception("BITS-EASY: loading utility ops state at %s failed", self._storage_path)
            return
        self._rules = payload.get("rules", {}) if isinstance(payload.get("rules", {}), dict) else {}
        self._rules_backup = payload.get("rulesBackup", {}) if isinstance(payload.get("rulesBackup", {}), dict) else {}
        self._audio = payload.get("audio", self._audio) if isinstance(payload.get("audio", {}), dict) else self._audio

    def import_rules(self, rules: Dict[str, Any], *, confirm: bool) -> RuntimeResult:
        if not confirm:
            return RuntimeResult(ok=False, message="Rules import requires explicit confirmation.")
        self._rules_backup = dict(self._rules)
        self._rules = dict(rules)
        self._save()
        return RuntimeResult(ok=True, message="Notification rules imported.", payload={"count": len(self._rules)})

    def restore_rules(self) -> RuntimeResult:
        self._rules = dict(self._rules_backup)
        self._save()
        return RuntimeResult(ok=True, message="Notification rules restored.", payload={"count": len(self._rules)})

    def audio_split(self, speech_pan: int, app_pan: int) -> RuntimeResult:
        self._audio["speechPan"] = max(-100, min(100, int(speech_pan)))
        self._audio["appPan"] = max(-100, min(100, int(app_pan)))
        self._save()
        return RuntimeResult(ok=True, message="Audio split updated.", payload={"speechPan": self._audio["speechPan"], "appPan": self._audio["appPan"]})

    def audio_restore_balance(self) -> RuntimeResult:
        self._audio["speechPan"] = 0
        self._audio["appPan"] = 0
        self._save()
        return RuntimeResult(ok=True, message="Audio balance restored.")

    def audio_cycle_card(self) -> RuntimeResult:
        cards = list(self._audio.get("cards", ["default"]))
        idx = int(self._audio.get("cardIndex", 0))
        idx = (idx + 1) % max(1, len(cards))
        self._audio["cardIndex"] = idx
        self._save()
        return RuntimeResult(ok=True, message="Audio output card cycled.", payload={"activeCard": cards[idx], "index": idx})

