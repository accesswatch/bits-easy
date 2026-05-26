from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from .engine import RuntimeResult


@dataclass
class CalendarSyncEvent:
    title: str
    start_iso: str
    end_iso: str
    description: str = ""
    location: str = ""


class GoogleCalendarSync:
    def __init__(self, credentials_path: Path | str, token_path: Path | str, calendar_id: str = "primary"):
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.calendar_id = calendar_id

    @staticmethod
    def sample_event(title: str) -> CalendarSyncEvent:
        now = datetime.now(timezone.utc)
        later = now + timedelta(minutes=30)
        return CalendarSyncEvent(
            title=title,
            start_iso=now.isoformat(),
            end_iso=later.isoformat(),
        )

    def sync_events(self, events: List[CalendarSyncEvent], *, dry_run: bool = True) -> RuntimeResult:
        if not events:
            return RuntimeResult(ok=False, message="No calendar events to sync.")

        if dry_run:
            return RuntimeResult(
                ok=True,
                message="Google Calendar sync dry-run complete.",
                payload={
                    "calendarId": self.calendar_id,
                    "eventCount": len(events),
                    "mode": "dry-run",
                },
            )

        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
        except Exception:
            return RuntimeResult(
                ok=False,
                message=(
                    "Google Calendar client libraries are missing. "
                    "Install google-api-python-client, google-auth-oauthlib, and google-auth-httplib2."
                ),
                next_steps=[
                    "Install required Google API packages in the active Python environment.",
                    "Re-run with dryRun=false after installation.",
                ],
            )

        scopes = ["https://www.googleapis.com/auth/calendar.events"]
        creds = None
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    return RuntimeResult(
                        ok=False,
                        message="Google OAuth credentials file was not found.",
                        next_steps=[
                            "Create OAuth desktop credentials in Google Cloud Console.",
                            f"Save client secret JSON to {self.credentials_path}.",
                        ],
                    )
                flow = InstalledAppFlow.from_client_secrets_file(str(self.credentials_path), scopes)
                creds = flow.run_local_server(port=0)
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            self.token_path.write_text(creds.to_json(), encoding="utf-8")

        service = build("calendar", "v3", credentials=creds)
        created = []
        for event in events:
            body: Dict[str, Any] = {
                "summary": event.title,
                "description": event.description,
                "location": event.location,
                "start": {"dateTime": event.start_iso},
                "end": {"dateTime": event.end_iso},
            }
            resp = service.events().insert(calendarId=self.calendar_id, body=body).execute()
            created.append({"id": str(resp.get("id", "")), "htmlLink": str(resp.get("htmlLink", ""))})

        return RuntimeResult(
            ok=True,
            message="Google Calendar sync complete.",
            payload={
                "calendarId": self.calendar_id,
                "eventCount": len(created),
                "events": created,
                "mode": "live",
            },
        )
