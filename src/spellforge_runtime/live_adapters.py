from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional

from .engine import AppAdapter, AppContext, RestoreResult, SelectionRange, SourceAnchor, UnsupportedSurfaceError


@dataclass
class FocusSnapshot:
    app_id: str
    window_id: str
    control_id: str
    role: str
    text: str
    caret: int
    selection_start: Optional[int] = None
    selection_end: Optional[int] = None
    selected_text: str = ""
    variant: str = ""


def _safe_getattr_chain(obj: Any, chain: list[str], default: Any = None) -> Any:
    current = obj
    for attr in chain:
        if current is None:
            return default
        current = getattr(current, attr, None)
    return current if current is not None else default


def _coerce_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    try:
        return str(value)
    except Exception:
        return default


def app_id_from_focus_object(focus: Any) -> str:
    app_name = _coerce_str(_safe_getattr_chain(focus, ["appModule", "appName"], "")).lower()
    if "outlook" in app_name:
        return "outlook"
    if "winword" in app_name or app_name == "word":
        return "word"
    if app_name in ("msedge", "chrome", "firefox"):
        return app_name.replace("msedge", "edge")
    if app_name:
        return app_name
    return "nvda"


def detect_outlook_variant(focus: Any) -> str:
    role = _coerce_str(getattr(focus, "role", ""), "").lower()
    name = _coerce_str(getattr(focus, "name", ""), "").lower()
    value = _coerce_str(getattr(focus, "value", ""), "").lower()

    if "message list" in name or "list" in role or "tree" in role:
        return "message-list"
    if "reading pane" in name or "reading" in value:
        return "reading-pane"
    if "document" in role or "edit" in role or "compose" in name or "editor" in name:
        return "compose"
    return "other"


def detect_word_variant(focus: Any) -> str:
    role = _coerce_str(getattr(focus, "role", ""), "").lower()
    name = _coerce_str(getattr(focus, "name", ""), "").lower()
    if "document" in role or "edit" in role:
        return "document"
    if "table" in role or "cell" in role:
        return "table"
    if "comment" in name or "track changes" in name:
        return "review-pane"
    return "other"


def snapshot_from_focus_object(focus: Any) -> FocusSnapshot:
    app_id = app_id_from_focus_object(focus)
    window_id = _coerce_str(getattr(focus, "windowHandle", ""), "")
    control_id = _coerce_str(getattr(focus, "name", ""), "") or _coerce_str(getattr(focus, "role", "focus"), "focus")
    role = _coerce_str(getattr(focus, "role", ""), "")

    # NVDA text APIs vary by object type. Use a broad, defensive extraction strategy.
    selected_text = ""
    selection_start: Optional[int] = None
    selection_end: Optional[int] = None
    text = ""
    caret = 0

    nav_text_obj = getattr(focus, "makeTextInfo", None)
    if callable(nav_text_obj):
        try:
            selection_info = nav_text_obj("selection")
            selected_text = _coerce_str(getattr(selection_info, "text", ""), "")
            start_obj = getattr(selection_info, "_start", None)
            end_obj = getattr(selection_info, "_end", None)
            selection_start = getattr(start_obj, "_offset", None)
            selection_end = getattr(end_obj, "_offset", None)
        except Exception:
            selected_text = ""

        try:
            all_info = nav_text_obj("all")
            text = _coerce_str(getattr(all_info, "text", ""), "")
        except Exception:
            text = ""

        try:
            caret_info = nav_text_obj("caret")
            start_obj = getattr(caret_info, "_start", None)
            caret = int(getattr(start_obj, "_offset", 0) or 0)
        except Exception:
            caret = 0

    # Fallbacks for browser/outlook objects that expose value-like content.
    if not text:
        text = _coerce_str(getattr(focus, "value", ""), "")

    return FocusSnapshot(
        app_id=app_id,
        window_id=window_id,
        control_id=control_id,
        role=role,
        text=text,
        caret=caret,
        selection_start=selection_start,
        selection_end=selection_end,
        selected_text=selected_text,
        variant=(
            detect_outlook_variant(focus)
            if app_id == "outlook"
            else detect_word_variant(focus)
            if app_id == "word"
            else ""
        ),
    )


class LiveFocusSelectionAdapter(AppAdapter):
    def __init__(self, app_id: str, snapshot_provider: Callable[[], Optional[FocusSnapshot]], supports_selection: bool = True):
        super().__init__(app_id=app_id, supports_selection=supports_selection)
        self._snapshot_provider = snapshot_provider

    def normalize_range(self, context: AppContext, start: int, end: int) -> SelectionRange:
        if not self.supports_selection:
            raise UnsupportedSurfaceError(
                f"Selection is not supported in {self.app_id} for this surface."
            )

        snapshot = self._snapshot_provider()
        if snapshot is not None:
            if snapshot.selected_text:
                lo = snapshot.selection_start if snapshot.selection_start is not None else min(start, end)
                hi = snapshot.selection_end if snapshot.selection_end is not None else max(start, end)
                return SelectionRange(
                    app_id=self.app_id,
                    start=int(lo),
                    end=int(hi),
                    text=snapshot.selected_text,
                    confidence=1.0,
                )

            if snapshot.text:
                lo = min(start, end)
                hi = max(start, end)
                if 0 <= lo < hi <= len(snapshot.text):
                    return SelectionRange(
                        app_id=self.app_id,
                        start=lo,
                        end=hi,
                        text=snapshot.text[lo:hi],
                        confidence=0.9,
                    )

        return super().normalize_range(context, start, end)

    def restore_anchor(self, anchor: SourceAnchor, context: AppContext) -> RestoreResult:
        snapshot = self._snapshot_provider()
        if snapshot is not None:
            if anchor.window_id != snapshot.window_id or anchor.control_id != snapshot.control_id:
                return RestoreResult(success=False, drift_detected=True, restored_caret=context.caret)
            if anchor.caret > len(snapshot.text):
                return RestoreResult(success=True, drift_detected=True, restored_caret=len(snapshot.text))
            return RestoreResult(success=True, drift_detected=False, restored_caret=anchor.caret)

        return super().restore_anchor(anchor, context)


class WordLiveAdapter(LiveFocusSelectionAdapter):
    def __init__(self, snapshot_provider: Callable[[], Optional[FocusSnapshot]]):
        super().__init__(app_id="word", snapshot_provider=snapshot_provider, supports_selection=True)

    def normalize_range(self, context: AppContext, start: int, end: int) -> SelectionRange:
        snapshot = self._snapshot_provider()
        if snapshot is not None:
            if snapshot.selected_text:
                return SelectionRange(
                    app_id=self.app_id,
                    start=int(snapshot.selection_start or min(start, end)),
                    end=int(snapshot.selection_end or max(start, end)),
                    text=snapshot.selected_text,
                    confidence=1.0,
                )

            if snapshot.variant in ("table", "review-pane") and snapshot.text:
                caret = max(0, min(len(snapshot.text), snapshot.caret))
                left = snapshot.text.rfind("\n", 0, caret)
                right = snapshot.text.find("\n", caret)
                lo = 0 if left < 0 else left + 1
                hi = len(snapshot.text) if right < 0 else right
                text = snapshot.text[lo:hi].strip()
                if text:
                    return SelectionRange(
                        app_id=self.app_id,
                        start=lo,
                        end=hi,
                        text=text,
                        confidence=0.8,
                    )

        return super().normalize_range(context, start, end)


class OutlookLiveAdapter(LiveFocusSelectionAdapter):
    def __init__(self, snapshot_provider: Callable[[], Optional[FocusSnapshot]]):
        # Outlook has many surfaces where selection is unavailable; keep support but allow fallback.
        super().__init__(app_id="outlook", snapshot_provider=snapshot_provider, supports_selection=True)

    def normalize_range(self, context: AppContext, start: int, end: int) -> SelectionRange:
        snapshot = self._snapshot_provider()
        if snapshot is not None:
            if snapshot.variant == "message-list":
                raise UnsupportedSurfaceError("Outlook message list rows do not expose stable text selections.")

            if snapshot.variant == "reading-pane" and snapshot.text:
                caret = max(0, min(len(snapshot.text), snapshot.caret))
                left = snapshot.text.rfind(".", 0, caret)
                right = snapshot.text.find(".", caret)
                lo = 0 if left < 0 else left + 1
                hi = len(snapshot.text) if right < 0 else right + 1
                text = snapshot.text[lo:hi].strip()
                if text:
                    return SelectionRange(
                        app_id=self.app_id,
                        start=lo,
                        end=hi,
                        text=text,
                        confidence=0.75,
                    )

        return super().normalize_range(context, start, end)


class BrowserLiveAdapter(LiveFocusSelectionAdapter):
    def __init__(self, app_id: str, snapshot_provider: Callable[[], Optional[FocusSnapshot]]):
        super().__init__(app_id=app_id, snapshot_provider=snapshot_provider, supports_selection=True)
