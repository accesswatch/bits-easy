from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class SurfaceContext:
    app_id: str
    mode: str
    role: str
    control_id: str


def classify_surface(app_id: str, role: str, control_id: str) -> SurfaceContext:
    role_l = (role or "").lower()
    control_l = (control_id or "").lower()
    app_l = (app_id or "").lower()

    if app_l == "outlook":
        if "edit" in role_l or "document" in role_l or "compose" in control_l or "editor" in control_l:
            return SurfaceContext(app_id=app_l, mode="outlook-compose", role=role_l, control_id=control_l)
        if "list" in role_l or "tree" in role_l or "message list" in control_l:
            return SurfaceContext(app_id=app_l, mode="outlook-message-list", role=role_l, control_id=control_l)
        return SurfaceContext(app_id=app_l, mode="outlook-other", role=role_l, control_id=control_l)

    if app_l in ("edge", "chrome", "firefox"):
        if "document" in role_l:
            return SurfaceContext(app_id=app_l, mode="browser-document", role=role_l, control_id=control_l)
        if "edit" in role_l:
            return SurfaceContext(app_id=app_l, mode="browser-editable", role=role_l, control_id=control_l)
        return SurfaceContext(app_id=app_l, mode="browser-other", role=role_l, control_id=control_l)

    if app_l == "word":
        if "document" in role_l or "edit" in role_l:
            return SurfaceContext(app_id=app_l, mode="word-document", role=role_l, control_id=control_l)
        return SurfaceContext(app_id=app_l, mode="word-other", role=role_l, control_id=control_l)

    return SurfaceContext(app_id=app_l or "nvda", mode="generic", role=role_l, control_id=control_l)


def fallback_steps_for(mode: str, command_id: str) -> List[str]:
    if mode == "outlook-message-list":
        return [
            "Open the message first, then retry selection commands.",
            "Use quick capture to inbox for list-row summaries.",
        ]
    if mode == "outlook-compose":
        return [
            "Retry after moving caret into the compose body.",
            "Use clipboard fallback capture if selection is unavailable.",
        ]
    if mode == "browser-document":
        return [
            "Switch to browse mode selection and retry.",
            "Use the virtualized result fallback menu.",
        ]
    if mode == "browser-editable":
        return [
            "Retry in the focused edit field.",
            "Use copy to slot from clipboard fallback.",
        ]
    if mode == "word-document":
        return [
            "Retry after selecting text in the active document.",
            "Use selection context readback for confidence check.",
        ]

    if command_id.startswith("cmd.clip"):
        return [
            "Try copy to slot from clipboard fallback.",
            "Open hotkey diagnostics for command guidance.",
        ]
    return ["Open fallback actions from the command palette."]
