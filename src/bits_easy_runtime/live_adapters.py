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
    provider_kind: str = "focus"
    selected_text_kind: str = ""
    text_kind: str = ""
    layout_signature: str = ""


_INTERACTIVE_ROLE_TOKENS = (
    "link",
    "button",
    "menuitem",
    "listitem",
    "treeviewitem",
    "tab",
    "checkbox",
    "radio",
)


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


def _is_interactive_role(role: str) -> bool:
    lowered = role.lower()
    return any(token in lowered for token in _INTERACTIVE_ROLE_TOKENS)


def _get_text_provider(focus: Any) -> Any:
    tree = getattr(focus, "treeInterceptor", None)
    pass_through = bool(getattr(tree, "passThrough", False)) if tree is not None else True
    if tree is not None and not pass_through:
        return tree
    return focus


def _provider_kind(focus: Any, provider: Any) -> str:
    tree = getattr(focus, "treeInterceptor", None)
    if tree is not None and provider is tree:
        return "interceptor"
    return "focus"


def _make_text_info(provider: Any, modes: tuple[Any, ...]) -> Optional[Any]:
    make_info = getattr(provider, "makeTextInfo", None)
    if not callable(make_info):
        return None
    for mode in modes:
        try:
            return make_info(mode)
        except Exception:
            continue
    return None


def _offset_from_bookmark(bookmark: Any, prefer_end: bool = False) -> Optional[int]:
    if bookmark is None:
        return None

    attr = "endOffset" if prefer_end else "startOffset"
    try:
        value = getattr(bookmark, attr, None)
        if value is not None:
            return int(value)
    except Exception:
        pass

    if isinstance(bookmark, (tuple, list)) and bookmark:
        index = 1 if prefer_end and len(bookmark) > 1 else 0
        try:
            return int(bookmark[index])
        except Exception:
            return None

    return None


def _range_from_info(info: Any) -> tuple[Optional[int], Optional[int]]:
    bookmark = getattr(info, "bookmark", None)
    start = _offset_from_bookmark(bookmark, prefer_end=False)
    end = _offset_from_bookmark(bookmark, prefer_end=True)
    if start is None and end is not None:
        start = end
    if end is None and start is not None:
        end = start
    return start, end


def app_id_from_focus_object(focus: Any) -> str:
    app_name = _coerce_str(_safe_getattr_chain(focus, ["appModule", "appName"], "")).lower()
    if "outlook" in app_name:
        return "outlook"
    if "winword" in app_name or app_name == "word":
        return "word"
    if app_name in ("msedge", "chrome", "firefox"):
        return app_name.replace("msedge", "edge")
    if app_name in ("code", "code-insiders", "vscode"):
        return "vscode"
    if app_name.startswith("notepad"):
        return "notepad"
    if app_name:
        return app_name
    return "nvda"


def detect_outlook_variant(focus: Any) -> str:
    role = _coerce_str(getattr(focus, "role", ""), "").lower()
    name = _coerce_str(getattr(focus, "name", ""), "").lower()
    value = _coerce_str(getattr(focus, "value", ""), "").lower()

    if "search results" in name or "results list" in name:
        return "search-results"
    if "search" in name or "find" in name:
        return "search"
    if "ribbon" in name or "toolbar" in name or "command bar" in name:
        return "ribbon"
    if "folder pane" in name or "navigation pane" in name or "folder tree" in name:
        return "folder-pane"
    if "message list" in name or "mail list" in name or "thread list" in name or "list" in role or "tree" in role:
        return "message-list"
    if "reading pane" in name or "preview pane" in name or "reading" in value:
        return "reading-pane"
    if "document" in role or "edit" in role or "compose" in name or "editor" in name:
        return "compose"
    return "other"


def detect_outlook_layout_signature(focus: Any) -> str:
    role = _coerce_str(getattr(focus, "role", ""), "").lower()
    name = _coerce_str(getattr(focus, "name", ""), "").lower()
    value = _coerce_str(getattr(focus, "value", ""), "").lower()

    if "search results" in name or "results list" in name:
        return "outlook-layout-search-results"
    if "search" in name or "find" in name:
        return "outlook-layout-search"
    if "ribbon" in name or "toolbar" in name or "command bar" in name:
        return "outlook-layout-ribbon"
    if "folder pane" in name or "navigation pane" in name or "folder tree" in name:
        return "outlook-layout-folder-pane"
    if "message list" in name or "mail list" in name or "thread list" in name or "list" in role or "tree" in role:
        return "outlook-layout-message-list"
    if "reading pane" in name or "preview pane" in name or "reading" in value:
        return "outlook-layout-reading-pane"
    if "document" in role or "edit" in role or "compose" in name or "editor" in name:
        return "outlook-layout-compose"
    return "outlook-layout-unknown"


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

    provider = _get_text_provider(focus)
    provider_kind = _provider_kind(focus, provider)
    selected_text_kind = ""
    text_kind = ""

    selection_info = _make_text_info(provider, ("selection", "sel", "range"))
    if selection_info is not None:
        selected_text = _coerce_str(getattr(selection_info, "text", ""), "")
        selection_start, selection_end = _range_from_info(selection_info)
        if selected_text:
            selected_text_kind = f"native-{provider_kind}-selection"

    all_info = _make_text_info(provider, ("all", "document", "story", "first"))
    if all_info is not None:
        text = _coerce_str(getattr(all_info, "text", ""), "")
        if text:
            text_kind = f"native-{provider_kind}-text"

    caret_info = _make_text_info(provider, ("caret", "insertionPoint", "point", "first"))
    if caret_info is not None:
        caret_start, _ = _range_from_info(caret_info)
        if caret_start is not None:
            caret = caret_start

    # Fallbacks for browser/outlook objects that expose value-like content.
    if not text:
        text = _coerce_str(getattr(focus, "value", ""), "")
        if text and not text_kind:
            text_kind = "value-fallback"

    # Interactive virtualized surfaces often expose names even when text APIs are sparse.
    if not text and _is_interactive_role(role):
        text = _coerce_str(getattr(focus, "name", ""), "") or _coerce_str(getattr(focus, "description", ""), "")
        if text:
            text_kind = "interactive-label-fallback"
    if not selected_text and _is_interactive_role(role):
        selected_text = text
        if selected_text:
            selected_text_kind = "interactive-label-fallback"

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
        variant=detect_outlook_variant(focus) if app_id == "outlook" else "",
        provider_kind=provider_kind,
        selected_text_kind=selected_text_kind,
        text_kind=text_kind,
        layout_signature=detect_outlook_layout_signature(focus) if app_id == "outlook" else "",
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
                    source_kind=snapshot.selected_text_kind or f"native-{snapshot.provider_kind}-selection",
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
                        source_kind=f"native-{snapshot.provider_kind}-range",
                    )

                if _is_interactive_role(snapshot.role):
                    return SelectionRange(
                        app_id=self.app_id,
                        start=0,
                        end=len(snapshot.text),
                        text=snapshot.text,
                        confidence=0.75,
                        source_kind="interactive-label-fallback",
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


class OutlookLiveAdapter(LiveFocusSelectionAdapter):
    def __init__(self, snapshot_provider: Callable[[], Optional[FocusSnapshot]]):
        # Outlook has many surfaces where selection is unavailable; keep support but allow fallback.
        super().__init__(app_id="outlook", snapshot_provider=snapshot_provider, supports_selection=True)

    def normalize_range(self, context: AppContext, start: int, end: int) -> SelectionRange:
        snapshot = self._snapshot_provider()
        if snapshot is not None:
            if snapshot.variant == "message-list":
                signature = snapshot.layout_signature or "outlook-layout-message-list"
                raise UnsupportedSurfaceError(
                    f"Outlook message list rows do not expose stable text selections. Layout signature: {signature}."
                )

        return super().normalize_range(context, start, end)


class BrowserLiveAdapter(LiveFocusSelectionAdapter):
    def __init__(self, app_id: str, snapshot_provider: Callable[[], Optional[FocusSnapshot]]):
        super().__init__(app_id=app_id, snapshot_provider=snapshot_provider, supports_selection=True)
