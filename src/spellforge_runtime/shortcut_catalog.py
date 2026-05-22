from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .diagnostics import get_logger
from .engine import RuntimeResult

_logger = get_logger("spellforge.shortcut_catalog")


@dataclass
class ShortcutItem:
    shortcut_id: str
    name: str
    target: str
    target_type: str
    category: str = "general"


class ShortcutCatalogStore:
    def __init__(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self._shortcuts: Dict[str, ShortcutItem] = {}
        self._presets: Dict[str, List[str]] = {}
        self._load()

    def _next_id(self, target: str) -> str:
        digest = hashlib.sha1(target.encode("utf-8")).hexdigest()[:8]
        return f"cut-{digest}"

    def _validate_target(self, target_type: str, target: str) -> Optional[str]:
        t = target.strip()
        if not t:
            return "Target cannot be empty."
        if target_type == "web" and not (t.startswith("http://") or t.startswith("https://")):
            return "Web shortcut target must start with http:// or https://."
        if target_type in ("file", "folder"):
            # For portability and testing we validate non-empty only, not existence.
            return None
        return None

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
        }

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            payload = json.loads(self.storage_path.read_text(encoding="utf-8"))
            for sid, item in (payload.get("shortcuts", {}) or {}).items():
                self._shortcuts[sid] = ShortcutItem(
                    shortcut_id=sid,
                    name=str(item.get("name", sid)),
                    target=str(item.get("target", "")),
                    target_type=str(item.get("targetType", "file")),
                    category=str(item.get("category", "general")),
                )
            self._presets = {k: [str(x) for x in v] for k, v in (payload.get("presets", {}) or {}).items()}
        except Exception:
            _logger.exception("Spellforge: loading shortcut catalog at %s failed", self.storage_path)
            self._shortcuts = {}
            self._presets = {}

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(json.dumps(self._serialize(), indent=2), encoding="utf-8")

    def create_shortcut(self, *, name: str, target: str, target_type: str) -> RuntimeResult:
        target_type = target_type.strip().lower()
        if target_type not in ("file", "folder", "web"):
            return RuntimeResult(ok=False, message="targetType must be file, folder, or web.")

        err = self._validate_target(target_type, target)
        if err:
            return RuntimeResult(ok=False, message=err)

        sid = self._next_id(target)
        # De-duplicate by target and type.
        for existing in self._shortcuts.values():
            if existing.target == target and existing.target_type == target_type:
                return RuntimeResult(ok=True, message="Shortcut already exists.", payload={"shortcutId": existing.shortcut_id})

        item = ShortcutItem(shortcut_id=sid, name=name.strip() or sid, target=target.strip(), target_type=target_type)
        self._shortcuts[sid] = item
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
            message="Shortcut Catalog list ready.",
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

    def delete_shortcut(self, shortcut_id: str) -> RuntimeResult:
        sid = shortcut_id.strip()
        if sid not in self._shortcuts:
            return RuntimeResult(ok=False, message="Shortcut not found.")
        del self._shortcuts[sid]
        # Remove from presets.
        for preset, sids in list(self._presets.items()):
            self._presets[preset] = [x for x in sids if x != sid]
        self._save()
        return RuntimeResult(ok=True, message="Shortcut deleted.", payload={"shortcutId": sid})

    def assign_category(self, shortcut_id: str, category: str) -> RuntimeResult:
        sid = shortcut_id.strip()
        item = self._shortcuts.get(sid)
        if not item:
            return RuntimeResult(ok=False, message="Shortcut not found.")
        item.category = category.strip() or "general"
        self._save()
        return RuntimeResult(ok=True, message="Shortcut category updated.", payload={"shortcutId": sid, "category": item.category})

    def create_preset(self, preset_name: str, shortcut_ids: List[str]) -> RuntimeResult:
        name = preset_name.strip()
        if not name:
            return RuntimeResult(ok=False, message="Preset name cannot be empty.")
        valid_ids = [sid for sid in shortcut_ids if sid in self._shortcuts]
        self._presets[name] = valid_ids
        self._save()
        return RuntimeResult(ok=True, message="Preset saved.", payload={"preset": name, "count": len(valid_ids)})

    def launch_shortcut(self, shortcut_id: str) -> RuntimeResult:
        sid = shortcut_id.strip()
        item = self._shortcuts.get(sid)
        if not item:
            return RuntimeResult(ok=False, message="Shortcut not found.")
        return RuntimeResult(
            ok=True,
            message="Shortcut launch prepared.",
            payload={
                "shortcutId": item.shortcut_id,
                "name": item.name,
                "target": item.target,
                "targetType": item.target_type,
            },
        )

    def run_preset(self, preset_name: str) -> RuntimeResult:
        name = preset_name.strip()
        ids = self._presets.get(name)
        if ids is None:
            return RuntimeResult(ok=False, message="Preset not found.")
        launched = []
        for sid in ids:
            item = self._shortcuts.get(sid)
            if item:
                launched.append({"shortcutId": item.shortcut_id, "name": item.name, "target": item.target})
        return RuntimeResult(ok=True, message="Preset launch list ready.", payload={"preset": name, "items": launched})

    def export_presets(self, out_path: Path | str) -> RuntimeResult:
        out = Path(out_path)
        payload = {
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
        }
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        payload["integrity"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return RuntimeResult(ok=True, message="Shortcut Catalog presets exported.", payload={"path": str(out)})

    def import_presets(self, in_path: Path | str, *, overwrite: bool = False) -> RuntimeResult:
        src = Path(in_path)
        if not src.exists():
            return RuntimeResult(ok=False, message="Preset pack not found.")
        try:
            payload = json.loads(src.read_text(encoding="utf-8"))
        except Exception:
            return RuntimeResult(ok=False, message="Preset pack malformed.")

        base = {
            "version": payload.get("version", 0),
            "shortcuts": payload.get("shortcuts", {}),
            "presets": payload.get("presets", {}),
        }
        if base["version"] != 1:
            return RuntimeResult(ok=False, message="Preset pack incompatible version.")

        integrity = str(payload.get("integrity", ""))
        expected = hashlib.sha256(json.dumps(base, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
        if integrity and integrity != expected:
            return RuntimeResult(ok=False, message="Preset pack integrity check failed.")

        conflicts = 0
        imported = 0
        for sid, row in (base["shortcuts"] or {}).items():
            if sid in self._shortcuts and not overwrite:
                conflicts += 1
                continue
            self._shortcuts[sid] = ShortcutItem(
                shortcut_id=sid,
                name=str(row.get("name", sid)),
                target=str(row.get("target", "")),
                target_type=str(row.get("targetType", "file")),
                category=str(row.get("category", "general")),
            )
            imported += 1

        for preset, ids in (base["presets"] or {}).items():
            if preset in self._presets and not overwrite:
                conflicts += 1
                continue
            self._presets[str(preset)] = [str(x) for x in ids]

        self._save()
        return RuntimeResult(ok=True, message="Shortcut Catalog presets imported.", payload={"imported": imported, "conflicts": conflicts})
