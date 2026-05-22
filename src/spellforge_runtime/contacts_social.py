from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Dict, List

from .diagnostics import get_logger
from .engine import RuntimeResult
from .google_contacts_sync import GoogleContact, GoogleContactsSync

_logger = get_logger("spellforge.contacts_social")


@dataclass
class Contact:
    contact_id: str
    name: str
    email: str
    phone: str


class ContactsSocialService:
    def __init__(self, storage_path: Path | str | None = None, google_sync: GoogleContactsSync | None = None):
        self._storage_path = Path(storage_path) if storage_path else None
        self._google_sync = google_sync
        self._counter = 0
        self._contacts: Dict[str, Contact] = {}
        self._nicknames: Dict[str, str] = {}
        self._notification_prefs: Dict[str, Dict[str, bool]] = {}
        self._load()

    def _save(self) -> None:
        if self._storage_path is None:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "counter": self._counter,
            "contacts": {
                cid: {"contact_id": c.contact_id, "name": c.name, "email": c.email, "phone": c.phone}
                for cid, c in self._contacts.items()
            },
            "nicknames": self._nicknames,
            "notificationPrefs": self._notification_prefs,
        }
        self._storage_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if self._storage_path is None or not self._storage_path.exists():
            return
        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except Exception:
            _logger.exception("Spellforge: loading contacts at %s failed", self._storage_path)
            return

        self._counter = int(payload.get("counter", 0))
        rows = payload.get("contacts", {})
        if isinstance(rows, dict):
            for cid, row in rows.items():
                if not isinstance(row, dict):
                    continue
                self._contacts[cid] = Contact(
                    contact_id=str(row.get("contact_id", cid)),
                    name=str(row.get("name", "")),
                    email=str(row.get("email", "")),
                    phone=str(row.get("phone", "")),
                )

        nick = payload.get("nicknames", {})
        if isinstance(nick, dict):
            self._nicknames = {str(k): str(v) for k, v in nick.items()}

        prefs = payload.get("notificationPrefs", {})
        if isinstance(prefs, dict):
            cleaned: Dict[str, Dict[str, bool]] = {}
            for channel, value in prefs.items():
                if not isinstance(value, dict):
                    continue
                cleaned[str(channel)] = {str(k): bool(v) for k, v in value.items()}
            self._notification_prefs = cleaned

    def create_contact(self, name: str, email: str, phone: str = "") -> RuntimeResult:
        nm = name.strip()
        em = email.strip()
        if not nm or not em:
            return RuntimeResult(ok=False, message="Contact name and email are required.")

        self._counter += 1
        cid = f"cnt-{self._counter:04d}"
        self._contacts[cid] = Contact(contact_id=cid, name=nm, email=em, phone=phone.strip())
        self._save()
        return RuntimeResult(ok=True, message="Contact created.", payload={"contactId": cid})

    def search_contacts(self, query: str) -> RuntimeResult:
        q = query.strip().lower()
        items = []
        for c in self._contacts.values():
            blob = f"{c.name} {c.email} {c.phone}".lower()
            if q and q not in blob:
                continue
            items.append({"contactId": c.contact_id, "name": c.name, "email": c.email, "phone": c.phone})
        return RuntimeResult(ok=True, message="Contacts search ready.", payload={"items": items, "count": len(items)})

    def insert_field(self, contact_id: str, field: str) -> RuntimeResult:
        c = self._contacts.get(contact_id.strip())
        if c is None:
            return RuntimeResult(ok=False, message="Contact not found.")

        key = field.strip().lower()
        mapping = {"name": c.name, "email": c.email, "phone": c.phone}
        if key not in mapping:
            return RuntimeResult(ok=False, message="Field must be name, email, or phone.")
        return RuntimeResult(ok=True, message="Contact insertion payload ready.", payload={"insertText": mapping[key], "field": key})

    def copy_field(self, contact_id: str, field: str) -> RuntimeResult:
        inserted = self.insert_field(contact_id, field)
        if not inserted.ok:
            return inserted
        payload = inserted.payload or {}
        return RuntimeResult(ok=True, message="Contact field copied.", payload={"clipboardText": payload.get("insertText", ""), "field": payload.get("field", "")})

    def sync_google_contacts(self, *, dry_run: bool = True) -> RuntimeResult:
        if self._google_sync is None:
            return RuntimeResult(ok=False, message="Google Contacts sync is not configured.")

        contacts = []
        for c in self._contacts.values():
            parts = c.name.split(" ", 1)
            given = parts[0]
            family = parts[1] if len(parts) > 1 else ""
            contacts.append(GoogleContact(given_name=given, family_name=family, email=c.email, phone=c.phone))

        return self._google_sync.sync_contacts(contacts, dry_run=dry_run)

    def mail_extract_sender(self, sender_name: str, sender_email: str) -> RuntimeResult:
        return RuntimeResult(ok=True, message="Sender extracted.", payload={"name": sender_name.strip(), "email": sender_email.strip()})

    def mail_attachment_actions(self, attachments: List[str], action: str) -> RuntimeResult:
        act = action.strip().lower()
        if act not in ("list", "copy-names", "save-all"):
            return RuntimeResult(ok=False, message="Action must be list, copy-names, or save-all.")
        rows = [str(x) for x in attachments]
        return RuntimeResult(ok=True, message="Attachment action ready.", payload={"action": act, "items": rows, "count": len(rows)})

    def whatsapp_recent(self, chat_id: str, messages: List[str]) -> RuntimeResult:
        latest = messages[-1] if messages else ""
        return RuntimeResult(ok=True, message="WhatsApp recent message ready.", payload={"chatId": chat_id, "latest": latest})

    def whatsapp_voice_control(self, mode: str) -> RuntimeResult:
        m = mode.strip().lower()
        if m not in ("record", "pause", "send", "cancel"):
            return RuntimeResult(ok=False, message="Voice mode must be record, pause, send, or cancel.")
        return RuntimeResult(ok=True, message="WhatsApp voice control executed.", payload={"mode": m})

    def x_timeline(self, items: List[str], cursor: int = 0) -> RuntimeResult:
        if not items:
            return RuntimeResult(ok=False, message="Timeline is empty.")
        idx = max(0, min(len(items) - 1, int(cursor)))
        return RuntimeResult(ok=True, message="X timeline item ready.", payload={"cursor": idx, "item": items[idx], "total": len(items)})

    def social_orbit_summary(self, account_items: Dict[str, List[str]]) -> RuntimeResult:
        rows = []
        for account, items in account_items.items():
            rows.append({"account": account, "count": len(items), "latest": items[-1] if items else ""})
        rows.sort(key=lambda x: x["account"])
        return RuntimeResult(ok=True, message="Social Orbit summary ready.", payload={"items": rows, "count": len(rows)})

    def nickname_upsert(self, source: str, nickname: str) -> RuntimeResult:
        src = source.strip()
        nick = nickname.strip()
        if not src or not nick:
            return RuntimeResult(ok=False, message="Source and nickname are required.")
        self._nicknames[src] = nick
        self._save()
        return RuntimeResult(ok=True, message="Nickname saved.", payload={"source": src, "nickname": nick})

    def nickname_replace(self, text: str) -> RuntimeResult:
        out = text
        applied = []
        for src, nick in self._nicknames.items():
            if src in out:
                out = out.replace(src, nick)
                applied.append({"source": src, "nickname": nick})
        return RuntimeResult(ok=True, message="Nickname replacement ready.", payload={"text": out, "applied": applied})

    def notification_set(self, channel: str, *, enabled: bool, mentions_only: bool = False) -> RuntimeResult:
        ch = channel.strip().lower()
        if not ch:
            return RuntimeResult(ok=False, message="Channel is required.")
        self._notification_prefs[ch] = {"enabled": bool(enabled), "mentionsOnly": bool(mentions_only)}
        self._save()
        return RuntimeResult(ok=True, message="Notification preference updated.", payload={"channel": ch, "settings": self._notification_prefs[ch]})
