from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .engine import RuntimeResult


class WorkflowPortabilityService:
    def export_pack(self, pack: Dict[str, Any], out_path: Path | str) -> RuntimeResult:
        path = Path(out_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "settings": pack.get("settings", {}),
            "chains": pack.get("chains", []),
            "templates": pack.get("templates", []),
        }
        path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")
        return RuntimeResult(ok=True, message="Workflow pack exported.", payload={"path": str(path)})

    def import_pack(self, in_path: Path | str, *, reject_on_conflict: bool = True) -> RuntimeResult:
        path = Path(in_path)
        if not path.exists():
            return RuntimeResult(ok=False, message="Workflow pack was not found.")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            return RuntimeResult(ok=False, message=f"Workflow pack import failed: {exc}")

        conflicts = []
        for key in ("settings", "chains", "templates"):
            if key not in payload:
                conflicts.append(f"missing:{key}")

        if conflicts and reject_on_conflict:
            return RuntimeResult(ok=False, message="Workflow pack conflicts detected.", payload={"conflicts": conflicts})

        return RuntimeResult(ok=True, message="Workflow pack imported.", payload={"integrity": "pass", "conflicts": conflicts})
