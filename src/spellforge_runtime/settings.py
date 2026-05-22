from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from .diagnostics import get_logger

_logger = get_logger("spellforge.settings")


@dataclass
class SpellforgeSettings:
    profile_id: str = "balanced"
    announce_surface_mode: bool = True
    enable_contextual_fallbacks: bool = True
    enable_command_palette: bool = True
    slot_default: int = 1
    preview_threshold_chars: int = 240
    enable_global_hotkeys: bool = True
    emulate_capslock_prefix_for_os_hotkeys: bool = True
    enable_multi_press_gestures: bool = True


class SettingsStore:
    def __init__(self, path: Path | str):
        self.path = Path(path)

    def load(self) -> SpellforgeSettings:
        if not self.path.exists():
            return SpellforgeSettings()
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            return SpellforgeSettings(
                profile_id=str(payload.get("profile_id", "balanced")),
                announce_surface_mode=bool(payload.get("announce_surface_mode", True)),
                enable_contextual_fallbacks=bool(payload.get("enable_contextual_fallbacks", True)),
                enable_command_palette=bool(payload.get("enable_command_palette", True)),
                slot_default=int(payload.get("slot_default", 1)),
                preview_threshold_chars=int(payload.get("preview_threshold_chars", 240)),
                enable_global_hotkeys=bool(payload.get("enable_global_hotkeys", True)),
                emulate_capslock_prefix_for_os_hotkeys=bool(payload.get("emulate_capslock_prefix_for_os_hotkeys", True)),
                enable_multi_press_gestures=bool(payload.get("enable_multi_press_gestures", True)),
            )
        except Exception:
            _logger.exception("Spellforge: loading settings store at %s failed", self.path)
            return SpellforgeSettings()

    def save(self, settings: SpellforgeSettings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")
