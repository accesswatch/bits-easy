from __future__ import annotations

import platform
from pathlib import Path
from typing import Any, Dict

from .engine import RuntimeResult


class SystemReportService:
    def collect(self) -> RuntimeResult:
        payload: Dict[str, Any] = {
            "os": platform.system(),
            "osVersion": platform.version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "pythonVersion": platform.python_version(),
            "network": {
                "hostname": platform.node(),
            },
            "memory": {
                "status": "basic-runtime-only",
            },
            "storage": {
                "status": "basic-runtime-only",
            },
        }
        return RuntimeResult(ok=True, message="System report collected.", payload=payload)

    def export(self, out_path: Path | str) -> RuntimeResult:
        target = Path(out_path)
        report = self.collect()
        if not report.ok:
            return report
        target.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "System Report",
            "============",
            f"OS: {report.payload.get('os','')}",
            f"OS Version: {report.payload.get('osVersion','')}",
            f"Platform: {report.payload.get('platform','')}",
            f"Machine: {report.payload.get('machine','')}",
            f"Processor: {report.payload.get('processor','')}",
            f"Python: {report.payload.get('pythonVersion','')}",
            f"Hostname: {report.payload.get('network',{}).get('hostname','')}",
        ]
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return RuntimeResult(ok=True, message="System report exported.", payload={"path": str(target)})
