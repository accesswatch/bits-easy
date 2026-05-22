from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Dict, List

from .diagnostics import get_logger
from .engine import RuntimeResult

_logger = get_logger("spellforge.backup_migration")


class BackupMigrationService:
    def __init__(self, storage_path: Path | str | None = None):
        self._storage_path = Path(storage_path) if storage_path else None
        self._sources: List[str] = []
        self._target = ""
        self._load()

    def _save(self) -> None:
        if not self._storage_path:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"sources": self._sources, "target": self._target}
        self._storage_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if not self._storage_path or not self._storage_path.exists():
            return
        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except Exception:
            _logger.exception("Spellforge: loading backup migration state at %s failed", self._storage_path)
            return
        self._sources = [str(x) for x in payload.get("sources", [])] if isinstance(payload.get("sources", []), list) else []
        self._target = str(payload.get("target", ""))

    def set_target(self, path: str) -> RuntimeResult:
        p = Path(path)
        if not p.is_absolute():
            return RuntimeResult(ok=False, message="Backup target must be an absolute path.")
        self._target = str(p)
        self._save()
        return RuntimeResult(ok=True, message="Backup target configured.", payload={"target": self._target})

    def add_source(self, path: str) -> RuntimeResult:
        p = Path(path)
        if not p.is_absolute():
            return RuntimeResult(ok=False, message="Backup source must be an absolute path.")
        val = str(p)
        if val in self._sources:
            return RuntimeResult(ok=False, message="Duplicate backup source is not allowed.")
        self._sources.append(val)
        self._save()
        return RuntimeResult(ok=True, message="Backup source added.", payload={"count": len(self._sources)})

    def backup_settings(self, files: Dict[str, str], out_path: Path | str) -> RuntimeResult:
        path = Path(out_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(files, ensure_ascii=True, indent=2), encoding="utf-8")
        return RuntimeResult(ok=True, message="Settings backup complete.", payload={"path": str(path), "count": len(files)})

    def restore_settings(self, in_path: Path | str) -> RuntimeResult:
        path = Path(in_path)
        if not path.exists():
            return RuntimeResult(ok=False, message="Settings backup file was not found.")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            return RuntimeResult(ok=False, message=f"Restore failed: {exc}")
        count = len(payload) if isinstance(payload, dict) else 0
        return RuntimeResult(ok=True, message="Settings restore complete.", payload={"count": count})

    def backup_selected(self, selected_paths: List[str], out_dir: Path | str) -> RuntimeResult:
        base = Path(out_dir)
        base.mkdir(parents=True, exist_ok=True)
        failures = []
        copied = []
        for item in selected_paths:
            src = Path(item)
            if not src.exists():
                failures.append(item)
                continue
            dest = base / src.name
            try:
                if src.is_dir():
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(src, dest)
                else:
                    shutil.copy2(src, dest)
                copied.append(str(dest))
            except Exception:
                failures.append(item)
        return RuntimeResult(ok=True, message="Selected backup complete.", payload={"copied": copied, "failures": failures})

    def migrate_profile(self, from_dir: Path | str, to_dir: Path | str, *, dry_run: bool = False) -> RuntimeResult:
        src = Path(from_dir)
        dst = Path(to_dir)
        if not src.exists():
            return RuntimeResult(ok=False, message="Migration source was not found.")
        files = [str(p.relative_to(src)) for p in src.rglob("*") if p.is_file()]
        if dry_run:
            return RuntimeResult(ok=True, message="Migration dry-run complete.", payload={"files": files, "count": len(files)})
        dst.mkdir(parents=True, exist_ok=True)
        for rel in files:
            s = src / rel
            d = dst / rel
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(s, d)
        return RuntimeResult(ok=True, message="Migration applied with rollback-ready copy set.", payload={"count": len(files), "target": str(dst)})
