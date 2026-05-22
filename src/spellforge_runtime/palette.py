from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from .config import RuntimeConfig


@dataclass
class PaletteItem:
    command_id: str
    name: str
    score: float


class PaletteEngine:
    def __init__(self, config: RuntimeConfig, history_path: Path | str):
        self.config = config
        self.history_path = Path(history_path)
        self._history = self._load_history()

    def _load_history(self) -> Dict[str, Dict[str, int]]:
        if not self.history_path.exists():
            return {}
        try:
            payload = json.loads(self.history_path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                return {
                    str(k): {
                        "count": int(v.get("count", 0)),
                        "last": int(v.get("last", 0)),
                    }
                    for k, v in payload.items()
                }
        except Exception:
            pass
        return {}

    def _save_history(self) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.write_text(json.dumps(self._history, indent=2), encoding="utf-8")

    def record_execution(self, command_id: str, tick: int) -> None:
        row = self._history.setdefault(command_id, {"count": 0, "last": 0})
        row["count"] += 1
        row["last"] = max(row["last"], int(tick))
        self._save_history()

    def _context_boost(self, app_id: str, command_id: str) -> float:
        app_l = (app_id or "").lower()
        if app_l in ("edge", "chrome", "firefox") and command_id.startswith("cmd.selection"):
            return 0.6
        if app_l == "outlook" and ("clip" in command_id or "capture" in command_id):
            return 0.5
        if app_l == "word" and command_id.startswith("cmd.selection"):
            return 0.7
        return 0.0

    def _query_score(self, query: str, command_id: str, name: str) -> float:
        if not query:
            return 0.1
        q = query.lower().strip()
        cid = command_id.lower()
        nm = (name or "").lower()

        if q == cid or q == nm:
            return 10.0
        if cid.startswith(q) or nm.startswith(q):
            return 7.0
        if q in cid:
            return 4.0
        if q in nm:
            return 3.0

        tokens = [t for t in q.split() if t]
        token_hits = sum(1 for t in tokens if t in cid or t in nm)
        if token_hits:
            return 1.5 + token_hits
        return -100.0

    def search(self, query: str, app_id: str, limit: int = 25) -> List[PaletteItem]:
        rows: List[PaletteItem] = []
        for command_id, meta in self.config.command_catalog.items():
            name = str(meta.get("name", command_id))
            score = self._query_score(query, command_id, name)
            if score < 0:
                continue

            hist = self._history.get(command_id, {"count": 0, "last": 0})
            score += min(2.0, 0.2 * hist["count"])
            score += min(1.5, 0.0001 * hist["last"])
            score += self._context_boost(app_id, command_id)
            rows.append(PaletteItem(command_id=command_id, name=name, score=score))

        rows.sort(key=lambda r: (-r.score, r.command_id))
        return rows[:limit]

    def top_recent(self, limit: int = 10) -> List[Tuple[str, int]]:
        rows = sorted(
            ((cid, data.get("last", 0)) for cid, data in self._history.items()),
            key=lambda item: item[1],
            reverse=True,
        )
        return rows[:limit]
