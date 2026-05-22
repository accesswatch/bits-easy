from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, List, Optional

from .engine import RuntimeResult
from .google_calendar_sync import CalendarSyncEvent, GoogleCalendarSync


@dataclass
class TaskRecord:
    task_id: str
    title: str
    due_at: str
    status: str
    category: str
    priority: str


class TaskIcsBridge:
    def __init__(self, storage_path: Path | str | None = None, calendar_sync: Optional[GoogleCalendarSync] = None):
        self._storage_path = Path(storage_path) if storage_path else None
        self._calendar_sync = calendar_sync
        self._counter = 0
        self._tasks: Dict[str, TaskRecord] = {}
        self._load()

    @staticmethod
    def _utc_now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _save(self) -> None:
        if self._storage_path is None:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "counter": self._counter,
            "tasks": {
                tid: {
                    "task_id": t.task_id,
                    "title": t.title,
                    "due_at": t.due_at,
                    "status": t.status,
                    "category": t.category,
                    "priority": t.priority,
                }
                for tid, t in self._tasks.items()
            },
        }
        self._storage_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if self._storage_path is None or not self._storage_path.exists():
            return
        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except Exception:
            return

        self._counter = int(payload.get("counter", 0))
        rows = payload.get("tasks", {})
        if not isinstance(rows, dict):
            return
        for tid, row in rows.items():
            if not isinstance(row, dict):
                continue
            self._tasks[tid] = TaskRecord(
                task_id=str(row.get("task_id", tid)),
                title=str(row.get("title", "")),
                due_at=str(row.get("due_at", self._utc_now_iso())),
                status=str(row.get("status", "open")),
                category=str(row.get("category", "general")),
                priority=str(row.get("priority", "normal")),
            )

    def create_task(self, title: str, due_at_iso: str, category: str = "general", priority: str = "normal") -> RuntimeResult:
        name = title.strip()
        if not name:
            return RuntimeResult(ok=False, message="Task title is required.")
        try:
            due = datetime.fromisoformat(due_at_iso)
            if due.tzinfo is None:
                due = due.replace(tzinfo=timezone.utc)
            due_iso = due.astimezone(timezone.utc).isoformat()
        except Exception:
            return RuntimeResult(ok=False, message="Task due date must be a valid ISO datetime.")

        self._counter += 1
        tid = f"tsk-{self._counter:04d}"
        self._tasks[tid] = TaskRecord(
            task_id=tid,
            title=name,
            due_at=due_iso,
            status="open",
            category=category.strip() or "general",
            priority=priority.strip() or "normal",
        )
        self._save()
        return RuntimeResult(ok=True, message="Task created.", payload={"taskId": tid, "dueAt": due_iso})

    def complete_task(self, task_id: str) -> RuntimeResult:
        tid = task_id.strip()
        task = self._tasks.get(tid)
        if task is None:
            return RuntimeResult(ok=False, message="Task not found.")
        task.status = "done"
        self._save()
        return RuntimeResult(ok=True, message="Task completed.", payload={"taskId": tid})

    def list_tasks(self, status: str = "", category: str = "", priority: str = "") -> RuntimeResult:
        st = status.strip().lower()
        cat = category.strip().lower()
        pri = priority.strip().lower()

        items = []
        for t in self._tasks.values():
            if st and t.status.lower() != st:
                continue
            if cat and t.category.lower() != cat:
                continue
            if pri and t.priority.lower() != pri:
                continue
            items.append(
                {
                    "taskId": t.task_id,
                    "title": t.title,
                    "dueAt": t.due_at,
                    "status": t.status,
                    "category": t.category,
                    "priority": t.priority,
                }
            )

        items.sort(key=lambda row: row["dueAt"])
        return RuntimeResult(ok=True, message="Task list ready.", payload={"items": items, "count": len(items)})

    def export_ics(self, out_path: Path | str) -> RuntimeResult:
        path = Path(out_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Spellforge//Tasks Bridge//EN",
        ]

        for task in sorted(self._tasks.values(), key=lambda x: x.due_at):
            due = datetime.fromisoformat(task.due_at)
            stamp = due.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            lines.extend(
                [
                    "BEGIN:VTODO",
                    f"UID:{task.task_id}@spellforge",
                    f"DTSTAMP:{stamp}",
                    f"DUE:{stamp}",
                    f"SUMMARY:{task.title}",
                    f"STATUS:{'COMPLETED' if task.status == 'done' else 'NEEDS-ACTION'}",
                    f"CATEGORIES:{task.category}",
                    "END:VTODO",
                ]
            )

        lines.append("END:VCALENDAR")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return RuntimeResult(ok=True, message="ICS export complete.", payload={"path": str(path), "taskCount": len(self._tasks)})

    def sync_to_google_calendar(self, *, dry_run: bool = True) -> RuntimeResult:
        if self._calendar_sync is None:
            return RuntimeResult(ok=False, message="Google Calendar sync is not configured.")

        events = []
        for task in self._tasks.values():
            if task.status == "done":
                continue
            due = datetime.fromisoformat(task.due_at)
            start = due.astimezone(timezone.utc)
            end = start
            events.append(
                CalendarSyncEvent(
                    title=f"Task: {task.title}",
                    start_iso=start.isoformat(),
                    end_iso=end.isoformat(),
                    description=f"Category: {task.category}; Priority: {task.priority}",
                )
            )

        return self._calendar_sync.sync_events(events, dry_run=dry_run)
