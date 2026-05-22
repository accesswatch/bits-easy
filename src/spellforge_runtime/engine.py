from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .diagnostics import get_logger

_logger = get_logger("spellforge.engine")


class RuntimeErrorCode(str, Enum):
    UNSUPPORTED_SURFACE = "unsupported-surface"
    PROTECTED_SLOT = "protected-slot"
    EMPTY_SLOT = "empty-slot"
    INVALID_SLOT = "invalid-slot"
    NO_SELECTION = "no-selection"
    NO_ANCHOR = "no-anchor"


@dataclass
class RuntimeResult:
    ok: bool
    message: str
    code: Optional[RuntimeErrorCode] = None
    payload: Optional[dict] = None
    next_steps: List[str] = field(default_factory=list)


@dataclass
class SourceAnchor:
    app_id: str
    window_id: str
    control_id: str
    caret: int
    captured_at: str


@dataclass
class SelectionRange:
    app_id: str
    start: int
    end: int
    text: str
    confidence: float


@dataclass
class ClipItem:
    content: str
    source_app: str
    captured_at: str
    length: int


@dataclass
class ClipSlot:
    item: Optional[ClipItem] = None
    protected: bool = False


@dataclass
class AppContext:
    app_id: str
    window_id: str
    control_id: str
    buffer: str
    caret: int
    clipboard_text: str = ""


@dataclass
class RestoreResult:
    success: bool
    drift_detected: bool
    restored_caret: int


class AdapterError(Exception):
    pass


class UnsupportedSurfaceError(AdapterError):
    pass


class AppAdapter:
    def __init__(self, app_id: str, supports_selection: bool = True):
        self.app_id = app_id
        self.supports_selection = supports_selection

    def normalize_range(self, context: AppContext, start: int, end: int) -> SelectionRange:
        if not self.supports_selection:
            raise UnsupportedSurfaceError(
                f"Selection is not supported in {self.app_id} for this surface."
            )

        lo = min(start, end)
        hi = max(start, end)
        if lo < 0 or hi > len(context.buffer) or lo == hi:
            raise UnsupportedSurfaceError(
                "Unable to form a valid selection range in this surface."
            )

        text = context.buffer[lo:hi]
        return SelectionRange(
            app_id=self.app_id,
            start=lo,
            end=hi,
            text=text,
            confidence=1.0,
        )

    def restore_anchor(self, anchor: SourceAnchor, context: AppContext) -> RestoreResult:
        if anchor.window_id != context.window_id or anchor.control_id != context.control_id:
            return RestoreResult(success=False, drift_detected=True, restored_caret=context.caret)

        if anchor.caret > len(context.buffer):
            return RestoreResult(success=True, drift_detected=True, restored_caret=len(context.buffer))

        return RestoreResult(success=True, drift_detected=False, restored_caret=anchor.caret)


class DriftAwareAdapter(AppAdapter):
    def __init__(self, app_id: str, supports_selection: bool = True, drift_delta: int = 0):
        super().__init__(app_id=app_id, supports_selection=supports_selection)
        self.drift_delta = drift_delta

    def restore_anchor(self, anchor: SourceAnchor, context: AppContext) -> RestoreResult:
        if anchor.window_id != context.window_id or anchor.control_id != context.control_id:
            return RestoreResult(success=False, drift_detected=True, restored_caret=context.caret)

        requested = max(0, min(len(context.buffer), anchor.caret + self.drift_delta))
        return RestoreResult(
            success=True,
            drift_detected=(requested != anchor.caret),
            restored_caret=requested,
        )


class SpellforgeRuntime:
    def __init__(self, adapters: Dict[str, AppAdapter], storage_path: Optional[Path | str] = None):
        self.adapters = adapters
        self._selection_markers: Dict[str, Dict[str, int]] = {}
        self._selection_cache: Dict[str, SelectionRange] = {}
        self._source_anchor: Optional[SourceAnchor] = None
        self._slots: Dict[int, ClipSlot] = {i: ClipSlot() for i in range(1, 13)}
        self._storage_path: Optional[Path] = Path(storage_path) if storage_path else None

        self._merge_mode = "append"
        self._merge_divider = "\n"
        self._merge_buffer = ""
        self._clear_on_paste = False

        self.load_slots()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _adapter_for(self, app_id: str) -> AppAdapter:
        if app_id in self.adapters:
            return self.adapters[app_id]
        return AppAdapter(app_id=app_id, supports_selection=False)

    def _slot_or_error(self, slot: int) -> Tuple[Optional[ClipSlot], Optional[RuntimeResult]]:
        if slot not in self._slots:
            return None, RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.INVALID_SLOT,
                message="Slot must be between 1 and 12.",
                next_steps=["Choose a slot in the range 1 to 12."],
            )
        return self._slots[slot], None

    def _serialize_slots(self) -> Dict[str, dict]:
        payload: Dict[str, dict] = {}
        for slot_id, slot_ref in self._slots.items():
            payload[str(slot_id)] = {
                "protected": slot_ref.protected,
                "item": None
                if slot_ref.item is None
                else {
                    "content": slot_ref.item.content,
                    "source_app": slot_ref.item.source_app,
                    "captured_at": slot_ref.item.captured_at,
                    "length": slot_ref.item.length,
                },
            }
        return payload

    def _deserialize_slots(self, payload: Dict[str, dict]) -> None:
        for slot_key, value in payload.items():
            try:
                slot_id = int(slot_key)
            except ValueError:
                continue
            if slot_id not in self._slots:
                continue

            slot_ref = self._slots[slot_id]
            slot_ref.protected = bool(value.get("protected", False))

            item = value.get("item")
            if not item:
                slot_ref.item = None
                continue

            slot_ref.item = ClipItem(
                content=str(item.get("content", "")),
                source_app=str(item.get("source_app", "unknown")),
                captured_at=str(item.get("captured_at", self._now())),
                length=int(item.get("length", len(str(item.get("content", ""))))),
            )

    def save_slots(self) -> None:
        if self._storage_path is None:
            return

        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._storage_path.write_text(
            json.dumps(self._serialize_slots(), indent=2),
            encoding="utf-8",
        )

    def load_slots(self) -> None:
        if self._storage_path is None or not self._storage_path.exists():
            return

        try:
            raw = self._storage_path.read_text(encoding="utf-8")
            payload = json.loads(raw)
            if isinstance(payload, dict):
                self._deserialize_slots(payload)
        except Exception:
            _logger.exception("Spellforge: loading clip slots at %s failed", self._storage_path)
            return

    def save_source_anchor(self, context: AppContext) -> RuntimeResult:
        self._source_anchor = SourceAnchor(
            app_id=context.app_id,
            window_id=context.window_id,
            control_id=context.control_id,
            caret=context.caret,
            captured_at=self._now(),
        )
        return RuntimeResult(ok=True, message="Source anchor saved.")

    def restore_source_anchor(self, context: AppContext) -> RuntimeResult:
        if self._source_anchor is None:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.NO_ANCHOR,
                message="No source anchor is available.",
                next_steps=[
                    "Run a selection or transform command first to capture a source anchor.",
                ],
            )

        adapter = self._adapter_for(self._source_anchor.app_id)
        restore = adapter.restore_anchor(self._source_anchor, context)
        if not restore.success:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.NO_ANCHOR,
                message="Could not restore source anchor in the current surface.",
                next_steps=[
                    "Retry return to source.",
                    "Open guided manual return options.",
                ],
            )

        context.caret = restore.restored_caret
        if restore.drift_detected:
            return RuntimeResult(
                ok=True,
                message="Returned to nearest valid source location. Drift detected.",
                payload={"caret": context.caret, "driftDetected": True},
                next_steps=[
                    "Retry exact restore.",
                    "Use manual return options.",
                ],
            )

        return RuntimeResult(
            ok=True,
            message="Returned to exact source anchor.",
            payload={"caret": context.caret, "driftDetected": False},
        )

    def mark_selection_start(self, context: AppContext) -> RuntimeResult:
        self._selection_markers.setdefault(context.app_id, {})["start"] = context.caret
        self.save_source_anchor(context)
        return RuntimeResult(
            ok=True,
            message=f"Selection start marker set at {context.caret}.",
            payload={"caret": context.caret},
        )

    def mark_selection_end(self, context: AppContext) -> RuntimeResult:
        markers = self._selection_markers.setdefault(context.app_id, {})
        if "start" not in markers:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.NO_SELECTION,
                message="Selection start marker is not set.",
                next_steps=[
                    "Set selection start marker first.",
                    "Use quick capture fallback.",
                ],
            )

        markers["end"] = context.caret
        adapter = self._adapter_for(context.app_id)
        try:
            selection = adapter.normalize_range(context, markers["start"], markers["end"])
            self._selection_cache[context.app_id] = selection
            return RuntimeResult(
                ok=True,
                message=f"Selection range captured, {len(selection.text)} characters.",
                payload={
                    "start": selection.start,
                    "end": selection.end,
                    "length": len(selection.text),
                    "confidence": selection.confidence,
                },
            )
        except UnsupportedSurfaceError:
            fallback_text = context.clipboard_text.strip()
            if fallback_text:
                self._selection_cache[context.app_id] = SelectionRange(
                    app_id=context.app_id,
                    start=markers["start"],
                    end=context.caret,
                    text=fallback_text,
                    confidence=0.6,
                )
                return RuntimeResult(
                    ok=True,
                    message="Selection surface unsupported. Captured fallback text from clipboard.",
                    code=RuntimeErrorCode.UNSUPPORTED_SURFACE,
                    payload={"confidence": 0.6, "fallbackUsed": True},
                    next_steps=["Review captured text before applying mutating actions."],
                )

            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.UNSUPPORTED_SURFACE,
                message="Selection is unsupported in this surface.",
                next_steps=[
                    "Use quick capture to inbox.",
                    "Open palette with fallback actions.",
                ],
            )

    def read_selection_context(self, context: AppContext, snippet: int = 18) -> RuntimeResult:
        if context.app_id not in self._selection_cache:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.NO_SELECTION,
                message="No selection range is available.",
                next_steps=["Set selection start and end markers first."],
            )

        selection = self._selection_cache[context.app_id]
        preview = selection.text.strip()
        head = preview[:snippet]
        tail = preview[-snippet:] if len(preview) > snippet else preview
        return RuntimeResult(
            ok=True,
            message="Selection context ready.",
            payload={
                "startSnippet": head,
                "endSnippet": tail,
                "confidence": selection.confidence,
                "length": len(selection.text),
            },
        )

    def jump_selection_start(self, context: AppContext) -> RuntimeResult:
        markers = self._selection_markers.get(context.app_id, {})
        if "start" not in markers:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.NO_SELECTION,
                message="No selection start marker exists.",
                next_steps=["Set a selection start marker first."],
            )

        target = min(max(markers["start"], 0), len(context.buffer))
        context.caret = target
        return RuntimeResult(ok=True, message="Jumped to selection start.", payload={"caret": target})

    def cancel_selection(self, context: AppContext) -> RuntimeResult:
        self._selection_markers.pop(context.app_id, None)
        self._selection_cache.pop(context.app_id, None)
        return RuntimeResult(ok=True, message="Selection markers cleared.")

    def copy_to_slot(self, context: AppContext, slot: int, text: Optional[str] = None) -> RuntimeResult:
        slot_ref, slot_err = self._slot_or_error(slot)
        if slot_err is not None:
            return slot_err

        assert slot_ref is not None
        if slot_ref.protected:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.PROTECTED_SLOT,
                message=f"Slot {slot} is protected and cannot be overwritten.",
                next_steps=["Unprotect the slot or choose a different slot."],
            )

        content = (text or "").strip()
        if not content and context.app_id in self._selection_cache:
            content = self._selection_cache[context.app_id].text
        if not content:
            content = context.clipboard_text.strip()

        if not content:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.NO_SELECTION,
                message="No content available to copy into a slot.",
                next_steps=[
                    "Mark a selection and capture it.",
                    "Copy text to clipboard and retry.",
                ],
            )

        slot_ref.item = ClipItem(
            content=content,
            source_app=context.app_id,
            captured_at=self._now(),
            length=len(content),
        )
        self.save_slots()
        return RuntimeResult(
            ok=True,
            message=f"Copied content to slot {slot}.",
            payload={"slot": slot, "length": len(content)},
        )

    def paste_from_slot(self, slot: int) -> RuntimeResult:
        slot_ref, slot_err = self._slot_or_error(slot)
        if slot_err is not None:
            return slot_err

        assert slot_ref is not None
        if slot_ref.item is None:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.EMPTY_SLOT,
                message=f"Slot {slot} is empty.",
                next_steps=["Copy content into the slot first."],
            )

        return RuntimeResult(
            ok=True,
            message=f"Ready to paste from slot {slot}.",
            payload={
                "slot": slot,
                "content": slot_ref.item.content,
                "sourceApp": slot_ref.item.source_app,
                "length": slot_ref.item.length,
            },
        )

    def protect_slot(self, slot: int) -> RuntimeResult:
        slot_ref, slot_err = self._slot_or_error(slot)
        if slot_err is not None:
            return slot_err
        assert slot_ref is not None

        slot_ref.protected = True
        self.save_slots()
        return RuntimeResult(ok=True, message=f"Slot {slot} is now protected.")

    def unprotect_slot(self, slot: int) -> RuntimeResult:
        slot_ref, slot_err = self._slot_or_error(slot)
        if slot_err is not None:
            return slot_err
        assert slot_ref is not None

        slot_ref.protected = False
        self.save_slots()
        return RuntimeResult(ok=True, message=f"Slot {slot} is now unprotected.")

    def delete_slot(self, slot: int) -> RuntimeResult:
        slot_ref, slot_err = self._slot_or_error(slot)
        if slot_err is not None:
            return slot_err
        assert slot_ref is not None

        if slot_ref.protected:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.PROTECTED_SLOT,
                message=f"Slot {slot} is protected and cannot be deleted.",
                next_steps=["Unprotect the slot first."],
            )

        slot_ref.item = None
        self.save_slots()
        return RuntimeResult(ok=True, message=f"Deleted content from slot {slot}.")

    def edit_slot(self, slot: int, content: str) -> RuntimeResult:
        slot_ref, slot_err = self._slot_or_error(slot)
        if slot_err is not None:
            return slot_err
        assert slot_ref is not None

        if slot_ref.item is None:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.EMPTY_SLOT,
                message=f"Slot {slot} is empty and cannot be edited.",
                next_steps=["Copy content into the slot first."],
            )

        if slot_ref.protected:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.PROTECTED_SLOT,
                message=f"Slot {slot} is protected and cannot be edited.",
                next_steps=["Unprotect the slot first."],
            )

        slot_ref.item.content = content
        slot_ref.item.length = len(content)
        self.save_slots()
        return RuntimeResult(ok=True, message=f"Edited slot {slot}.", payload={"length": len(content)})

    def describe_slot(self, slot: int) -> RuntimeResult:
        slot_ref, slot_err = self._slot_or_error(slot)
        if slot_err is not None:
            return slot_err
        assert slot_ref is not None

        if slot_ref.item is None:
            return RuntimeResult(
                ok=True,
                message=f"Slot {slot} is empty.",
                payload={"slot": slot, "empty": True, "protected": slot_ref.protected},
            )

        return RuntimeResult(
            ok=True,
            message=f"Slot {slot} has content.",
            payload={
                "slot": slot,
                "empty": False,
                "protected": slot_ref.protected,
                "sourceApp": slot_ref.item.source_app,
                "capturedAt": slot_ref.item.captured_at,
                "length": slot_ref.item.length,
                "preview": slot_ref.item.content[:60],
            },
        )

    def set_merge_mode_append(self) -> RuntimeResult:
        self._merge_mode = "append"
        return RuntimeResult(ok=True, message="Merge mode set to append.")

    def set_merge_mode_replace(self) -> RuntimeResult:
        self._merge_mode = "replace"
        return RuntimeResult(ok=True, message="Merge mode set to replace.")

    def set_merge_divider_line(self) -> RuntimeResult:
        self._merge_divider = "\n---\n"
        return RuntimeResult(ok=True, message="Merge divider set to line.")

    def set_merge_divider_space(self) -> RuntimeResult:
        self._merge_divider = " "
        return RuntimeResult(ok=True, message="Merge divider set to space.")

    def set_merge_divider_paragraph(self) -> RuntimeResult:
        self._merge_divider = "\n\n"
        return RuntimeResult(ok=True, message="Merge divider set to paragraph.")

    def set_merge_custom_separator(self, separator: str) -> RuntimeResult:
        self._merge_divider = separator
        return RuntimeResult(ok=True, message="Merge custom separator set.", payload={"separator": separator})

    def set_clear_on_paste(self, enabled: bool) -> RuntimeResult:
        self._clear_on_paste = enabled
        return RuntimeResult(ok=True, message=f"Clear on paste set to {enabled}.")

    def toggle_clear_on_paste(self) -> RuntimeResult:
        self._clear_on_paste = not self._clear_on_paste
        return RuntimeResult(ok=True, message=f"Clear on paste set to {self._clear_on_paste}.", payload={"enabled": self._clear_on_paste})

    def merge_capture(self, segment: str, source_tag: Optional[str] = None) -> RuntimeResult:
        value = segment
        if source_tag:
            value = f"[{source_tag}] {value}"

        if self._merge_mode == "replace" or not self._merge_buffer:
            self._merge_buffer = value
        else:
            self._merge_buffer = f"{self._merge_buffer}{self._merge_divider}{value}"

        return RuntimeResult(
            ok=True,
            message="Merge segment captured.",
            payload={"bufferLength": len(self._merge_buffer), "mode": self._merge_mode},
        )

    def merge_commit(self) -> RuntimeResult:
        output = self._merge_buffer
        if not output:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.NO_SELECTION,
                message="Merge buffer is empty.",
                next_steps=["Capture at least one segment before commit."],
            )

        if self._clear_on_paste:
            self._merge_buffer = ""

        return RuntimeResult(ok=True, message="Merge commit ready.", payload={"content": output})
