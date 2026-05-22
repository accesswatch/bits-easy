from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from .engine import RuntimeResult, SpellforgeRuntime


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ClipRecord:
    clip_id: str
    content: str
    source_app: str
    created_at: str
    archive_state: str
    slot_id: Optional[int]
    slot_alias: Optional[str]
    categories: List[str]
    retention_policy: str
    folder_links: List[str]


class ClipLibraryStore:
    def __init__(self, runtime: SpellforgeRuntime, storage_path: Path | str):
        self.runtime = runtime
        self.storage_path = Path(storage_path)
        self._clips: Dict[str, ClipRecord] = {}
        self._folders: Dict[str, Dict[str, str]] = {}
        self._load()

    def _new_clip_id(self) -> str:
        return f"clip-{len(self._clips) + 1:04d}"

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            payload = json.loads(self.storage_path.read_text(encoding="utf-8"))
            for cid, row in (payload.get("clips", {}) or {}).items():
                self._clips[cid] = ClipRecord(
                    clip_id=cid,
                    content=str(row.get("content", "")),
                    source_app=str(row.get("sourceApp", "unknown")),
                    created_at=str(row.get("createdAt", _now())),
                    archive_state=str(row.get("archiveState", "active")),
                    slot_id=row.get("slotId"),
                    slot_alias=row.get("slotAlias"),
                    categories=[str(x) for x in (row.get("categories", []) or [])],
                    retention_policy=str(row.get("retentionPolicy", "keep-forever")),
                    folder_links=[str(x) for x in (row.get("folderLinks", []) or [])],
                )
            self._folders = {
                fid: {
                    "name": str(row.get("name", fid)),
                    "category": str(row.get("category", "general")),
                }
                for fid, row in (payload.get("folders", {}) or {}).items()
            }
        except Exception:
            self._clips = {}
            self._folders = {}

    def _save(self) -> None:
        payload = {
            "version": 1,
            "clips": {
                cid: {
                    "content": c.content,
                    "sourceApp": c.source_app,
                    "createdAt": c.created_at,
                    "archiveState": c.archive_state,
                    "slotId": c.slot_id,
                    "slotAlias": c.slot_alias,
                    "categories": c.categories,
                    "retentionPolicy": c.retention_policy,
                    "folderLinks": c.folder_links,
                }
                for cid, c in self._clips.items()
            },
            "folders": self._folders,
        }
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def ingest_slot(self, slot: int) -> RuntimeResult:
        desc = self.runtime.describe_slot(slot)
        if not desc.ok or bool((desc.payload or {}).get("empty", True)):
            return RuntimeResult(ok=False, message="Slot is empty and cannot be archived.")
        paste = self.runtime.paste_from_slot(slot)
        if not paste.ok:
            return RuntimeResult(ok=False, message="Could not read slot content.")

        content = str((paste.payload or {}).get("content", ""))
        source = str((desc.payload or {}).get("sourceApp", "unknown"))
        created = str((desc.payload or {}).get("capturedAt", _now()))
        clip_id = self._new_clip_id()
        self._clips[clip_id] = ClipRecord(
            clip_id=clip_id,
            content=content,
            source_app=source,
            created_at=created,
            archive_state="active",
            slot_id=slot,
            slot_alias=None,
            categories=[],
            retention_policy="keep-forever",
            folder_links=[],
        )
        self._save()
        return RuntimeResult(ok=True, message="Clip archived to library.", payload={"clipId": clip_id, "slotId": slot})

    def open_library(self, *, archive_state: str = "", category: str = "", folder_id: str = "") -> RuntimeResult:
        rows = list(self._clips.values())
        if archive_state:
            rows = [r for r in rows if r.archive_state == archive_state]
        if category:
            rows = [r for r in rows if category in r.categories]
        if folder_id:
            rows = [r for r in rows if folder_id in r.folder_links]
        rows.sort(key=lambda r: r.created_at, reverse=True)
        return RuntimeResult(
            ok=True,
            message="Clip library view ready.",
            payload={
                "clips": [
                    {
                        "clipId": r.clip_id,
                        "sourceApp": r.source_app,
                        "createdAt": r.created_at,
                        "archiveState": r.archive_state,
                        "slotId": r.slot_id,
                        "slotAlias": r.slot_alias,
                        "categories": r.categories,
                        "retentionPolicy": r.retention_policy,
                        "folderLinks": r.folder_links,
                        "length": len(r.content),
                    }
                    for r in rows
                ],
                "folders": self._folders,
            },
        )

    def create_folder(self, folder_name: str, category: str = "general") -> RuntimeResult:
        name = folder_name.strip()
        if not name:
            return RuntimeResult(ok=False, message="Folder name cannot be empty.")
        fid = f"fld-{len(self._folders) + 1:03d}"
        self._folders[fid] = {"name": name, "category": category.strip() or "general"}
        self._save()
        return RuntimeResult(ok=True, message="Library folder created.", payload={"folderId": fid, "name": name})

    def rename_folder(self, folder_id: str, new_name: str) -> RuntimeResult:
        if folder_id not in self._folders:
            return RuntimeResult(ok=False, message="Folder not found.")
        self._folders[folder_id]["name"] = new_name.strip() or self._folders[folder_id]["name"]
        self._save()
        return RuntimeResult(ok=True, message="Library folder renamed.", payload={"folderId": folder_id})

    def delete_folder(self, folder_id: str) -> RuntimeResult:
        if folder_id not in self._folders:
            return RuntimeResult(ok=False, message="Folder not found.")
        del self._folders[folder_id]
        for clip in self._clips.values():
            clip.folder_links = [x for x in clip.folder_links if x != folder_id]
        self._save()
        return RuntimeResult(ok=True, message="Library folder deleted.", payload={"folderId": folder_id})

    def move_to_folder(self, clip_id: str, folder_id: str) -> RuntimeResult:
        clip = self._clips.get(clip_id)
        if clip is None:
            return RuntimeResult(ok=False, message="Clip not found.")
        if folder_id not in self._folders:
            return RuntimeResult(ok=False, message="Folder not found.")
        clip.archive_state = "archived"
        clip.slot_id = None
        clip.folder_links = [folder_id]
        self._save()
        return RuntimeResult(ok=True, message="Clip moved to folder.", payload={"clipId": clip_id, "folderId": folder_id})

    def link_to_folder(self, clip_id: str, folder_id: str) -> RuntimeResult:
        clip = self._clips.get(clip_id)
        if clip is None:
            return RuntimeResult(ok=False, message="Clip not found.")
        if folder_id not in self._folders:
            return RuntimeResult(ok=False, message="Folder not found.")
        if folder_id not in clip.folder_links:
            clip.folder_links.append(folder_id)
        self._save()
        return RuntimeResult(ok=True, message="Clip linked to folder.", payload={"clipId": clip_id, "folderId": folder_id})

    def retain_slot_alias(self, clip_id: str, alias: str) -> RuntimeResult:
        clip = self._clips.get(clip_id)
        if clip is None:
            return RuntimeResult(ok=False, message="Clip not found.")
        for other in self._clips.values():
            if other.clip_id != clip_id and other.slot_alias and other.slot_alias == alias:
                return RuntimeResult(
                    ok=False,
                    message="Slot alias collision detected.",
                    next_steps=["Choose a different alias.", "Clear existing alias first."],
                )
        clip.slot_alias = alias.strip() or None
        self._save()
        return RuntimeResult(ok=True, message="Slot alias updated.", payload={"clipId": clip_id, "slotAlias": clip.slot_alias})

    def restore_to_slot(self, clip_id: str, slot: int, *, mode: str = "replace") -> RuntimeResult:
        clip = self._clips.get(clip_id)
        if clip is None:
            return RuntimeResult(ok=False, message="Clip not found.")

        current = self.runtime.describe_slot(slot)
        has_content = not bool((current.payload or {}).get("empty", True))
        if has_content and mode == "cancel":
            return RuntimeResult(ok=False, message="Restore cancelled due to slot conflict.")
        if has_content and mode == "merge":
            existing = self.runtime.paste_from_slot(slot)
            existing_text = str((existing.payload or {}).get("content", "")) if existing.ok else ""
            merged = f"{existing_text}\n{clip.content}" if existing_text else clip.content
            self.runtime.unprotect_slot(slot)
            put = self.runtime.copy_to_slot(self._empty_context(), slot=slot, text=merged)
        else:
            self.runtime.unprotect_slot(slot)
            put = self.runtime.copy_to_slot(self._empty_context(), slot=slot, text=clip.content)

        if not put.ok:
            return put

        clip.slot_id = slot
        clip.archive_state = "active"
        self._save()
        return RuntimeResult(ok=True, message="Clip restored to slot.", payload={"clipId": clip_id, "slot": slot, "mode": mode})

    def set_retention_policy(self, clip_id: str, policy: str) -> RuntimeResult:
        clip = self._clips.get(clip_id)
        if clip is None:
            return RuntimeResult(ok=False, message="Clip not found.")
        allowed = {"keep-forever", "age-out", "pin-protected"}
        if policy not in allowed:
            return RuntimeResult(ok=False, message="Invalid retention policy.")
        clip.retention_policy = policy
        clip.archive_state = "pinned" if policy == "pin-protected" else clip.archive_state
        self._save()
        return RuntimeResult(ok=True, message="Retention policy updated.", payload={"clipId": clip_id, "retentionPolicy": policy})

    def list_linked_locations(self, clip_id: str) -> RuntimeResult:
        clip = self._clips.get(clip_id)
        if clip is None:
            return RuntimeResult(ok=False, message="Clip not found.")
        details = [{"folderId": fid, "name": self._folders.get(fid, {}).get("name", fid)} for fid in clip.folder_links]
        return RuntimeResult(ok=True, message="Linked locations listed.", payload={"clipId": clip_id, "locations": details})

    @staticmethod
    def _empty_context():
        from .engine import AppContext

        return AppContext(
            app_id="library",
            window_id="library",
            control_id="library",
            buffer="",
            caret=0,
            clipboard_text="",
        )
