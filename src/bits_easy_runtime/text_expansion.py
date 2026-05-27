from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .diagnostics import get_logger
from .engine import RuntimeResult

_logger = get_logger("bits_easy.text_expansion")


@dataclass
class ExpansionEntry:
    abbreviation: str
    content: str
    title: str
    folder_id: str = "root"
    trigger: str = ""
    hotkey_hint: str = ""


@dataclass
class ExpansionFolder:
    folder_id: str
    name: str
    parent_id: str = ""


class TextExpansionStore:
    def __init__(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self._entries: Dict[str, ExpansionEntry] = {}
        self._folders: Dict[str, ExpansionFolder] = {"root": ExpansionFolder(folder_id="root", name="EASYText Studio", parent_id="")}
        self._primary: Optional[str] = None
        self._load()

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            payload = json.loads(self.storage_path.read_text(encoding="utf-8"))
            self._primary = payload.get("primary")
            raw_folders = payload.get("folders", {})
            for folder_id, item in (raw_folders or {}).items():
                fid = str(folder_id or "").strip()
                if not fid or fid == "root":
                    continue
                self._folders[fid] = ExpansionFolder(
                    folder_id=fid,
                    name=str(item.get("name", fid)).strip() or fid,
                    parent_id=str(item.get("parentId", "root") or "root").strip() or "root",
                )

            rows = payload.get("entries", {})
            for abbr, item in rows.items():
                trigger = str(item.get("trigger", abbr)).strip() or str(abbr)
                folder_id = str(item.get("folderId", "root") or "root").strip() or "root"
                if folder_id not in self._folders:
                    folder_id = "root"
                self._entries[abbr] = ExpansionEntry(
                    abbreviation=abbr,
                    content=str(item.get("content", "")),
                    title=str(item.get("title", abbr)),
                    folder_id=folder_id,
                    trigger=trigger,
                    hotkey_hint=str(item.get("hotkeyHint", "")),
                )
        except Exception:
            _logger.exception("BITS-EASY: loading text expansions at %s failed", self.storage_path)
            self._entries = {}
            self._folders = {"root": ExpansionFolder(folder_id="root", name="EASYText Studio", parent_id="")}
            self._primary = None

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "primary": self._primary,
            "folders": {
                fid: {"name": folder.name, "parentId": folder.parent_id}
                for fid, folder in self._folders.items()
                if fid != "root"
            },
            "entries": {
                abbr: {
                    "content": entry.content,
                    "title": entry.title,
                    "folderId": entry.folder_id,
                    "trigger": entry.trigger,
                    "hotkeyHint": entry.hotkey_hint,
                }
                for abbr, entry in self._entries.items()
            },
        }
        self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def upsert(
        self,
        abbreviation: str,
        content: str,
        *,
        title: Optional[str] = None,
        overwrite: bool = False,
        folder_id: str = "root",
        trigger: str = "",
        hotkey_hint: str = "",
    ) -> RuntimeResult:
        abbreviation = abbreviation.strip()
        if not abbreviation:
            return RuntimeResult(ok=False, message="Abbreviation cannot be empty.")

        folder_id = str(folder_id or "root").strip() or "root"
        if folder_id not in self._folders:
            return RuntimeResult(ok=False, message="Folder not found.")

        trigger_value = str(trigger or abbreviation).strip() or abbreviation

        existing = self._entries.get(abbreviation)
        if existing and existing.content != content and not overwrite:
            return RuntimeResult(
                ok=False,
                message="Abbreviation conflict detected.",
                payload={"abbreviation": abbreviation, "existing": existing.content, "incoming": content},
                next_steps=["Retry with overwrite enabled.", "Rename one of the abbreviations."],
            )

        self._entries[abbreviation] = ExpansionEntry(
            abbreviation=abbreviation,
            content=content,
            title=(title or abbreviation),
            folder_id=folder_id,
            trigger=trigger_value,
            hotkey_hint=str(hotkey_hint or ""),
        )
        if self._primary is None:
            self._primary = abbreviation
        self._save()
        return RuntimeResult(
            ok=True,
            message="EASYText saved.",
            payload={
                "abbreviation": abbreviation,
                "trigger": trigger_value,
                "folderId": folder_id,
            },
        )

    def expand(self, abbreviation: str) -> RuntimeResult:
        entry = self._entries.get(abbreviation.strip())
        if not entry:
            return RuntimeResult(ok=False, message="Expansion not found.")
        return RuntimeResult(
            ok=True,
            message="EASYText expansion ready.",
            payload={
                "content": entry.content,
                "abbreviation": entry.abbreviation,
                "trigger": entry.trigger,
                "title": entry.title,
                "folderId": entry.folder_id,
                "hotkeyHint": entry.hotkey_hint,
                "insertText": entry.content,
                "insertTextSuffix": " ",
                "insertViaClipboard": True,
            },
        )

    def resolve_trigger(self, trigger: str) -> RuntimeResult:
        token = str(trigger or "").strip()
        if not token:
            return RuntimeResult(ok=False, message="Trigger token is required.")
        for entry in self._entries.values():
            if str(entry.trigger).strip().lower() == token.lower():
                return self.expand(entry.abbreviation)
        return RuntimeResult(ok=False, message="No EASYText trigger match found.")

    def list_entries(self) -> RuntimeResult:
        folders = [
            {
                "folderId": f.folder_id,
                "name": f.name,
                "parentId": f.parent_id,
                "children": [c.folder_id for c in self._folders.values() if c.parent_id == f.folder_id and c.folder_id != f.folder_id],
            }
            for f in sorted(self._folders.values(), key=lambda x: (x.parent_id, x.name.lower()))
        ]
        return RuntimeResult(
            ok=True,
            message="EASYText Studio list ready.",
            payload={
                "primary": self._primary,
                "folders": folders,
                "items": [
                    {
                        "abbreviation": e.abbreviation,
                        "title": e.title,
                        "trigger": e.trigger,
                        "folderId": e.folder_id,
                        "hotkeyHint": e.hotkey_hint,
                        "length": len(e.content),
                    }
                    for e in sorted(self._entries.values(), key=lambda x: x.abbreviation)
                ],
            },
        )

    def folder_tree(self) -> RuntimeResult:
        tree: Dict[str, List[str]] = {}
        for folder in self._folders.values():
            if folder.folder_id == "root":
                continue
            tree.setdefault(folder.parent_id or "root", []).append(folder.folder_id)
        for parent_id in list(tree.keys()):
            tree[parent_id] = sorted(tree[parent_id])
        return RuntimeResult(
            ok=True,
            message="EASYText folder tree ready.",
            payload={
                "root": "root",
                "folders": {
                    fid: {
                        "name": folder.name,
                        "parentId": folder.parent_id,
                    }
                    for fid, folder in self._folders.items()
                },
                "tree": tree,
            },
        )

    def create_folder(self, name: str, parent_id: str = "root") -> RuntimeResult:
        label = str(name or "").strip()
        if not label:
            return RuntimeResult(ok=False, message="Folder name cannot be empty.")
        parent = str(parent_id or "root").strip() or "root"
        if parent not in self._folders:
            return RuntimeResult(ok=False, message="Parent folder not found.")
        seed = len(self._folders)
        next_id = f"txt-{seed:03d}"
        while next_id in self._folders:
            seed += 1
            next_id = f"txt-{seed:03d}"
        self._folders[next_id] = ExpansionFolder(folder_id=next_id, name=label, parent_id=parent)
        self._save()
        return RuntimeResult(ok=True, message="EASYText folder created.", payload={"folderId": next_id, "name": label, "parentId": parent})

    def rename_folder(self, folder_id: str, new_name: str) -> RuntimeResult:
        fid = str(folder_id or "").strip()
        if fid == "root" or fid not in self._folders:
            return RuntimeResult(ok=False, message="Folder not found.")
        label = str(new_name or "").strip()
        if not label:
            return RuntimeResult(ok=False, message="Folder name cannot be empty.")
        self._folders[fid].name = label
        self._save()
        return RuntimeResult(ok=True, message="EASYText folder renamed.", payload={"folderId": fid, "name": label})

    def delete_folder(self, folder_id: str) -> RuntimeResult:
        fid = str(folder_id or "").strip()
        if fid == "root" or fid not in self._folders:
            return RuntimeResult(ok=False, message="Folder not found.")

        descendant_ids = [fid]
        while True:
            expanded = False
            for child in list(self._folders.values()):
                if child.folder_id in descendant_ids:
                    continue
                if child.parent_id in descendant_ids:
                    descendant_ids.append(child.folder_id)
                    expanded = True
            if not expanded:
                break

        for entry in self._entries.values():
            if entry.folder_id in descendant_ids:
                entry.folder_id = "root"

        for delete_id in descendant_ids:
            self._folders.pop(delete_id, None)
        self._save()
        return RuntimeResult(ok=True, message="EASYText folder deleted.", payload={"folderId": fid, "reassignedTo": "root"})

    def move_to_folder(self, abbreviation: str, folder_id: str) -> RuntimeResult:
        abbr = str(abbreviation or "").strip()
        entry = self._entries.get(abbr)
        if not entry:
            return RuntimeResult(ok=False, message="Expansion not found.")
        fid = str(folder_id or "root").strip() or "root"
        if fid not in self._folders:
            return RuntimeResult(ok=False, message="Folder not found.")
        entry.folder_id = fid
        self._save()
        return RuntimeResult(ok=True, message="EASYText moved to folder.", payload={"abbreviation": abbr, "folderId": fid})

    def rename(self, abbreviation: str, new_title: str) -> RuntimeResult:
        entry = self._entries.get(abbreviation.strip())
        if not entry:
            return RuntimeResult(ok=False, message="Expansion not found.")
        entry.title = new_title.strip() or entry.title
        self._save()
        return RuntimeResult(ok=True, message="Expansion renamed.", payload={"abbreviation": entry.abbreviation, "title": entry.title})

    def set_hotkey_hint(self, abbreviation: str, hotkey_hint: str) -> RuntimeResult:
        entry = self._entries.get(str(abbreviation or "").strip())
        if not entry:
            return RuntimeResult(ok=False, message="Expansion not found.")
        entry.hotkey_hint = str(hotkey_hint or "").strip()
        self._save()
        return RuntimeResult(
            ok=True,
            message="EASYText hotkey hint saved.",
            payload={"abbreviation": entry.abbreviation, "hotkeyHint": entry.hotkey_hint},
        )

    def delete(self, abbreviation: str) -> RuntimeResult:
        abbr = abbreviation.strip()
        if abbr not in self._entries:
            return RuntimeResult(ok=False, message="Expansion not found.")
        del self._entries[abbr]
        if self._primary == abbr:
            self._primary = next(iter(sorted(self._entries.keys())), None)
        self._save()
        return RuntimeResult(ok=True, message="Expansion deleted.", payload={"abbreviation": abbr})

    def set_primary(self, abbreviation: str) -> RuntimeResult:
        abbr = abbreviation.strip()
        if abbr not in self._entries:
            return RuntimeResult(ok=False, message="Expansion not found.")
        self._primary = abbr
        self._save()
        return RuntimeResult(ok=True, message="Primary quick insert updated.", payload={"abbreviation": abbr})

    def quick_insert(self) -> RuntimeResult:
        if not self._primary:
            return RuntimeResult(ok=False, message="No primary quick insert is configured.")
        return self.expand(self._primary)

