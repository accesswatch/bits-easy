from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set

from .engine import RuntimeResult


@dataclass
class TaggedItem:
    path: str


class TaggingSession:
    def __init__(self):
        self._tagged: Set[str] = set()

    def tag(self, path: str) -> RuntimeResult:
        p = path.strip()
        if not p:
            return RuntimeResult(ok=False, message="Path is required.")
        self._tagged.add(p)
        return RuntimeResult(ok=True, message="File tagged.", payload={"path": p, "count": len(self._tagged)})

    def untag(self, path: str) -> RuntimeResult:
        p = path.strip()
        if p not in self._tagged:
            return RuntimeResult(ok=False, message="File is not tagged.")
        self._tagged.remove(p)
        return RuntimeResult(ok=True, message="File untagged.", payload={"path": p, "count": len(self._tagged)})

    def report(self) -> RuntimeResult:
        items = [{"path": p} for p in sorted(self._tagged)]
        return RuntimeResult(ok=True, message="Tagged file report ready.", payload={"items": items})

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
        items = sorted(self._tagged)
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
