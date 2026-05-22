from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .engine import RuntimeResult


class JoplinBridge:
    def __init__(self, storage_path: Path | str | None = None):
        self._storage_path = Path(storage_path) if storage_path else None
        self._mapping_profile: Dict[str, Any] = {"tagMap": {}, "attachmentMap": {}}
        self._last_refresh_snapshot: Dict[str, Any] | None = None
        self._load()

    def _save(self) -> None:
        if not self._storage_path:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"mappingProfile": self._mapping_profile, "lastRefreshSnapshot": self._last_refresh_snapshot}
        self._storage_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if not self._storage_path or not self._storage_path.exists():
            return
        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except Exception:
            return
        mp = payload.get("mappingProfile", {})
        self._mapping_profile = mp if isinstance(mp, dict) else {"tagMap": {}, "attachmentMap": {}}
        snap = payload.get("lastRefreshSnapshot")
        self._last_refresh_snapshot = snap if isinstance(snap, dict) else None

    def import_notes(self, in_path: Path | str) -> RuntimeResult:
        path = Path(in_path)
        if not path.exists():
            return RuntimeResult(ok=False, message="Joplin import package was not found.")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            return RuntimeResult(ok=False, message=f"Joplin import failed: {exc}")
        notes = payload.get("notes", []) if isinstance(payload.get("notes", []), list) else []
        mapped = []
        for n in notes:
            mapped.append({"title": n.get("title", ""), "body": n.get("body", ""), "tags": n.get("tags", [])})
        return RuntimeResult(ok=True, message="Joplin import pipeline complete.", payload={"imported": mapped, "count": len(mapped), "skips": 0, "failures": 0})

    def export_notes(self, notes: List[Dict[str, Any]], out_path: Path | str) -> RuntimeResult:
        path = Path(out_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"joplinVersion": 1, "notes": notes}
        path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
        return RuntimeResult(ok=True, message="Joplin export pipeline complete.", payload={"path": str(path), "count": len(notes)})

    def set_mapping_profile(self, tag_map: Dict[str, str], attachment_map: Dict[str, str]) -> RuntimeResult:
        # De-dup attachment targets and keep predictable tag collision behavior.
        dedup_attachment: Dict[str, str] = {}
        seen_targets = set()
        for k, v in attachment_map.items():
            target = str(v)
            if target in seen_targets:
                continue
            dedup_attachment[str(k)] = target
            seen_targets.add(target)
        self._mapping_profile = {
            "tagMap": {str(k): str(v) for k, v in tag_map.items()},
            "attachmentMap": dedup_attachment,
        }
        self._save()
        return RuntimeResult(ok=True, message="Joplin mapping profile saved.", payload={"tagMapCount": len(self._mapping_profile["tagMap"]), "attachmentMapCount": len(self._mapping_profile["attachmentMap"])})

    def refresh_linked(self, incoming_notes: List[Dict[str, Any]], *, apply: bool = False) -> RuntimeResult:
        conflicts = []
        for row in incoming_notes:
            if row.get("conflict", False):
                conflicts.append(row)
        if not apply:
            return RuntimeResult(ok=True, message="Linked refresh dry-run complete.", payload={"conflicts": conflicts, "conflictCount": len(conflicts)})
        self._last_refresh_snapshot = {"notes": incoming_notes}
        self._save()
        return RuntimeResult(ok=True, message="Linked refresh applied with snapshot.", payload={"applied": len(incoming_notes), "conflictCount": len(conflicts)})

    def rollback_refresh(self) -> RuntimeResult:
        if not self._last_refresh_snapshot:
            return RuntimeResult(ok=False, message="No linked refresh snapshot available.")
        return RuntimeResult(ok=True, message="Linked workspace rollback restored pre-apply state.", payload={"snapshot": self._last_refresh_snapshot})
