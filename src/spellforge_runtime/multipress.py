from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class MultiPressResolution:
    matched_command_id: str
    trigger_kind: str
    used_press_count: int
    fallback_used: bool
    reason: str
    announcement: str


class MultiPressResolver:
    def __init__(self, bindings: List[dict]):
        self.bindings = bindings

    @staticmethod
    def _equivalent_key_chords(key_chord: str) -> List[str]:
        chord = str(key_chord or "").strip()
        if not chord:
            return []

        aliases: List[str] = [chord]
        if chord.startswith("CapsLock+"):
            aliases.append("NVDA+" + chord[len("CapsLock+"):])
        elif chord.startswith("NVDA+"):
            aliases.append("CapsLock+" + chord[len("NVDA+"):])
        return aliases

    def resolve(
        self,
        key_chord: str,
        press_count: int,
        *,
        hold_duration_ms: int = 0,
        multi_press_enabled: bool = True,
    ) -> Optional[MultiPressResolution]:
        candidates = set(self._equivalent_key_chords(key_chord))
        relevant = [b for b in self.bindings if b.get("enabled", True) and b.get("keyChord") in candidates]
        if not relevant:
            return None

        if not multi_press_enabled:
            press_count = 1
            hold_duration_ms = 0

        # Emergency stop always wins.
        for b in relevant:
            if b.get("commandId") == "cmd.system.emergencyStop":
                return MultiPressResolution(
                    matched_command_id="cmd.system.emergencyStop",
                    trigger_kind="single-press",
                    used_press_count=press_count,
                    fallback_used=False,
                    reason="emergency-stop-precedence",
                    announcement="Emergency stop triggered.",
                )

        explicit: Dict[str, dict] = {}
        for b in relevant:
            trig = b.get("trigger") or {"kind": "single-press"}
            kind = trig.get("kind", "single-press")
            if kind not in explicit:
                explicit[kind] = b

        if not multi_press_enabled and "single-press" not in explicit:
            return None

        hold_cfg = explicit.get("press-and-hold")
        if hold_cfg is not None:
            trig = hold_cfg.get("trigger") or {}
            hold_threshold = int(trig.get("holdThresholdMs", 500))
            if hold_duration_ms >= hold_threshold:
                return MultiPressResolution(
                    matched_command_id=hold_cfg.get("commandId", ""),
                    trigger_kind="press-and-hold",
                    used_press_count=press_count,
                    fallback_used=False,
                    reason="explicit-hold",
                    announcement="Press-and-hold action triggered.",
                )

        if press_count >= 3 and "triple-press" in explicit:
            return MultiPressResolution(
                matched_command_id=explicit["triple-press"].get("commandId", ""),
                trigger_kind="triple-press",
                used_press_count=press_count,
                fallback_used=False,
                reason="explicit-triple",
                announcement="Triple-press action triggered.",
            )

        if press_count >= 2 and "double-press" in explicit:
            return MultiPressResolution(
                matched_command_id=explicit["double-press"].get("commandId", ""),
                trigger_kind="double-press",
                used_press_count=press_count,
                fallback_used=False,
                reason="explicit-double",
                announcement="Double-press action triggered.",
            )

        if "single-press" in explicit:
            return MultiPressResolution(
                matched_command_id=explicit["single-press"].get("commandId", ""),
                trigger_kind="single-press",
                used_press_count=press_count,
                fallback_used=(press_count > 1),
                reason="single-fallback" if press_count > 1 else "explicit-single",
                announcement="Single-press action triggered." if press_count <= 1 else "Ambiguous timing resolved to single-press action.",
            )

        # First plain binding fallback.
        first = relevant[0]
        return MultiPressResolution(
            matched_command_id=first.get("commandId", ""),
            trigger_kind="single-press",
            used_press_count=press_count,
            fallback_used=True,
            reason="default-first-binding",
            announcement="Default single-press action triggered.",
        )
