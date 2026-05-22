from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict

from .diagnostics import get_logger
from .engine import RuntimeResult

_logger = get_logger("spellforge.quick_capture")


@dataclass
class CaptureItem:
    capture_id: str
    text: str
    source_app: str
    window_id: str
    captured_at: str
    route: str = "inbox"


class QuickCaptureInbox:
    def __init__(self, storage_path: Path | str | None = None):
        self._items: Dict[str, CaptureItem] = {}
        self._counter = 0
        self._storage_path = Path(storage_path) if storage_path else None
        self._load()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _load(self) -> None:
        if self._storage_path is None or not self._storage_path.exists():
            return

        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except Exception:
            _logger.exception("Spellforge: loading quick capture inbox at %s failed", self._storage_path)
            return

        self._counter = int(payload.get("counter", 0))
        items = payload.get("items", {})
        if not isinstance(items, dict):
            return

        loaded: Dict[str, CaptureItem] = {}
        for cid, row in items.items():
            if not isinstance(row, dict):
                continue
            loaded[cid] = CaptureItem(
                capture_id=str(row.get("capture_id", cid)),
                text=str(row.get("text", "")),
                source_app=str(row.get("source_app", "unknown")),
                window_id=str(row.get("window_id", "")),
                captured_at=str(row.get("captured_at", self._now())),
                route=str(row.get("route", "inbox")),
            )

        self._items = loaded

    def _save(self) -> None:
        if self._storage_path is None:
            return

        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "counter": self._counter,
            "items": {
                cid: {
                    "capture_id": item.capture_id,
                    "text": item.text,
                    "source_app": item.source_app,
                    "window_id": item.window_id,
                    "captured_at": item.captured_at,
                    "route": item.route,
                }
                for cid, item in self._items.items()
            },
        }
        self._storage_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    def capture(self, text: str, *, source_app: str, window_id: str) -> RuntimeResult:
        value = text.strip()
        if not value:
            return RuntimeResult(ok=False, message="No text available to capture.")

        self._counter += 1
        cid = f"cap-{self._counter:04d}"
        item = CaptureItem(
            capture_id=cid,
            text=value,
            source_app=source_app.strip() or "unknown",
            window_id=window_id.strip() or "",
            captured_at=self._now(),
        )
        self._items[cid] = item
        self._save()
        return RuntimeResult(
            ok=True,
            message="Quick capture saved.",
            payload={
                "captureId": cid,
                "capturedLength": len(value),
                "sourceApp": item.source_app,
                "capturedAt": item.captured_at,
            },
        )

    def route(self, capture_id: str, target: str) -> RuntimeResult:
        cid = capture_id.strip()
        item = self._items.get(cid)
        if item is None:
            return RuntimeResult(ok=False, message="Capture item not found.")

        route = target.strip().lower()
        if route not in ("inbox", "notes", "clips", "drafts"):
            return RuntimeResult(ok=False, message="Route target must be inbox, notes, clips, or drafts.")

        previous_route = item.route
        item.route = route
        self._save()
        return RuntimeResult(
            ok=True,
            message="Quick capture routed.",
            payload={
                "captureId": cid,
                "target": route,
                "previousRoute": previous_route,
                "sourceApp": item.source_app,
            },
        )

    def list_items(self, route: str = "") -> RuntimeResult:
        filter_route = route.strip().lower()
        items = []
        for item in self._items.values():
            if filter_route and item.route != filter_route:
                continue
            items.append(
                {
                    "captureId": item.capture_id,
                    "text": item.text,
                    "sourceApp": item.source_app,
                    "windowId": item.window_id,
                    "capturedAt": item.captured_at,
                    "route": item.route,
                }
            )
        items.sort(key=lambda x: x["captureId"])
        return RuntimeResult(ok=True, message="Quick capture list ready.", payload={"items": items, "count": len(items)})
