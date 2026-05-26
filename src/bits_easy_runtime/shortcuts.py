from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from .engine import RuntimeResult


@dataclass
class ShortcutEntry:
    shortcut_id: str
    name: str
    target: str
    target_type: str
    category: str = "general"


class ShortcutsStore:
    _DEFAULT_LAUNCHER_APPS = ["edge", "outlook", "vscode"]

    def __init__(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self._shortcuts: Dict[str, ShortcutEntry] = {}
        self._presets: Dict[str, List[str]] = {}
        self._launcher: List[str] = []
        self._drive_mappings: Dict[str, str] = {}
        self._load()
        self._ensure_default_launcher_entries()

    def _next_id(self, target: str, target_type: str) -> str:
        digest = hashlib.sha1(f"{target_type}:{target}".encode("utf-8")).hexdigest()[:10]
        return f"sc-{digest}"

    def _ensure_default_launcher_entries(self) -> None:
        changed = False
        for app_id in self._DEFAULT_LAUNCHER_APPS:
            sid = self._next_id(app_id, "app")
            if sid not in self._shortcuts:
                self._shortcuts[sid] = ShortcutEntry(
                    shortcut_id=sid,
                    name=app_id.upper(),
                    target=app_id,
                    target_type="app",
                    category="launcher",
                )
                changed = True
            if sid not in self._launcher:
                self._launcher.append(sid)
                changed = True
        if changed:
            self._save()

    def _serialize(self) -> dict:
        return {
            "version": 1,
            "shortcuts": {
                sid: {
                    "name": item.name,
                    "target": item.target,
                    "targetType": item.target_type,
                    "category": item.category,
                }
                for sid, item in self._shortcuts.items()
            },
            "presets": self._presets,
            "launcher": self._launcher,
            "driveMappings": self._drive_mappings,
        }

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            payload = json.loads(self.storage_path.read_text(encoding="utf-8"))
            for sid, row in (payload.get("shortcuts", {}) or {}).items():
                self._shortcuts[sid] = ShortcutEntry(
                    shortcut_id=sid,
                    name=str(row.get("name", sid)),
                    target=str(row.get("target", "")),
                    target_type=str(row.get("targetType", "file")),
                    category=str(row.get("category", "general")),
                )
            self._presets = {str(k): [str(x) for x in v] for k, v in (payload.get("presets", {}) or {}).items()}
            self._launcher = [str(x) for x in (payload.get("launcher", []) or [])]
            self._drive_mappings = {
                str(k).upper(): str(v)
                for k, v in (payload.get("driveMappings", {}) or {}).items()
                if str(k).strip()
            }
        except Exception:
            self._shortcuts = {}
            self._presets = {}
            self._launcher = []
            self._drive_mappings = {}

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(json.dumps(self._serialize(), indent=2), encoding="utf-8")

    def _validate_target(self, target_type: str, target: str) -> str:
        t = target.strip()
        if not t:
            return "Target cannot be empty."
        if target_type == "web" and not (t.startswith("http://") or t.startswith("https://")):
            return "Web target must start with http:// or https://."
        if target_type not in ("file", "folder", "web", "app"):
            return "targetType must be file, folder, web, or app."
        return ""

    def create_shortcut(self, *, name: str, target: str, target_type: str) -> RuntimeResult:
        target_type = target_type.strip().lower()
        err = self._validate_target(target_type, target)
        if err:
            return RuntimeResult(ok=False, message=err)

        sid = self._next_id(target.strip(), target_type)
        existing = self._shortcuts.get(sid)
        if existing:
            return RuntimeResult(ok=True, message="Shortcut already exists.", payload={"shortcutId": sid})

        self._shortcuts[sid] = ShortcutEntry(
            shortcut_id=sid,
            name=name.strip() or sid,
            target=target.strip(),
            target_type=target_type,
        )
        self._save()
        return RuntimeResult(ok=True, message="Shortcut created.", payload={"shortcutId": sid})

    def list_shortcuts(self, *, target_type: str = "", category: str = "") -> RuntimeResult:
        rows = list(self._shortcuts.values())
        if target_type:
            rows = [r for r in rows if r.target_type == target_type]
        if category:
            rows = [r for r in rows if r.category == category]
        rows.sort(key=lambda r: (r.category, r.name.lower(), r.shortcut_id))
        return RuntimeResult(
            ok=True,
            message="Shortcut list ready.",
            payload={
                "items": [
                    {
                        "shortcutId": r.shortcut_id,
                        "name": r.name,
                        "target": r.target,
                        "targetType": r.target_type,
                        "category": r.category,
                    }
                    for r in rows
                ]
            },
        )

    def get_shortcut(self, shortcut_id: str) -> RuntimeResult:
        sid = shortcut_id.strip()
        row = self._shortcuts.get(sid)
        if row is None:
            return RuntimeResult(ok=False, message="Shortcut not found.")
        return RuntimeResult(
            ok=True,
            message="Shortcut resolved.",
            payload={
                "shortcutId": row.shortcut_id,
                "name": row.name,
                "target": row.target,
                "targetType": row.target_type,
                "category": row.category,
            },
        )

    def assign_category(self, shortcut_id: str, category: str) -> RuntimeResult:
        sid = shortcut_id.strip()
        row = self._shortcuts.get(sid)
        if not row:
            return RuntimeResult(ok=False, message="Shortcut not found.")
        row.category = category.strip() or "general"
        self._save()
        return RuntimeResult(ok=True, message="Shortcut category updated.", payload={"shortcutId": sid, "category": row.category})

    def create_preset(self, preset_name: str, shortcut_ids: List[str]) -> RuntimeResult:
        name = preset_name.strip()
        if not name:
            return RuntimeResult(ok=False, message="Preset name cannot be empty.")
        valid = [sid for sid in shortcut_ids if sid in self._shortcuts]
        self._presets[name] = valid
        self._save()
        return RuntimeResult(ok=True, message="Preset saved.", payload={"preset": name, "count": len(valid)})

    def run_preset(self, preset_name: str) -> RuntimeResult:
        name = preset_name.strip()
        ids = self._presets.get(name)
        if ids is None:
            return RuntimeResult(ok=False, message="Preset not found.")
        items = []
        for sid in ids:
            row = self._shortcuts.get(sid)
            if row:
                items.append(
                    {
                        "shortcutId": row.shortcut_id,
                        "name": row.name,
                        "target": row.target,
                        "targetType": row.target_type,
                    }
                )
        return RuntimeResult(ok=True, message="Preset launch list ready.", payload={"preset": name, "items": items})

    def add_to_launcher(self, shortcut_id: str) -> RuntimeResult:
        sid = shortcut_id.strip()
        if sid not in self._shortcuts:
            return RuntimeResult(ok=False, message="Shortcut not found.")
        if sid not in self._launcher:
            self._launcher.append(sid)
            self._save()
        return RuntimeResult(ok=True, message="Shortcut added to launcher.", payload={"shortcutId": sid, "launcherCount": len(self._launcher)})

    def add_focused_app(self, app_id: str) -> RuntimeResult:
        app = app_id.strip().lower()
        if not app:
            return RuntimeResult(ok=False, message="Focused app id is required.")

        sid = self._next_id(app, "app")
        if sid not in self._shortcuts:
            self._shortcuts[sid] = ShortcutEntry(
                shortcut_id=sid,
                name=app.upper(),
                target=app,
                target_type="app",
                category="launcher",
            )
        if sid not in self._launcher:
            self._launcher.append(sid)
        self._save()
        return RuntimeResult(ok=True, message="Focused app added to launcher.", payload={"shortcutId": sid, "appId": app})

    def remove_from_launcher(self, shortcut_id: str) -> RuntimeResult:
        sid = shortcut_id.strip()
        if sid not in self._launcher:
            return RuntimeResult(ok=False, message="Shortcut is not in launcher.")
        self._launcher = [x for x in self._launcher if x != sid]
        self._save()
        return RuntimeResult(ok=True, message="Launcher entry removed.", payload={"shortcutId": sid, "launcherCount": len(self._launcher)})

    def restore_launcher_defaults(self) -> RuntimeResult:
        self._launcher = []
        self._ensure_default_launcher_entries()
        return RuntimeResult(ok=True, message="Launcher defaults restored.", payload={"launcherCount": len(self._launcher)})

    def list_launcher(self) -> RuntimeResult:
        items = []
        for sid in self._launcher:
            row = self._shortcuts.get(sid)
            if not row:
                continue
            items.append(
                {
                    "shortcutId": row.shortcut_id,
                    "name": row.name,
                    "target": row.target,
                    "targetType": row.target_type,
                    "category": row.category,
                }
            )
        return RuntimeResult(ok=True, message="Launcher list ready.", payload={"items": items, "count": len(items)})

    def map_drive(self, drive_letter: str, folder_path: str) -> RuntimeResult:
        letter = drive_letter.strip().upper().replace(":", "")
        folder = folder_path.strip()
        if len(letter) != 1 or not letter.isalpha():
            return RuntimeResult(ok=False, message="Drive letter must be a single A-Z letter.")
        if not folder:
            return RuntimeResult(ok=False, message="Folder path is required.")
        self._drive_mappings[letter] = folder
        self._save()
        return RuntimeResult(ok=True, message="Drive mapping saved.", payload={"driveLetter": f"{letter}:", "folder": folder})

    def unmap_drive(self, drive_letter: str) -> RuntimeResult:
        letter = drive_letter.strip().upper().replace(":", "")
        if letter not in self._drive_mappings:
            return RuntimeResult(ok=False, message="Drive mapping not found.")
        folder = self._drive_mappings[letter]
        del self._drive_mappings[letter]
        self._save()
        return RuntimeResult(ok=True, message="Drive mapping removed.", payload={"driveLetter": f"{letter}:", "folder": folder})

    def list_drive_mappings(self) -> RuntimeResult:
        items = [
            {"driveLetter": f"{letter}:", "folder": folder}
            for letter, folder in sorted(self._drive_mappings.items())
        ]
        return RuntimeResult(ok=True, message="Drive mappings ready.", payload={"items": items, "count": len(items)})
