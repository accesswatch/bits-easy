from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .diagnostics import get_logger
from .engine import RuntimeResult

_logger = get_logger("spellforge.notes_workspace")


class NotesWorkspaceService:
    def __init__(self, storage_path: Path | str | None = None):
        self._storage_path = Path(storage_path) if storage_path else None
        self._notes: Dict[str, Dict[str, Any]] = {}
        self._categories: Dict[str, Dict[str, Any]] = {}
        self._global_help: Dict[str, str] = {}
        self._app_help: Dict[str, Dict[str, str]] = {}
        self._web_notes: Dict[str, Dict[str, str]] = {}
        self._snapshots: List[Dict[str, Any]] = []
        self._counter = 0
        self._mode = "simple"
        self._load()

    def _save(self) -> None:
        if not self._storage_path:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "notes": self._notes,
            "categories": self._categories,
            "globalHelp": self._global_help,
            "appHelp": self._app_help,
            "webNotes": self._web_notes,
            "snapshots": self._snapshots[-20:],
            "counter": self._counter,
            "mode": self._mode,
        }
        self._storage_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if not self._storage_path or not self._storage_path.exists():
            return
        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except Exception:
            _logger.exception("Spellforge: loading notes workspace at %s failed", self._storage_path)
            return
        self._notes = payload.get("notes", {}) if isinstance(payload.get("notes", {}), dict) else {}
        self._categories = payload.get("categories", {}) if isinstance(payload.get("categories", {}), dict) else {}
        self._global_help = payload.get("globalHelp", {}) if isinstance(payload.get("globalHelp", {}), dict) else {}
        self._app_help = payload.get("appHelp", {}) if isinstance(payload.get("appHelp", {}), dict) else {}
        self._web_notes = payload.get("webNotes", {}) if isinstance(payload.get("webNotes", {}), dict) else {}
        self._snapshots = payload.get("snapshots", []) if isinstance(payload.get("snapshots", []), list) else []
        self._counter = int(payload.get("counter", 0))
        self._mode = str(payload.get("mode", "simple"))

    def _snapshot(self, reason: str) -> None:
        self._snapshots.append(
            {
                "reason": reason,
                "notes": self._notes,
                "categories": self._categories,
                "mode": self._mode,
            }
        )

    def quick_note(self, text: str, app_id: str) -> RuntimeResult:
        value = text.strip()
        if not value:
            return RuntimeResult(ok=False, message="Quick note text is required.")
        self._counter += 1
        nid = f"note-{self._counter:05d}"
        self._notes[nid] = {
            "id": nid,
            "title": value[:60],
            "body": value,
            "appId": app_id,
            "category": "inbox",
            "relations": [],
            "attachments": [],
            "fields": {},
        }
        self._save()
        return RuntimeResult(ok=True, message="Quick note captured.", payload={"noteId": nid})

    def set_mode(self, mode: str) -> RuntimeResult:
        m = mode.strip().lower()
        if m not in ("simple", "advanced"):
            return RuntimeResult(ok=False, message="Mode must be simple or advanced.")
        self._mode = m
        self._save()
        return RuntimeResult(ok=True, message="Notes mode updated.", payload={"mode": m})

    def category_create(self, category: str, parent: str = "") -> RuntimeResult:
        cid = category.strip().lower()
        if not cid:
            return RuntimeResult(ok=False, message="Category name is required.")
        if cid in self._categories:
            return RuntimeResult(ok=False, message="Category already exists.")
        self._categories[cid] = {"id": cid, "parent": parent.strip().lower(), "open": True}
        self._save()
        return RuntimeResult(ok=True, message="Category created.", payload={"category": cid})

    def category_move(self, category: str, new_parent: str = "") -> RuntimeResult:
        cid = category.strip().lower()
        row = self._categories.get(cid)
        if row is None:
            return RuntimeResult(ok=False, message="Category not found.")
        row["parent"] = new_parent.strip().lower()
        self._save()
        return RuntimeResult(ok=True, message="Category moved.", payload={"category": cid, "parent": row["parent"]})

    def relate_notes(self, note_a: str, note_b: str) -> RuntimeResult:
        a = self._notes.get(note_a.strip())
        b = self._notes.get(note_b.strip())
        if a is None or b is None:
            return RuntimeResult(ok=False, message="Both notes must exist.")
        if note_b not in a["relations"]:
            a["relations"].append(note_b)
        if note_a not in b["relations"]:
            b["relations"].append(note_a)
        self._save()
        return RuntimeResult(ok=True, message="Related notes linked bidirectionally.")

    def attachment_add(self, note_id: str, path: str) -> RuntimeResult:
        note = self._notes.get(note_id.strip())
        if note is None:
            return RuntimeResult(ok=False, message="Note not found.")
        val = path.strip()
        if not val:
            return RuntimeResult(ok=False, message="Attachment path is required.")
        if val not in note["attachments"]:
            note["attachments"].append(val)
        self._save()
        return RuntimeResult(ok=True, message="Attachment added.", payload={"count": len(note["attachments"])})

    def field_set(self, note_id: str, key: str, value: str) -> RuntimeResult:
        note = self._notes.get(note_id.strip())
        if note is None:
            return RuntimeResult(ok=False, message="Note not found.")
        k = key.strip()
        if not k:
            return RuntimeResult(ok=False, message="Field key is required.")
        note["fields"][k] = value
        self._save()
        return RuntimeResult(ok=True, message="Advanced field updated.", payload={"field": k})

    def help_set(self, text: str, *, app_id: str = "", domain: str = "", page: str = "") -> RuntimeResult:
        value = text.strip()
        if not value:
            return RuntimeResult(ok=False, message="Help text is required.")
        if app_id.strip():
            bucket = self._app_help.setdefault(app_id.strip().lower(), {})
            bucket["default"] = value
        elif domain.strip() or page.strip():
            bucket = self._web_notes.setdefault(domain.strip().lower() or "*", {})
            bucket[page.strip().lower() or "*"] = value
        else:
            self._global_help["default"] = value
        self._save()
        return RuntimeResult(ok=True, message="Help note saved.")

    def help_resolve(self, *, app_id: str = "", domain: str = "", page: str = "") -> RuntimeResult:
        app = app_id.strip().lower()
        dom = domain.strip().lower()
        pg = page.strip().lower()

        if app and app in self._app_help and "default" in self._app_help[app]:
            return RuntimeResult(ok=True, message="App help resolved.", payload={"scope": "app", "text": self._app_help[app]["default"]})

        if dom:
            bucket = self._web_notes.get(dom, {})
            if pg and pg in bucket:
                return RuntimeResult(ok=True, message="Page help resolved.", payload={"scope": "page", "text": bucket[pg]})
            if "*" in bucket:
                return RuntimeResult(ok=True, message="Domain help resolved.", payload={"scope": "domain", "text": bucket["*"]})

        if "default" in self._global_help:
            return RuntimeResult(ok=True, message="Global help resolved.", payload={"scope": "global", "text": self._global_help["default"]})
        return RuntimeResult(ok=False, message="No help note found for this context.")

    def snapshot_create(self, reason: str) -> RuntimeResult:
        self._snapshot(reason.strip() or "manual")
        self._save()
        return RuntimeResult(ok=True, message="Notes restore point created.", payload={"count": len(self._snapshots)})

    def snapshot_restore(self, index: int = -1) -> RuntimeResult:
        if not self._snapshots:
            return RuntimeResult(ok=False, message="No restore points available.")
        row = self._snapshots[index]
        self._notes = dict(row.get("notes", {}))
        self._categories = dict(row.get("categories", {}))
        self._mode = str(row.get("mode", "simple"))
        self._save()
        return RuntimeResult(ok=True, message="Notes state restored.", payload={"reason": row.get("reason", "")})

    def category_tree(self) -> RuntimeResult:
        tree: Dict[str, List[str]] = {}
        for cid, row in self._categories.items():
            parent = str(row.get("parent", "")).strip().lower() or "root"
            tree.setdefault(parent, []).append(cid)
        for key in list(tree.keys()):
            tree[key].sort()
        return RuntimeResult(ok=True, message="Category tree ready.", payload={"tree": tree, "count": len(self._categories)})

    def related_graph(self, note_id: str) -> RuntimeResult:
        nid = note_id.strip()
        root = self._notes.get(nid)
        if root is None:
            return RuntimeResult(ok=False, message="Note not found.")
        nodes = {nid: {"title": root.get("title", ""), "depth": 0}}
        edges: List[Dict[str, str]] = []
        for rel in list(root.get("relations", [])):
            peer = self._notes.get(rel)
            if peer is not None:
                nodes[rel] = {"title": peer.get("title", ""), "depth": 1}
                edges.append({"from": nid, "to": rel})
        return RuntimeResult(
            ok=True,
            message="Related note graph ready.",
            payload={"root": nid, "nodes": [{"id": k, **v} for k, v in nodes.items()], "edges": edges},
        )

    def attachment_action(self, note_id: str, path: str, action: str) -> RuntimeResult:
        note = self._notes.get(note_id.strip())
        if note is None:
            return RuntimeResult(ok=False, message="Note not found.")
        target = path.strip()
        if not target:
            return RuntimeResult(ok=False, message="Attachment path is required.")
        if target not in note.get("attachments", []):
            return RuntimeResult(ok=False, message="Attachment not found on this note.")
        mode = action.strip().lower()
        if mode not in ("open", "copy"):
            return RuntimeResult(ok=False, message="Attachment action must be open or copy.")
        return RuntimeResult(
            ok=True,
            message="Attachment action prepared.",
            payload={"noteId": note_id.strip(), "path": target, "action": mode, "insertText": target if mode == "copy" else ""},
        )

    def backup_export(self, out_path: Path | str) -> RuntimeResult:
        path = Path(out_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "notes": self._notes,
            "categories": self._categories,
            "globalHelp": self._global_help,
            "appHelp": self._app_help,
            "webNotes": self._web_notes,
            "mode": self._mode,
            "counter": self._counter,
        }
        path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
        return RuntimeResult(ok=True, message="Notes backup exported.", payload={"path": str(path)})

    def backup_restore(self, in_path: Path | str) -> RuntimeResult:
        path = Path(in_path)
        if not path.exists():
            return RuntimeResult(ok=False, message="Notes backup file was not found.")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            return RuntimeResult(ok=False, message=f"Notes backup restore failed: {exc}")
        notes = payload.get("notes", {})
        categories = payload.get("categories", {})
        if not isinstance(notes, dict) or not isinstance(categories, dict):
            return RuntimeResult(ok=False, message="Notes backup payload is invalid.")
        self._snapshot("backup-restore-before")
        self._notes = notes
        self._categories = categories
        self._global_help = payload.get("globalHelp", {}) if isinstance(payload.get("globalHelp", {}), dict) else {}
        self._app_help = payload.get("appHelp", {}) if isinstance(payload.get("appHelp", {}), dict) else {}
        self._web_notes = payload.get("webNotes", {}) if isinstance(payload.get("webNotes", {}), dict) else {}
        self._mode = str(payload.get("mode", self._mode))
        self._counter = int(payload.get("counter", self._counter))
        self._save()
        return RuntimeResult(ok=True, message="Notes backup restored.", payload={"noteCount": len(self._notes), "categoryCount": len(self._categories)})
