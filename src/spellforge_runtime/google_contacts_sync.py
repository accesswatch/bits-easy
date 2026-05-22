from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from .engine import RuntimeResult


@dataclass
class GoogleContact:
    given_name: str
    family_name: str
    email: str
    phone: str = ""


class GoogleContactsSync:
    def __init__(self, credentials_path: Path | str, token_path: Path | str):
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)

    def sync_contacts(self, contacts: List[GoogleContact], *, dry_run: bool = True) -> RuntimeResult:
        if not contacts:
            return RuntimeResult(ok=False, message="No contacts to sync.")

        if dry_run:
            return RuntimeResult(ok=True, message="Google Contacts sync dry-run complete.", payload={"contactCount": len(contacts), "mode": "dry-run"})

        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
        except Exception:
            return RuntimeResult(
                ok=False,
                message=(
                    "Google client libraries are missing. Install google-api-python-client, "
                    "google-auth-oauthlib, and google-auth-httplib2."
                ),
                next_steps=[
                    "Install required Google API packages in the active Python environment.",
                    "Re-run with dryRun=false after installation.",
                ],
            )

        scopes = ["https://www.googleapis.com/auth/contacts"]
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

        service = build("people", "v1", credentials=creds)
        created: List[Dict[str, Any]] = []
        for c in contacts:
            body: Dict[str, Any] = {
                "names": [{"givenName": c.given_name, "familyName": c.family_name}],
                "emailAddresses": [{"value": c.email}],
            }
            if c.phone:
                body["phoneNumbers"] = [{"value": c.phone}]

            resp = service.people().createContact(body=body).execute()
            created.append({"resourceName": str(resp.get("resourceName", ""))})

        return RuntimeResult(ok=True, message="Google Contacts sync complete.", payload={"contactCount": len(created), "mode": "live", "items": created})
