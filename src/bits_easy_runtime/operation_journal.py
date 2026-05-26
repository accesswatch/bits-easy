from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List

from .diagnostics import get_logger
from .engine import RuntimeResult

_logger = get_logger("bits_easy.operation_journal")


@dataclass
class JournalEntry:
    entry_id: str
    app_id: str
    command_id: str
    action_type: str
    summary: str
    reversible: bool
    created_at: str
    rollback_action: Dict[str, Any] | None = None
    rollback_status: str = "none"
    rolled_back_at: str = ""


class OperationJournal:
    def __init__(self, storage_path: Path | str | None = None):
        self._entries: List[JournalEntry] = []
        self._counter = 0
        self._storage_path = Path(storage_path) if storage_path else None
        self._load()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _save(self) -> None:
        if self._storage_path is None:
            return

        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "counter": self._counter,
            "entries": [
                {
                    "entry_id": e.entry_id,
                    "app_id": e.app_id,
                    "command_id": e.command_id,
                    "action_type": e.action_type,
                    "summary": e.summary,
                    "reversible": e.reversible,
                    "created_at": e.created_at,
                    "rollback_action": e.rollback_action,
                    "rollback_status": e.rollback_status,
                    "rolled_back_at": e.rolled_back_at,
                }
                for e in self._entries
            ],
        }
        self._storage_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if self._storage_path is None or not self._storage_path.exists():
            return

        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except Exception:
            _logger.exception("BITS-EASY: loading operation journal at %s failed", self._storage_path)
            return

        self._counter = int(payload.get("counter", 0))
        entries = payload.get("entries", [])
        if not isinstance(entries, list):
            return

        rows: List[JournalEntry] = []
        for row in entries:
            if not isinstance(row, dict):
                continue
            rollback_action = row.get("rollback_action")
            rows.append(
                JournalEntry(
                    entry_id=str(row.get("entry_id", "")),
                    app_id=str(row.get("app_id", "")),
                    command_id=str(row.get("command_id", "")),
                    action_type=str(row.get("action_type", "")),
                    summary=str(row.get("summary", "")),
                    reversible=bool(row.get("reversible", False)),
                    created_at=str(row.get("created_at", self._now())),
                    rollback_action=rollback_action if isinstance(rollback_action, dict) else None,
                    rollback_status=str(row.get("rollback_status", "none")),
                    rolled_back_at=str(row.get("rolled_back_at", "")),
                )
            )
        self._entries = rows

    def record(
        self,
        *,
        app_id: str,
        command_id: str,
        action_type: str,
        summary: str,
        reversible: bool,
        rollback_action: Dict[str, Any] | None = None,
    ) -> RuntimeResult:
        self._counter += 1
        eid = f"jrnl-{self._counter:05d}"
        rollback_action_value = rollback_action if isinstance(rollback_action, dict) else None
        row = JournalEntry(
            entry_id=eid,
            app_id=app_id,
            command_id=command_id,
            action_type=action_type,
            summary=summary.strip() or command_id,
            reversible=bool(reversible),
            created_at=self._now(),
            rollback_action=rollback_action_value,
        )
        self._entries.append(row)
        self._save()
        return RuntimeResult(ok=True, message="Journal entry recorded.", payload={"entryId": eid})

    def list_entries(self, *, app_id: str = "", action_type: str = "") -> RuntimeResult:
        app_filter = app_id.strip().lower()
        action_filter = action_type.strip().lower()
        rows = []
        for e in self._entries:
            if app_filter and e.app_id.lower() != app_filter:
                continue
            if action_filter and e.action_type.lower() != action_filter:
                continue
            rows.append(
                {
                    "entryId": e.entry_id,
                    "appId": e.app_id,
                    "commandId": e.command_id,
                    "actionType": e.action_type,
                    "summary": e.summary,
                    "reversible": e.reversible,
                    "createdAt": e.created_at,
                    "rollbackStatus": e.rollback_status,
                }
            )
        return RuntimeResult(ok=True, message="Journal entries ready.", payload={"items": rows, "count": len(rows)})

    def rollback(self, entry_id: str) -> RuntimeResult:
        eid = entry_id.strip()
        entry = next((e for e in self._entries if e.entry_id == eid), None)
        if entry is None:
            return RuntimeResult(ok=False, message="Journal entry not found.")
        if not entry.reversible:
            return RuntimeResult(ok=False, message="Entry is not reversible.", next_steps=["Use manual recovery flow."])
        if entry.rollback_status == "applied":
            return RuntimeResult(ok=False, message="Entry already rolled back.")
        if not entry.rollback_action:
            return RuntimeResult(ok=False, message="No rollback handler is registered for this entry.")
        return RuntimeResult(
            ok=True,
            message="Rollback handler ready.",
            payload={
                "entryId": eid,
                "commandId": entry.command_id,
                "appId": entry.app_id,
                "rollbackAction": entry.rollback_action,
            },
        )

    def trend_report(self, *, window_days: int = 30) -> RuntimeResult:
        days = max(1, int(window_days))
        by_command: Dict[str, int] = {}
        by_app: Dict[str, int] = {}
        by_action: Dict[str, int] = {}
        rollback_status: Dict[str, int] = {"none": 0, "applied": 0, "failed": 0}
        reversible = 0
        for e in self._entries:
            by_command[e.command_id] = by_command.get(e.command_id, 0) + 1
            by_app[e.app_id] = by_app.get(e.app_id, 0) + 1
            by_action[e.action_type] = by_action.get(e.action_type, 0) + 1
            if e.rollback_status in rollback_status:
                rollback_status[e.rollback_status] += 1
            else:
                rollback_status[e.rollback_status] = rollback_status.get(e.rollback_status, 0) + 1
            if e.reversible:
                reversible += 1
        top_commands = sorted(by_command.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
        top_apps = sorted(by_app.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
        top_actions = sorted(by_action.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
        return RuntimeResult(
            ok=True,
            message="Journal trend report ready.",
            payload={
                "windowDays": days,
                "totalEntries": len(self._entries),
                "reversibleCount": reversible,
                "reversibleRate": (float(reversible) / float(len(self._entries))) if self._entries else 0.0,
                "topCommands": [{"commandId": k, "count": v} for k, v in top_commands],
                "topApps": [{"appId": k, "count": v} for k, v in top_apps],
                "topActionTypes": [{"actionType": k, "count": v} for k, v in top_actions],
                "rollbackStatus": rollback_status,
            },
        )

    def mark_rollback_applied(self, entry_id: str, *, success: bool) -> RuntimeResult:
        eid = entry_id.strip()
        entry = next((e for e in self._entries if e.entry_id == eid), None)
        if entry is None:
            return RuntimeResult(ok=False, message="Journal entry not found.")

        entry.rollback_status = "applied" if success else "failed"
        entry.rolled_back_at = self._now()
        self._save()
        return RuntimeResult(
            ok=True,
            message="Rollback status updated.",
            payload={"entryId": entry.entry_id, "status": entry.rollback_status},
        )

