from __future__ import annotations

from typing import List

from .engine import RuntimeResult


class ProgressCueEngine:
    def __init__(self, interval_percent: int = 10):
        self.interval_percent = max(1, min(50, int(interval_percent)))

    def cue_plan(self, total_steps: int, *, tutorial: bool = False) -> RuntimeResult:
        steps = max(1, int(total_steps))
        marks: List[int] = []
        p = self.interval_percent
        while p < 100:
            mark = max(1, min(steps, int(round((p / 100.0) * steps))))
            if not marks or marks[-1] != mark:
                marks.append(mark)
            p += self.interval_percent

        payload = {
            "totalSteps": steps,
            "intervalPercent": self.interval_percent,
            "cueSteps": marks,
            "tickBetweenMajor": True,
        }
        if tutorial:
            payload["tutorial"] = [
                "Tick cue for incremental progress.",
                "Major cue at configured interval.",
                "Completion cue at 100 percent.",
            ]

        return RuntimeResult(ok=True, message="Progress cue plan ready.", payload=payload)
