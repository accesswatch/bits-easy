from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .engine import RuntimeResult


@dataclass
class AdaptiveActionResult:
    content: str
    confidence: float
    fallbacks: List[str]


class AdaptiveActionEngine:
    def summarize(self, text: str) -> RuntimeResult:
        value = text.strip()
        if not value:
            return RuntimeResult(ok=False, message="No text available for summarize action.")

        words = value.split()
        short = " ".join(words[:20])
        summary = short + ("..." if len(words) > 20 else "")
        confidence = 0.92 if len(words) >= 12 else 0.68
        return RuntimeResult(
            ok=True,
            message="Selection summary prepared.",
            payload={
                "content": summary,
                "confidence": confidence,
                "fallbacks": ["cmd.result.openFallbacks", "cmd.palette.open"],
            },
        )

    def extract_actions(self, text: str) -> RuntimeResult:
        value = text.strip()
        if not value:
            return RuntimeResult(ok=False, message="No text available for action extraction.")

        lines = [part.strip(" -") for part in value.replace("\r", "").split("\n") if part.strip()]
        actions = []
        for line in lines:
            low = line.lower()
            if any(token in low for token in ("todo", "action", "must", "should", "follow up", "next")):
                actions.append(line)
        if not actions:
            actions = lines[:3]

        confidence = 0.88 if len(actions) >= 2 else 0.62
        return RuntimeResult(
            ok=True,
            message="Action items extracted.",
            payload={
                "items": actions,
                "confidence": confidence,
                "fallbacks": ["cmd.result.openFallbacks", "cmd.palette.open"],
            },
        )

    def rewrite_beginner(self, text: str) -> RuntimeResult:
        value = text.strip()
        if not value:
            return RuntimeResult(ok=False, message="No text available for rewrite action.")

        rewritten = value.replace("utilize", "use").replace("approximately", "about")
        confidence = 0.9 if len(value.split()) >= 10 else 0.65
        return RuntimeResult(
            ok=True,
            message="Beginner rewrite prepared.",
            payload={
                "content": rewritten,
                "confidence": confidence,
                "fallbacks": ["cmd.result.openFallbacks", "cmd.palette.open"],
            },
        )
