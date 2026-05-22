from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .engine import RuntimeResult, SpellforgeRuntime


@dataclass
class SlotView:
    slot: int
    empty: bool
    protected: bool
    source_app: str
    length: int
    preview: str


class PocketClipsStudio:
    def __init__(self, runtime: SpellforgeRuntime):
        self.runtime = runtime

    def list_slots(self, *, source_app: str = "", only_protected: Optional[bool] = None, sort_by: str = "slot") -> List[SlotView]:
        rows: List[SlotView] = []
        for slot in range(1, 13):
            desc = self.runtime.describe_slot(slot)
            payload = desc.payload or {}
            row = SlotView(
                slot=slot,
                empty=bool(payload.get("empty", True)),
                protected=bool(payload.get("protected", False)),
                source_app=str(payload.get("sourceApp", "")),
                length=int(payload.get("length", 0)),
                preview=str(payload.get("preview", "")),
            )
            rows.append(row)

        if source_app:
            rows = [r for r in rows if r.source_app.lower() == source_app.lower()]
        if only_protected is not None:
            rows = [r for r in rows if r.protected == only_protected]

        if sort_by == "recency":
            rows.sort(key=lambda r: (r.empty, -r.length, r.slot))
        elif sort_by == "size":
            rows.sort(key=lambda r: (-r.length, r.slot))
        else:
            rows.sort(key=lambda r: r.slot)
        return rows

    def compare_slots(self, slot_a: int, slot_b: int) -> RuntimeResult:
        a = self.runtime.paste_from_slot(slot_a)
        b = self.runtime.paste_from_slot(slot_b)
        if not a.ok or not b.ok:
            return RuntimeResult(ok=False, message="Both slots must have content for compare.")

        text_a = str((a.payload or {}).get("content", ""))
        text_b = str((b.payload or {}).get("content", ""))

        a_words = set(text_a.split())
        b_words = set(text_b.split())
        added = sorted(list(b_words - a_words))[:20]
        removed = sorted(list(a_words - b_words))[:20]

        return RuntimeResult(
            ok=True,
            message="Slot compare summary ready.",
            payload={
                "slotA": slot_a,
                "slotB": slot_b,
                "addedWords": added,
                "removedWords": removed,
                "lenA": len(text_a),
                "lenB": len(text_b),
            },
        )

    def split_slot(self, slot: int, separator: str = "\n") -> RuntimeResult:
        cur = self.runtime.paste_from_slot(slot)
        if not cur.ok:
            return cur
        content = str((cur.payload or {}).get("content", ""))
        pieces = [p.strip() for p in content.split(separator) if p.strip()]
        if len(pieces) < 2:
            return RuntimeResult(ok=False, message="No split parts found.")

        self.runtime.edit_slot(slot, pieces[0])
        next_slot = slot + 1
        if next_slot <= 12:
            self.runtime.unprotect_slot(next_slot)
            self.runtime.copy_to_slot(
                context=self._empty_context(),
                slot=next_slot,
                text=separator.join(pieces[1:]),
            )

        return RuntimeResult(
            ok=True,
            message="Slot split completed.",
            payload={"primarySlot": slot, "secondarySlot": next_slot if next_slot <= 12 else None},
        )

    def merge_slots(self, slot_a: int, slot_b: int, separator: str = "\n") -> RuntimeResult:
        a = self.runtime.paste_from_slot(slot_a)
        b = self.runtime.paste_from_slot(slot_b)
        if not a.ok or not b.ok:
            return RuntimeResult(ok=False, message="Both slots must contain content to merge.")

        merged = f"{(a.payload or {}).get('content', '')}{separator}{(b.payload or {}).get('content', '')}"
        return self.runtime.edit_slot(slot_a, merged)

    def reorder_slot(self, from_slot: int, to_slot: int, overwrite: bool = False) -> RuntimeResult:
        src = self.runtime.paste_from_slot(from_slot)
        if not src.ok:
            return src

        to_desc = self.runtime.describe_slot(to_slot)
        to_payload = to_desc.payload or {}
        to_empty = bool(to_payload.get("empty", True))
        if not to_empty and not overwrite:
            return RuntimeResult(
                ok=False,
                message="Destination slot has content.",
                next_steps=["Retry with overwrite enabled.", "Choose an empty destination slot."],
            )

        src_content = str((src.payload or {}).get("content", ""))
        self.runtime.unprotect_slot(to_slot)
        put = self.runtime.copy_to_slot(self._empty_context(), slot=to_slot, text=src_content)
        if not put.ok:
            return put

        self.runtime.unprotect_slot(from_slot)
        self.runtime.delete_slot(from_slot)
        return RuntimeResult(ok=True, message="Slot reorder completed.", payload={"from": from_slot, "to": to_slot})

    def batch_action(self, slots: List[int], action: str) -> RuntimeResult:
        done: List[int] = []
        for slot in slots:
            if action == "protect":
                result = self.runtime.protect_slot(slot)
            elif action == "unprotect":
                result = self.runtime.unprotect_slot(slot)
            elif action == "delete":
                result = self.runtime.delete_slot(slot)
            else:
                return RuntimeResult(ok=False, message=f"Unsupported batch action: {action}")

            if result.ok:
                done.append(slot)

        return RuntimeResult(ok=True, message="Batch action complete.", payload={"action": action, "slots": done})

    def export_pack(self, slots: List[int], out_path: Path | str) -> RuntimeResult:
        out = Path(out_path)
        payload: Dict[str, dict] = {"version": 1, "slots": {}}
        for slot in slots:
            desc = self.runtime.describe_slot(slot)
            if not desc.ok:
                continue
            paste = self.runtime.paste_from_slot(slot)
            slot_payload = desc.payload or {}
            payload["slots"][str(slot)] = {
                "meta": slot_payload,
                "content": (paste.payload or {}).get("content", "") if paste.ok else "",
            }

        canonical = json.dumps({"version": payload["version"], "slots": payload["slots"]}, sort_keys=True, separators=(",", ":"))
        payload["integrity"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return RuntimeResult(ok=True, message="Slot pack exported.", payload={"path": str(out), "count": len(payload["slots"])})

    def import_pack(self, in_path: Path | str, overwrite: bool = False) -> RuntimeResult:
        src = Path(in_path)
        if not src.exists():
            return RuntimeResult(ok=False, message="Slot pack file not found.")

        try:
            payload = json.loads(src.read_text(encoding="utf-8"))
        except Exception:
            return RuntimeResult(ok=False, message="Slot pack is malformed JSON.")

        if not isinstance(payload, dict) or payload.get("version") != 1 or not isinstance(payload.get("slots", {}), dict):
            return RuntimeResult(ok=False, message="Slot pack is incompatible or malformed.")

        integrity = str(payload.get("integrity", ""))
        canonical = json.dumps({"version": payload.get("version"), "slots": payload.get("slots", {})}, sort_keys=True, separators=(",", ":"))
        expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if integrity and integrity != expected:
            return RuntimeResult(ok=False, message="Slot pack integrity check failed.")

        slots_data = payload.get("slots", {})
        restored: List[int] = []

        for slot_key, data in slots_data.items():
            try:
                slot = int(slot_key)
            except ValueError:
                continue
            if slot < 1 or slot > 12:
                continue

            current = self.runtime.describe_slot(slot)
            current_empty = bool((current.payload or {}).get("empty", True))
            if not overwrite and not current_empty:
                continue

            self.runtime.unprotect_slot(slot)
            self.runtime.copy_to_slot(self._empty_context(), slot=slot, text=str(data.get("content", "")))
            meta = data.get("meta", {})
            if bool(meta.get("protected", False)):
                self.runtime.protect_slot(slot)
            restored.append(slot)

        return RuntimeResult(ok=True, message="Slot pack import complete.", payload={"restoredSlots": restored})

    @staticmethod
    def _empty_context():
        from .engine import AppContext

        return AppContext(
            app_id="studio",
            window_id="studio",
            control_id="studio",
            buffer="",
            caret=0,
            clipboard_text="",
        )
