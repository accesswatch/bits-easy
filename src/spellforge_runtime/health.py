from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class HealthReport:
    total_commands: int
    success_count: int
    failure_count: int
    success_rate: float
    by_app: Dict[str, Dict[str, int]]
    top_failures: List[str]


class IntegrationHealthTracker:
    def __init__(self, log_path: Path | str):
        self.log_path = Path(log_path)

    def record(self, app_id: str, command_id: str, ok: bool, reason: str = "") -> None:
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        row = {
            "appId": app_id,
            "commandId": command_id,
            "ok": bool(ok),
            "reason": reason,
        }
        with self.log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=True) + "\n")

    def report(self) -> HealthReport:
        if not self.log_path.exists():
            return HealthReport(0, 0, 0, 0.0, {}, [])

        total = 0
        success = 0
        fail = 0
        by_app = defaultdict(lambda: {"ok": 0, "fail": 0})
        failure_reasons = defaultdict(int)

        with self.log_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                total += 1
                app = str(row.get("appId", "unknown"))
                ok = bool(row.get("ok", False))
                if ok:
                    success += 1
                    by_app[app]["ok"] += 1
                else:
                    fail += 1
                    by_app[app]["fail"] += 1
                    reason = str(row.get("reason", "unknown"))
                    failure_reasons[reason] += 1

        rate = (success / total) if total else 0.0
        top_failures = [k for k, _ in sorted(failure_reasons.items(), key=lambda x: (-x[1], x[0]))[:5]]

        return HealthReport(
            total_commands=total,
            success_count=success,
            failure_count=fail,
            success_rate=rate,
            by_app=dict(by_app),
            top_failures=top_failures,
        )
