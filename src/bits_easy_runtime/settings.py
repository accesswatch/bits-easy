from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .diagnostics import get_logger

_logger = get_logger("bits_easy.settings")


@dataclass
class BitsEasySettings:
    profile_id: str = "balanced"
    announce_surface_mode: bool = True
    enable_contextual_fallbacks: bool = True
    enable_command_palette: bool = True
    slot_default: int = 1
    preview_threshold_chars: int = 240
    enable_global_hotkeys: bool = True
    emulate_capslock_prefix_for_os_hotkeys: bool = True
    enable_multi_press_gestures: bool = True
    enable_beta_features: bool = False
    enable_raw_easy_sequences: bool = True
    raw_easy_sequence_timeout_ms: int = 900
    active_mode: str = ""
    custom_modes: Dict[str, Dict[str, Any]] = None

    def __post_init__(self):
        if self.custom_modes is None:
            self.custom_modes = {}


class SettingsStore:
    def __init__(self, path: Path | str):
        self.path = Path(path)

    def load(self) -> BitsEasySettings:
        if not self.path.exists():
            return BitsEasySettings()
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            custom_modes = payload.get("custom_modes", {})
            if not isinstance(custom_modes, dict):
                custom_modes = {}
            return BitsEasySettings(
                profile_id=str(payload.get("profile_id", "balanced")),
                announce_surface_mode=bool(payload.get("announce_surface_mode", True)),
                enable_contextual_fallbacks=bool(payload.get("enable_contextual_fallbacks", True)),
                enable_command_palette=bool(payload.get("enable_command_palette", True)),
                slot_default=int(payload.get("slot_default", 1)),
                preview_threshold_chars=int(payload.get("preview_threshold_chars", 240)),
                enable_global_hotkeys=bool(payload.get("enable_global_hotkeys", True)),
                emulate_capslock_prefix_for_os_hotkeys=bool(payload.get("emulate_capslock_prefix_for_os_hotkeys", True)),
                enable_multi_press_gestures=bool(payload.get("enable_multi_press_gestures", True)),
                enable_beta_features=bool(payload.get("enable_beta_features", False)),
                # EASY key sequences are mandatory; keep persisted field for compatibility.
                enable_raw_easy_sequences=True,
                raw_easy_sequence_timeout_ms=int(payload.get("raw_easy_sequence_timeout_ms", 900)),
                active_mode=str(payload.get("active_mode", "")),
                custom_modes=custom_modes,
            )
        except Exception:
            _logger.exception("BITS-EASY: loading settings store at %s failed", self.path)
            return BitsEasySettings()

    def save(self, settings: BitsEasySettings) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(asdict(settings), indent=2), encoding="utf-8")


def mode_payload_from_settings(
    settings: BitsEasySettings,
    *,
    base_profile: Optional[str] = None,
    hotkey_bindings: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "baseProfile": str(base_profile or settings.profile_id or "balanced"),
        "overrides": {
            "enable_command_palette": bool(settings.enable_command_palette),
            "enable_multi_press_gestures": bool(settings.enable_multi_press_gestures),
            "enable_raw_easy_sequences": True,
            "raw_easy_sequence_timeout_ms": int(settings.raw_easy_sequence_timeout_ms),
            "enable_contextual_fallbacks": bool(settings.enable_contextual_fallbacks),
            "announce_surface_mode": bool(settings.announce_surface_mode),
            "enable_global_hotkeys": bool(settings.enable_global_hotkeys),
        },
    }
    if isinstance(hotkey_bindings, list) and hotkey_bindings:
        payload["hotkeyBindings"] = [dict(row) for row in hotkey_bindings if isinstance(row, dict)]
    return payload


def _coerce_hotkey_bindings(raw: Any) -> Optional[List[Dict[str, Any]]]:
    if not isinstance(raw, list):
        return None
    rows = [dict(row) for row in raw if isinstance(row, dict)]
    if not rows:
        return None
    return rows


def resolve_active_mode_payload(settings: BitsEasySettings) -> Optional[Dict[str, Any]]:
    mode_name = str(getattr(settings, "active_mode", "") or "").strip()
    if not mode_name:
        return None
    custom_modes = getattr(settings, "custom_modes", {}) or {}
    if not isinstance(custom_modes, dict):
        return None
    payload = custom_modes.get(mode_name)
    if not isinstance(payload, dict):
        return None
    return dict(payload)


def apply_mode_payload_to_settings(settings: BitsEasySettings, mode_payload: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    if not isinstance(mode_payload, dict):
        return None

    base = str(mode_payload.get("baseProfile", settings.profile_id or "balanced"))
    if base not in ("beginner", "balanced", "expert"):
        base = "balanced"
    settings.profile_id = base

    overrides = mode_payload.get("overrides", {})
    if not isinstance(overrides, dict):
        overrides = {}

    settings.enable_command_palette = bool(overrides.get("enable_command_palette", settings.enable_command_palette))
    settings.enable_multi_press_gestures = bool(
        overrides.get("enable_multi_press_gestures", settings.enable_multi_press_gestures)
    )
    # EASY key sequences are always active by design.
    settings.enable_raw_easy_sequences = True
    settings.raw_easy_sequence_timeout_ms = int(
        overrides.get("raw_easy_sequence_timeout_ms", settings.raw_easy_sequence_timeout_ms)
    )
    settings.enable_contextual_fallbacks = bool(
        overrides.get("enable_contextual_fallbacks", settings.enable_contextual_fallbacks)
    )
    settings.announce_surface_mode = bool(overrides.get("announce_surface_mode", settings.announce_surface_mode))
    settings.enable_global_hotkeys = bool(overrides.get("enable_global_hotkeys", settings.enable_global_hotkeys))

    return _coerce_hotkey_bindings(mode_payload.get("hotkeyBindings"))


def apply_active_mode(settings: BitsEasySettings) -> Optional[List[Dict[str, Any]]]:
    payload = resolve_active_mode_payload(settings)
    if payload is None:
        return None
    return apply_mode_payload_to_settings(settings, payload)


def effective_keymap_bindings(
    base_bindings: List[Dict[str, Any]],
    mode_hotkey_bindings: Optional[List[Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    override = _coerce_hotkey_bindings(mode_hotkey_bindings)
    if override is not None:
        return [dict(row) for row in override]
    return [dict(row) for row in base_bindings if isinstance(row, dict)]

