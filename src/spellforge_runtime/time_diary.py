from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from typing import Dict, List

from .engine import RuntimeResult


@dataclass
class Appointment:
    appointment_id: str
    title: str
    starts_at: str
    notes: str


class TimeDiaryService:
    def __init__(self, storage_path: Path | str | None = None):
        self._storage_path = Path(storage_path) if storage_path else None
        self._appointments: Dict[str, Appointment] = {}
        self._counter = 0

        self._stopwatch_running = False
        self._stopwatch_started_at: datetime | None = None
        self._stopwatch_elapsed = timedelta(0)
        self._precision = 1

        self._countdown_target: datetime | None = None
        self._alarm_target: datetime | None = None

        self._monitor_enabled = False
        self._monitor_braille = False

        self._load()

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)

    def _save(self) -> None:
        if self._storage_path is None:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "counter": self._counter,
            "appointments": {
                aid: {
                    "appointment_id": appt.appointment_id,
                    "title": appt.title,
                    "starts_at": appt.starts_at,
                    "notes": appt.notes,
                }
                for aid, appt in self._appointments.items()
            },
            "precision": self._precision,
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
        self._precision = int(payload.get("precision", 1))
        rows = payload.get("appointments", {})
        if not isinstance(rows, dict):
            return
        for aid, row in rows.items():
            if not isinstance(row, dict):
                continue
            self._appointments[aid] = Appointment(
                appointment_id=str(row.get("appointment_id", aid)),
                title=str(row.get("title", "")),
                starts_at=str(row.get("starts_at", "")),
                notes=str(row.get("notes", "")),
            )

    def speak_time(self, include_seconds: bool = False) -> RuntimeResult:
        now = self._now().astimezone()
        fmt = "%H:%M:%S" if include_seconds else "%H:%M"
        return RuntimeResult(ok=True, message="Current time ready.", payload={"text": now.strftime(fmt)})

    def insert_time(self, include_seconds: bool = False) -> RuntimeResult:
        now = self._now().astimezone()
        fmt = "%H:%M:%S" if include_seconds else "%H:%M"
        return RuntimeResult(ok=True, message="Insert time payload ready.", payload={"insertText": now.strftime(fmt)})

    def insert_date(self) -> RuntimeResult:
        now = self._now().astimezone()
        return RuntimeResult(ok=True, message="Insert date payload ready.", payload={"insertText": now.strftime("%Y-%m-%d")})

    def stopwatch_start(self) -> RuntimeResult:
        if self._stopwatch_running:
            return RuntimeResult(ok=True, message="Stopwatch already running.")
        self._stopwatch_running = True
        self._stopwatch_started_at = self._now()
        return RuntimeResult(ok=True, message="Stopwatch started.")

    def stopwatch_stop(self) -> RuntimeResult:
        if not self._stopwatch_running:
            return RuntimeResult(ok=True, message="Stopwatch already stopped.")
        assert self._stopwatch_started_at is not None
        self._stopwatch_elapsed += self._now() - self._stopwatch_started_at
        self._stopwatch_started_at = None
        self._stopwatch_running = False
        return RuntimeResult(ok=True, message="Stopwatch stopped.", payload={"elapsedSeconds": self._stopwatch_elapsed.total_seconds()})

    def stopwatch_clear(self) -> RuntimeResult:
        self._stopwatch_running = False
        self._stopwatch_started_at = None
        self._stopwatch_elapsed = timedelta(0)
        return RuntimeResult(ok=True, message="Stopwatch cleared.")

    def stopwatch_set_precision(self, decimals: int) -> RuntimeResult:
        self._precision = max(0, min(3, int(decimals)))
        self._save()
        return RuntimeResult(ok=True, message="Stopwatch precision updated.", payload={"decimals": self._precision})

    def stopwatch_elapsed(self) -> RuntimeResult:
        elapsed = self._stopwatch_elapsed
        if self._stopwatch_running and self._stopwatch_started_at is not None:
            elapsed += self._now() - self._stopwatch_started_at
        val = round(elapsed.total_seconds(), self._precision)
        return RuntimeResult(ok=True, message="Stopwatch elapsed ready.", payload={"elapsedSeconds": val, "decimals": self._precision})

    def countdown_start(self, minutes: int) -> RuntimeResult:
        mins = max(1, int(minutes))
        self._countdown_target = self._now() + timedelta(minutes=mins)
        return RuntimeResult(ok=True, message="Countdown started.", payload={"minutes": mins})

    def countdown_status(self) -> RuntimeResult:
        if self._countdown_target is None:
            return RuntimeResult(ok=False, message="Countdown is not running.")
        remaining = max(0, int((self._countdown_target - self._now()).total_seconds()))
        return RuntimeResult(ok=True, message="Countdown status ready.", payload={"remainingSeconds": remaining, "triggered": remaining == 0})

    def countdown_stop(self) -> RuntimeResult:
        self._countdown_target = None
        return RuntimeResult(ok=True, message="Countdown stopped.")

    def alarm_set(self, at_iso: str) -> RuntimeResult:
        try:
            when = datetime.fromisoformat(at_iso)
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            self._alarm_target = when.astimezone(timezone.utc)
            return RuntimeResult(ok=True, message="Alarm set.", payload={"at": self._alarm_target.isoformat()})
        except Exception:
            return RuntimeResult(ok=False, message="Alarm time must be a valid ISO datetime.")

    def alarm_cancel(self) -> RuntimeResult:
        self._alarm_target = None
        return RuntimeResult(ok=True, message="Alarm cancelled.")

    def alarm_status(self) -> RuntimeResult:
        if self._alarm_target is None:
            return RuntimeResult(ok=False, message="Alarm is not set.")
        remaining = int((self._alarm_target - self._now()).total_seconds())
        return RuntimeResult(ok=True, message="Alarm status ready.", payload={"at": self._alarm_target.isoformat(), "remainingSeconds": max(0, remaining), "triggered": remaining <= 0})

    def monitor_start(self, braille_mode: bool = False) -> RuntimeResult:
        self._monitor_enabled = True
        self._monitor_braille = bool(braille_mode)
        return RuntimeResult(ok=True, message="Time monitor started.", payload={"brailleMode": self._monitor_braille})

    def monitor_stop(self) -> RuntimeResult:
        self._monitor_enabled = False
        self._monitor_braille = False
        return RuntimeResult(ok=True, message="Time monitor stopped.")

    def monitor_status(self) -> RuntimeResult:
        return RuntimeResult(ok=True, message="Time monitor status ready.", payload={"enabled": self._monitor_enabled, "brailleMode": self._monitor_braille})

    def appointment_create(self, title: str, starts_at_iso: str, notes: str = "") -> RuntimeResult:
        name = title.strip()
        if not name:
            return RuntimeResult(ok=False, message="Appointment title is required.")
        try:
            when = datetime.fromisoformat(starts_at_iso)
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            starts_at = when.astimezone(timezone.utc).isoformat()
        except Exception:
            return RuntimeResult(ok=False, message="Appointment datetime must be a valid ISO datetime.")

        self._counter += 1
        aid = f"apt-{self._counter:04d}"
        self._appointments[aid] = Appointment(appointment_id=aid, title=name, starts_at=starts_at, notes=notes.strip())
        self._save()
        return RuntimeResult(ok=True, message="Appointment created.", payload={"appointmentId": aid, "startsAt": starts_at})

    def appointment_list_month(self, year: int, month: int) -> RuntimeResult:
        y = int(year)
        m = int(month)
        rows = []
        for appt in self._appointments.values():
            try:
                dt = datetime.fromisoformat(appt.starts_at)
            except Exception:
                continue
            if dt.year == y and dt.month == m:
                rows.append({"appointmentId": appt.appointment_id, "title": appt.title, "startsAt": appt.starts_at, "notes": appt.notes})
        rows.sort(key=lambda x: x["startsAt"])
        return RuntimeResult(ok=True, message="Monthly appointments ready.", payload={"items": rows, "count": len(rows)})

    def day_of_week(self, date_iso: str) -> RuntimeResult:
        try:
            dt = datetime.fromisoformat(date_iso)
        except Exception:
            return RuntimeResult(ok=False, message="Date must be ISO format YYYY-MM-DD.")
        return RuntimeResult(ok=True, message="Day lookup ready.", payload={"date": date_iso, "day": dt.strftime("%A")})

    def date_add_days(self, date_iso: str, days: int) -> RuntimeResult:
        try:
            dt = datetime.fromisoformat(date_iso)
        except Exception:
            return RuntimeResult(ok=False, message="Date must be ISO format YYYY-MM-DD.")
        out = dt + timedelta(days=int(days))
        return RuntimeResult(ok=True, message="Date math ready.", payload={"inputDate": date_iso, "days": int(days), "resultDate": out.strftime("%Y-%m-%d")})
