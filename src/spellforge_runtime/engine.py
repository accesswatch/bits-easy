from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
        self._selection_markers: Dict[str, Dict[str, Any]] = {}
        self._selection_cache: Dict[str, SelectionRange] = {}
        self._source_anchor: Optional[SourceAnchor] = None
        self._slots: Dict[int, ClipSlot] = {i: ClipSlot() for i in range(1, 13)}
        self._active_slot: int = 1
        self._storage_path: Optional[Path] = Path(storage_path) if storage_path else None
        self._marker_metrics: Dict[str, Any] = {"global": {}, "apps": {}}

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

    def _resolve_slot_number(self, slot: Optional[int]) -> int:
        return self._active_slot if slot is None else int(slot)

    def active_slot(self) -> int:
        return self._active_slot

    def select_active_slot(self, slot: int) -> RuntimeResult:
        slot_ref, slot_err = self._slot_or_error(slot)
        if slot_err is not None:
            return slot_err
        assert slot_ref is not None
        self._active_slot = int(slot)
        return RuntimeResult(
            ok=True,
            message=f"Active clip slot set to {slot}.",
            payload={"slot": int(slot), "activeSlot": self._active_slot},
        )

    def selection_text_for_actions(self, context: AppContext) -> str:
        selection = self._selection_cache.get(context.app_id)
        if selection is not None:
            return selection.text.strip()

        # If range markers are available but cache is missing, reconstruct from
        # current buffer so selection actions can still proceed predictably.
        markers = self._selection_markers.get(context.app_id, {})
        start_caret = self._marker_caret(markers, "start")
        end_caret = self._marker_caret(markers, "end")
        if start_caret is None or end_caret is None:
            return ""

        lo = min(start_caret, end_caret)
        hi = max(start_caret, end_caret)
        if lo < 0 or hi > len(context.buffer) or lo == hi:
            return ""
        return context.buffer[lo:hi].strip()

    def _selection_guided_flow_payload(
        self,
        context: AppContext,
        *,
        stage: str,
        fallback_used: bool = False,
        drift_detected: bool = False,
    ) -> Dict[str, Any]:
        hints: List[str] = []
        if stage == "start-set":
            hints = [
                "Move caret to target start point.",
                "Use normal selection keys such as Shift+Arrow to extend selection.",
                "Run Mark selection end to capture and preview the range.",
            ]
        elif stage == "range-captured":
            hints = [
                "Run Read selection context to preview snippets.",
                "Run summarize, extract actions, or rewrite on the captured range.",
                "Run Jump selection start to quickly return to anchor.",
            ]
        elif stage == "fallback-captured":
            hints = [
                "Review fallback text in selection context before mutating actions.",
                "If needed, refresh selection in a supported text field.",
                "Use quick capture fallback when surface blocks range capture.",
            ]
        elif stage == "status":
            hints = [
                "Use marker status to verify drift and confidence.",
                "If markers look stale, cancel and re-capture.",
            ]
        elif stage == "cancelled":
            hints = [
                "Set selection start to begin a new capture cycle.",
                "Use quick inbox capture for one-off snippets.",
            ]

        return {
            "stage": stage,
            "appId": context.app_id,
            "normalSelectionMode": True,
            "fallbackUsed": fallback_used,
            "surfaceDriftDetected": drift_detected,
            "hints": hints,
        }

    @staticmethod
    def _selection_preview_payload(selection: SelectionRange, snippet: int = 18) -> Dict[str, Any]:
        preview = selection.text.strip()
        head = preview[:snippet]
        tail = preview[-snippet:] if len(preview) > snippet else preview
        return {
            "startSnippet": head,
            "endSnippet": tail,
            "confidence": selection.confidence,
            "length": len(selection.text),
        }

    @staticmethod
    def _surface_key(context: AppContext) -> str:
        return f"{context.app_id}:{context.window_id}:{context.control_id}"

    def _marker_meta(self, context: AppContext) -> Dict[str, Any]:
        return {
            "appId": context.app_id,
            "windowId": context.window_id,
            "controlId": context.control_id,
            "surfaceKey": self._surface_key(context),
            "capturedAt": self._now(),
        }

    @staticmethod
    def _marker_caret(markers: Dict[str, Any], key: str) -> Optional[int]:
        value = markers.get(key)
        if isinstance(value, int):
            return value
        return None

    def _record_marker_metric(self, app_id: str, metric: str) -> None:
        metric_key = metric.strip()
        if not metric_key:
            return
        global_metrics = self._marker_metrics.setdefault("global", {})
        app_metrics = self._marker_metrics.setdefault("apps", {}).setdefault(app_id, {})
        global_metrics[metric_key] = int(global_metrics.get(metric_key, 0)) + 1
        app_metrics[metric_key] = int(app_metrics.get(metric_key, 0)) + 1

    @staticmethod
    def _metric_rate(numerator: int, denominator: int) -> float:
        if denominator <= 0:
            return 0.0
        return round(numerator / denominator, 4)

    def _marker_telemetry_payload(self, app_id: str) -> Dict[str, Any]:
        global_metrics = dict(self._marker_metrics.get("global", {}))
        app_metrics = dict((self._marker_metrics.get("apps", {}) or {}).get(app_id, {}))
        app_attempts = int(app_metrics.get("markEndAttempt", 0))
        app_captured = int(app_metrics.get("markEndCaptured", 0))
        app_fallback = int(app_metrics.get("fallbackUsed", 0))
        app_surface_drift = int(app_metrics.get("surfaceDriftDetected", 0))
        return {
            "appId": app_id,
            "app": app_metrics,
            "global": global_metrics,
            "rates": {
                "captureSuccessRate": self._metric_rate(app_captured, app_attempts),
                "fallbackRate": self._metric_rate(app_fallback, app_attempts),
                "surfaceDriftRate": self._metric_rate(app_surface_drift, app_attempts),
            },
        }

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
        markers = self._selection_markers.setdefault(context.app_id, {})
        markers["start"] = context.caret
        markers["startMeta"] = self._marker_meta(context)
        self.save_source_anchor(context)
        self._record_marker_metric(context.app_id, "markStartSet")
        return RuntimeResult(
            ok=True,
            message=f"Selection start marker set at {context.caret}.",
            payload={
                "caret": context.caret,
                "guidedFlow": self._selection_guided_flow_payload(context, stage="start-set"),
            },
            next_steps=[
                "Use normal selection keys to extend the selection.",
                "Run Mark selection end to capture the active range.",
            ],
        )

    def mark_selection_end(self, context: AppContext) -> RuntimeResult:
        markers = self._selection_markers.setdefault(context.app_id, {})
        start_caret = self._marker_caret(markers, "start")
        if start_caret is None:
            self._record_marker_metric(context.app_id, "markEndMissingStart")
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.NO_SELECTION,
                message="Selection start marker is not set.",
                next_steps=[
                    "Set selection start marker first.",
                    "Use quick capture fallback.",
                ],
            )

        self._record_marker_metric(context.app_id, "markEndAttempt")
        markers["end"] = context.caret
        markers["endMeta"] = self._marker_meta(context)
        start_meta = markers.get("startMeta", {})
        if isinstance(start_meta, dict):
            start_surface = str(start_meta.get("surfaceKey", ""))
            if start_surface and start_surface != self._surface_key(context):
                self._record_marker_metric(context.app_id, "surfaceDriftDetected")

        adapter = self._adapter_for(context.app_id)
        try:
            selection = adapter.normalize_range(context, start_caret, context.caret)
            self._selection_cache[context.app_id] = selection
            payload = self._selection_preview_payload(selection)
            payload.update(
                {
                    "start": selection.start,
                    "end": selection.end,
                    "startMeta": markers.get("startMeta"),
                    "endMeta": markers.get("endMeta"),
                    "guidedFlow": self._selection_guided_flow_payload(context, stage="range-captured"),
                }
            )
            self._record_marker_metric(context.app_id, "markEndCaptured")
            return RuntimeResult(
                ok=True,
                message=f"Selection range captured, {len(selection.text)} characters.",
                payload=payload,
                next_steps=[
                    "Run Read selection context to verify snippets.",
                    "Apply summarize or rewrite on the captured selection.",
                ],
            )
        except UnsupportedSurfaceError:
            lo = min(start_caret, context.caret)
            hi = max(start_caret, context.caret)
            if lo >= 0 and hi <= len(context.buffer) and hi > lo:
                fallback_text = context.buffer[lo:hi].strip()
                if fallback_text:
                    fallback_selection = SelectionRange(
                        app_id=context.app_id,
                        start=lo,
                        end=hi,
                        text=fallback_text,
                        confidence=0.75,
                    )
                    self._selection_cache[context.app_id] = fallback_selection
                    payload = self._selection_preview_payload(fallback_selection)
                    payload.update(
                        {
                            "fallbackUsed": True,
                            "fallbackSource": "buffer-range",
                            "start": lo,
                            "end": hi,
                            "startMeta": markers.get("startMeta"),
                            "endMeta": markers.get("endMeta"),
                            "guidedFlow": self._selection_guided_flow_payload(
                                context,
                                stage="fallback-captured",
                                fallback_used=True,
                            ),
                        }
                    )
                    self._record_marker_metric(context.app_id, "markEndCaptured")
                    self._record_marker_metric(context.app_id, "fallbackUsed")
                    self._record_marker_metric(context.app_id, "bufferFallbackUsed")
                    return RuntimeResult(
                        ok=True,
                        message="Selection surface unsupported. Captured fallback text from current buffer range.",
                        code=RuntimeErrorCode.UNSUPPORTED_SURFACE,
                        payload=payload,
                        next_steps=["Review captured text before applying mutating actions."],
                    )

            fallback_text = context.clipboard_text.strip()
            if fallback_text:
                fallback_selection = SelectionRange(
                    app_id=context.app_id,
                    start=start_caret,
                    end=context.caret,
                    text=fallback_text,
                    confidence=0.6,
                )
                self._selection_cache[context.app_id] = fallback_selection
                payload = self._selection_preview_payload(fallback_selection)
                payload.update(
                    {
                        "fallbackUsed": True,
                        "start": start_caret,
                        "end": context.caret,
                        "startMeta": markers.get("startMeta"),
                        "endMeta": markers.get("endMeta"),
                            "fallbackSource": "clipboard",
                            "guidedFlow": self._selection_guided_flow_payload(
                                context,
                                stage="fallback-captured",
                                fallback_used=True,
                            ),
                    }
                )
                self._record_marker_metric(context.app_id, "markEndCaptured")
                self._record_marker_metric(context.app_id, "fallbackUsed")
                return RuntimeResult(
                    ok=True,
                    message="Selection surface unsupported. Captured fallback text from clipboard.",
                    code=RuntimeErrorCode.UNSUPPORTED_SURFACE,
                    payload=payload,
                    next_steps=["Review captured text before applying mutating actions."],
                )

            self._record_marker_metric(context.app_id, "unsupportedSurfaceFailure")
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.UNSUPPORTED_SURFACE,
                message="Selection is unsupported in this surface.",
                next_steps=[
                    "Use quick capture to inbox.",
                    "Open palette with fallback actions.",
                ],
            )
        finally:
            if context.app_id in self._selection_cache:
                markers["lastRangeMeta"] = self._selection_preview_payload(self._selection_cache[context.app_id], snippet=32)

    def read_selection_context(self, context: AppContext, snippet: int = 18) -> RuntimeResult:
        if context.app_id not in self._selection_cache:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.NO_SELECTION,
                message="No selection range is available.",
                next_steps=["Set selection start and end markers first."],
            )

        self._record_marker_metric(context.app_id, "readContext")
        selection = self._selection_cache[context.app_id]
        payload = self._selection_preview_payload(selection, snippet=snippet)
        payload["guidedFlow"] = self._selection_guided_flow_payload(context, stage="status")
        return RuntimeResult(
            ok=True,
            message="Selection context ready.",
            payload=payload,
            next_steps=[
                "Run summarize or extract actions on this selection.",
                "Run marker status if you need drift diagnostics.",
            ],
        )

    def describe_selection_markers(self, context: AppContext, snippet: int = 18) -> RuntimeResult:
        markers = self._selection_markers.get(context.app_id, {})
        selection = self._selection_cache.get(context.app_id)
        has_start = self._marker_caret(markers, "start") is not None
        has_end = self._marker_caret(markers, "end") is not None
        start_meta = markers.get("startMeta") if isinstance(markers.get("startMeta"), dict) else {}
        end_meta = markers.get("endMeta") if isinstance(markers.get("endMeta"), dict) else {}
        current_surface = self._surface_key(context)
        surface_drift_from_start = bool(start_meta.get("surfaceKey")) and str(start_meta.get("surfaceKey")) != current_surface
        self._record_marker_metric(context.app_id, "statusRead")

        if selection is not None:
            payload = self._selection_preview_payload(selection, snippet=snippet)
            payload.update(
                {
                    "startMarkerSet": has_start,
                    "endMarkerSet": has_end,
                    "startCaret": self._marker_caret(markers, "start"),
                    "endCaret": self._marker_caret(markers, "end"),
                    "activeRangeStart": selection.start,
                    "activeRangeEnd": selection.end,
                    "startMeta": start_meta,
                    "endMeta": end_meta,
                    "currentSurfaceKey": current_surface,
                    "surfaceDriftFromStart": surface_drift_from_start,
                    "telemetry": self._marker_telemetry_payload(context.app_id),
                    "guidedFlow": self._selection_guided_flow_payload(
                        context,
                        stage="status",
                        drift_detected=surface_drift_from_start,
                    ),
                }
            )
            return RuntimeResult(
                ok=True,
                message="Selection markers and range are ready.",
                payload=payload,
            )

        if has_start and has_end:
            return RuntimeResult(
                ok=True,
                message="Selection markers are set, but no active range is cached yet.",
                payload={
                    "startMarkerSet": True,
                    "endMarkerSet": True,
                    "startCaret": self._marker_caret(markers, "start"),
                    "endCaret": self._marker_caret(markers, "end"),
                    "startMeta": start_meta,
                    "endMeta": end_meta,
                    "currentSurfaceKey": current_surface,
                    "surfaceDriftFromStart": surface_drift_from_start,
                    "telemetry": self._marker_telemetry_payload(context.app_id),
                },
                next_steps=["Run Mark selection end again to refresh the selection range."],
            )

        if has_start:
            return RuntimeResult(
                ok=True,
                message="Selection start marker is set. End marker is not set yet.",
                payload={
                    "startMarkerSet": True,
                    "endMarkerSet": False,
                    "startCaret": self._marker_caret(markers, "start"),
                    "startMeta": start_meta,
                    "currentSurfaceKey": current_surface,
                    "surfaceDriftFromStart": surface_drift_from_start,
                    "telemetry": self._marker_telemetry_payload(context.app_id),
                },
                next_steps=["Set selection end marker to capture a range."],
            )

        if has_end:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.NO_SELECTION,
                message="Selection end marker exists without a start marker.",
                payload={
                    "startMarkerSet": False,
                    "endMarkerSet": True,
                    "endCaret": self._marker_caret(markers, "end"),
                    "endMeta": end_meta,
                    "currentSurfaceKey": current_surface,
                    "telemetry": self._marker_telemetry_payload(context.app_id),
                },
                next_steps=["Cancel selection markers and set selection start marker first."],
            )

        return RuntimeResult(
            ok=False,
            code=RuntimeErrorCode.NO_SELECTION,
            message="No selection markers are set.",
            payload={
                "startMarkerSet": False,
                "endMarkerSet": False,
                "currentSurfaceKey": current_surface,
                "telemetry": self._marker_telemetry_payload(context.app_id),
            },
            next_steps=["Set selection start marker first."],
        )

    def jump_selection_start(self, context: AppContext) -> RuntimeResult:
        markers = self._selection_markers.get(context.app_id, {})
        start_caret = self._marker_caret(markers, "start")
        if start_caret is None:
            self._record_marker_metric(context.app_id, "jumpMissingStart")
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.NO_SELECTION,
                message="No selection start marker exists.",
                next_steps=["Set a selection start marker first."],
            )

        target = min(max(start_caret, 0), len(context.buffer))
        context.caret = target
        self._record_marker_metric(context.app_id, "jumpStartSuccess")
        return RuntimeResult(
            ok=True,
            message="Jumped to selection start.",
            payload={
                "caret": target,
                "guidedFlow": self._selection_guided_flow_payload(context, stage="status"),
            },
            next_steps=["Use normal selection keys to extend from this anchor, then mark selection end."],
        )

    def cancel_selection(self, context: AppContext) -> RuntimeResult:
        self._selection_markers.pop(context.app_id, None)
        self._selection_cache.pop(context.app_id, None)
        self._record_marker_metric(context.app_id, "cancelSelection")
        return RuntimeResult(
            ok=True,
            message="Selection markers cleared.",
            payload={"guidedFlow": self._selection_guided_flow_payload(context, stage="cancelled")},
            next_steps=["Set selection start marker to begin a new range."],
        )

    def copy_to_slot(self, context: AppContext, slot: Optional[int] = None, text: Optional[str] = None) -> RuntimeResult:
        slot_number = self._resolve_slot_number(slot)
        slot_ref, slot_err = self._slot_or_error(slot_number)
        if slot_err is not None:
            return slot_err

        assert slot_ref is not None
        if slot_ref.protected:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.PROTECTED_SLOT,
                message=f"Slot {slot_number} is protected and cannot be overwritten.",
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
            message=f"Copied content to slot {slot_number}.",
            payload={"slot": slot_number, "activeSlot": self._active_slot, "length": len(content)},
        )

    def paste_from_slot(self, slot: Optional[int] = None) -> RuntimeResult:
        slot_number = self._resolve_slot_number(slot)
        slot_ref, slot_err = self._slot_or_error(slot_number)
        if slot_err is not None:
            return slot_err

        assert slot_ref is not None
        if slot_ref.item is None:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.EMPTY_SLOT,
                message=f"Slot {slot_number} is empty.",
                next_steps=["Copy content into the slot first."],
            )

        return RuntimeResult(
            ok=True,
            message=f"Ready to paste from slot {slot_number}.",
            payload={
                "slot": slot_number,
                "activeSlot": self._active_slot,
                "content": slot_ref.item.content,
                "sourceApp": slot_ref.item.source_app,
                "length": slot_ref.item.length,
            },
        )

    def protect_slot(self, slot: Optional[int] = None) -> RuntimeResult:
        slot_number = self._resolve_slot_number(slot)
        slot_ref, slot_err = self._slot_or_error(slot_number)
        if slot_err is not None:
            return slot_err
        assert slot_ref is not None

        slot_ref.protected = True
        self.save_slots()
        return RuntimeResult(ok=True, message=f"Slot {slot_number} is now protected.")

    def unprotect_slot(self, slot: Optional[int] = None) -> RuntimeResult:
        slot_number = self._resolve_slot_number(slot)
        slot_ref, slot_err = self._slot_or_error(slot_number)
        if slot_err is not None:
            return slot_err
        assert slot_ref is not None

        slot_ref.protected = False
        self.save_slots()
        return RuntimeResult(ok=True, message=f"Slot {slot_number} is now unprotected.")

    def delete_slot(self, slot: Optional[int] = None) -> RuntimeResult:
        slot_number = self._resolve_slot_number(slot)
        slot_ref, slot_err = self._slot_or_error(slot_number)
        if slot_err is not None:
            return slot_err
        assert slot_ref is not None

        if slot_ref.protected:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.PROTECTED_SLOT,
                message=f"Slot {slot_number} is protected and cannot be deleted.",
                next_steps=["Unprotect the slot first."],
            )

        slot_ref.item = None
        self.save_slots()
        return RuntimeResult(
            ok=True,
            message=f"Deleted content from slot {slot_number}.",
            payload={"slot": slot_number, "activeSlot": self._active_slot},
        )

    def edit_slot(self, slot: Optional[int], content: str) -> RuntimeResult:
        slot_number = self._resolve_slot_number(slot)
        slot_ref, slot_err = self._slot_or_error(slot_number)
        if slot_err is not None:
            return slot_err
        assert slot_ref is not None

        if slot_ref.item is None:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.EMPTY_SLOT,
                message=f"Slot {slot_number} is empty and cannot be edited.",
                next_steps=["Copy content into the slot first."],
            )

        if slot_ref.protected:
            return RuntimeResult(
                ok=False,
                code=RuntimeErrorCode.PROTECTED_SLOT,
                message=f"Slot {slot_number} is protected and cannot be edited.",
                next_steps=["Unprotect the slot first."],
            )

        slot_ref.item.content = content
        slot_ref.item.length = len(content)
        self.save_slots()
        return RuntimeResult(
            ok=True,
            message=f"Edited slot {slot_number}.",
            payload={"slot": slot_number, "activeSlot": self._active_slot, "length": len(content)},
        )

    def describe_slot(self, slot: Optional[int] = None) -> RuntimeResult:
        slot_number = self._resolve_slot_number(slot)
        slot_ref, slot_err = self._slot_or_error(slot_number)
        if slot_err is not None:
            return slot_err
        assert slot_ref is not None

        if slot_ref.item is None:
            return RuntimeResult(
                ok=True,
                message=f"Slot {slot_number} is empty.",
                payload={"slot": slot_number, "activeSlot": self._active_slot, "empty": True, "protected": slot_ref.protected},
            )

        return RuntimeResult(
            ok=True,
            message=f"Slot {slot_number} has content.",
            payload={
                "slot": slot_number,
                "activeSlot": self._active_slot,
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
