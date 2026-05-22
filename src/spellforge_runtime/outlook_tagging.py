from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .engine import RuntimeResult


@dataclass
class OutlookMessageTag:
    message_id: str
    sender: str
    subject: str


class OutlookTaggingSession:
    def __init__(self):
        self._tagged: Dict[str, OutlookMessageTag] = {}

    def tag_message(self, message_id: str, sender: str, subject: str) -> RuntimeResult:
        mid = message_id.strip()
        if not mid:
            return RuntimeResult(ok=False, message="messageId is required.")
        self._tagged[mid] = OutlookMessageTag(
            message_id=mid,
            sender=sender.strip() or "unknown",
            subject=subject.strip() or "(no subject)",
        )
        return RuntimeResult(ok=True, message="Outlook message tagged.", payload={"messageId": mid, "count": len(self._tagged)})

    def untag_message(self, message_id: str) -> RuntimeResult:
        mid = message_id.strip()
        if mid not in self._tagged:
            return RuntimeResult(ok=False, message="Message is not tagged.")
        del self._tagged[mid]
        return RuntimeResult(ok=True, message="Outlook message untagged.", payload={"messageId": mid, "count": len(self._tagged)})

    def report(self) -> RuntimeResult:
        items = [
            {
                "messageId": row.message_id,
                "sender": row.sender,
                "subject": row.subject,
            }
            for row in sorted(self._tagged.values(), key=lambda r: (r.sender.lower(), r.subject.lower(), r.message_id))
        ]
        return RuntimeResult(ok=True, message="Outlook tagged message report ready.", payload={"items": items, "count": len(items)})

    def cancel(self) -> RuntimeResult:
        count = len(self._tagged)
        self._tagged.clear()
        return RuntimeResult(ok=True, message="Outlook tagging session cleared.", payload={"cleared": count})

    def batch_action(self, action: str, *, folder: str = "") -> RuntimeResult:
        act = action.strip().lower()
        if act not in ("move", "copy", "delete"):
            return RuntimeResult(ok=False, message="Unsupported Outlook batch action.")

        items = [
            {
                "messageId": row.message_id,
                "sender": row.sender,
                "subject": row.subject,
            }
            for row in self._tagged.values()
        ]
        if not items:
            return RuntimeResult(ok=False, message="No tagged Outlook messages.")

        if act in ("move", "copy") and not folder.strip():
            return RuntimeResult(ok=False, message="Target folder is required.")

        confirmation_required = act == "delete" or len(items) >= 15
        safety_prompts: List[str] = []
        if act == "delete":
            safety_prompts.append("Confirm permanent delete of tagged messages.")
        elif act == "move":
            safety_prompts.append("Confirm destination folder before move.")
        elif act == "copy":
            safety_prompts.append("Confirm destination folder before copy.")

        payload = {
            "action": act,
            "count": len(items),
            "items": items,
            "confirmationRequired": confirmation_required,
            "safetyPrompts": safety_prompts,
        }
        if folder.strip():
            payload["folder"] = folder.strip()

        return RuntimeResult(ok=True, message="Outlook batch action prepared.", payload=payload)
