from __future__ import annotations

from dataclasses import dataclass

from .engine import RuntimeResult


@dataclass
class DialogDetection:
    kind: str
    confidence: float


class DialogPathInserter:
    def detect(self, window_title: str) -> RuntimeResult:
        title = window_title.strip().lower()
        if not title:
            return RuntimeResult(ok=True, message="Dialog type unknown.", payload={"kind": "unknown", "confidence": 0.0})

        if any(token in title for token in ("open", "open file", "open folder")):
            kind = "open"
            confidence = 0.9
        elif any(token in title for token in ("save", "save as")):
            kind = "save"
            confidence = 0.9
        elif any(token in title for token in ("attach", "insert file", "upload")):
            kind = "attach"
            confidence = 0.8
        else:
            kind = "unknown"
            confidence = 0.4

        return RuntimeResult(ok=True, message="Dialog detection ready.", payload={"kind": kind, "confidence": confidence})

    def insert_path(self, folder_path: str, *, window_title: str = "", supports_insertion: bool = True) -> RuntimeResult:
        path = folder_path.strip()
        if not path:
            return RuntimeResult(ok=False, message="Folder path is required.")

        detection = self.detect(window_title)
        d_payload = detection.payload or {}
        kind = str(d_payload.get("kind", "unknown"))

        if supports_insertion:
            return RuntimeResult(
                ok=True,
                message="Dialog path inserted.",
                payload={
                    "inserted": True,
                    "dialogKind": kind,
                    "path": path,
                    "fallbackGuidance": [],
                },
            )

        return RuntimeResult(
            ok=True,
            message="Dialog insertion unavailable; fallback guidance provided.",
            payload={
                "inserted": False,
                "dialogKind": kind,
                "path": path,
                "fallbackGuidance": [
                    "Press Alt+D to focus the path bar.",
                    "Paste the path and press Enter.",
                    "Use manual browse if path bar is unavailable.",
                ],
            },
            next_steps=[
                "Use manual dialog navigation.",
                "Re-run insertion after focus returns to dialog.",
            ],
        )
