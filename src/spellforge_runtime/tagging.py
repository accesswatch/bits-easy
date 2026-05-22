from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List

from .engine import RuntimeResult


@dataclass
class TaggedItem:
    path: str
    tagged_at: str


class TaggingSession:
    def __init__(self):
        self._tagged: Dict[str, TaggedItem] = {}

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _normalize_path(path: str) -> str:
        p = path.strip().strip('"').strip("'")
        if "\n" in p:
            p = p.splitlines()[0].strip()
        return p

    def tag(self, path: str) -> RuntimeResult:
        p = self._normalize_path(path)
        if not p:
            return RuntimeResult(ok=False, message="Path is required.")
        if p in self._tagged:
            return RuntimeResult(
                ok=True,
                message="File is already tagged.",
                payload={"path": p, "count": len(self._tagged), "alreadyTagged": True},
            )
        self._tagged[p] = TaggedItem(path=p, tagged_at=self._now())
        return RuntimeResult(ok=True, message="File tagged.", payload={"path": p, "count": len(self._tagged), "alreadyTagged": False})

    def untag(self, path: str) -> RuntimeResult:
        p = self._normalize_path(path)
        if p not in self._tagged:
            return RuntimeResult(ok=False, message="File is not tagged.")
        del self._tagged[p]
        return RuntimeResult(ok=True, message="File untagged.", payload={"path": p, "count": len(self._tagged)})

    def toggle(self, path: str) -> RuntimeResult:
        p = self._normalize_path(path)
        if not p:
            return RuntimeResult(ok=False, message="Path is required.")
        if p in self._tagged:
            out = self.untag(p)
            if out.ok and out.payload is not None:
                out.payload["toggledTo"] = "untagged"
            return out
        out = self.tag(p)
        if out.ok and out.payload is not None:
            out.payload["toggledTo"] = "tagged"
        return out

    def report(self) -> RuntimeResult:
        items = [
            {
                "index": idx + 1,
                "path": row.path,
                "taggedAt": row.tagged_at,
            }
            for idx, row in enumerate(self._tagged.values())
        ]
        return RuntimeResult(ok=True, message="Tagged file report ready.", payload={"items": items, "count": len(items)})

    def count(self) -> RuntimeResult:
        return RuntimeResult(ok=True, message="Tag count ready.", payload={"count": len(self._tagged)})

    def cancel(self) -> RuntimeResult:
        count = len(self._tagged)
        self._tagged.clear()
        return RuntimeResult(ok=True, message="Tag session cleared.", payload={"cleared": count})

    def batch_action(self, action: str, *, target: str = "") -> RuntimeResult:
        act = action.strip().lower()
        if act not in ("copy", "cut", "delete", "playlist-add"):
            return RuntimeResult(ok=False, message="Unsupported batch action.")
        items = [row.path for row in self._tagged.values()]
        if not items:
            return RuntimeResult(ok=False, message="No tagged files in current session.")
        if act in ("copy", "cut", "playlist-add") and not target.strip():
            return RuntimeResult(ok=False, message="Target is required for this batch action.")

        confirmation_required = act in ("cut", "delete") or len(items) >= 20
        safety_prompts: List[str] = []
        if act == "delete":
            safety_prompts.append("Confirm delete for all tagged files.")
        elif act == "cut":
            safety_prompts.append("Confirm move destination before cut operation.")
        elif act == "copy":
            safety_prompts.append("Confirm copy destination before bulk copy operation.")

        payload: Dict[str, object] = {
            "action": act,
            "count": len(items),
            "items": [{"path": p} for p in items],
            "confirmationRequired": confirmation_required,
            "safetyPrompts": safety_prompts,
        }
        if target.strip():
            payload["target"] = target.strip()
        return RuntimeResult(ok=True, message="Batch action prepared.", payload=payload)
