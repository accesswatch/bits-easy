from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class RuntimeConfig:
    command_catalog: Dict[str, Dict[str, Any]]
    keymap_bindings: List[Dict[str, Any]]
    profiles: Dict[str, Dict[str, Any]]

    @staticmethod
    def _equivalent_key_chords(key_chord: str) -> List[str]:
        chord = str(key_chord or "").strip()
        if not chord:
            return []

        candidates: List[str] = [chord]
        if chord.startswith("CapsLock+"):
            suffix = chord[len("CapsLock+"):]
            candidates.append("NVDA+" + suffix)
            candidates.append("Control+Alt+" + suffix)
        elif chord.startswith("Control+Alt+"):
            suffix = chord[len("Control+Alt+"):]
            candidates.append("CapsLock+" + suffix)
            candidates.append("NVDA+" + suffix)
        elif chord.startswith("NVDA+"):
            suffix = chord[len("NVDA+"):]
            candidates.append("CapsLock+" + suffix)
            candidates.append("Control+Alt+" + suffix)
        return candidates

    def command(self, command_id: str) -> Optional[Dict[str, Any]]:
        return self.command_catalog.get(command_id)

    def key_binding_for_command(self, command_id: str) -> Optional[Dict[str, Any]]:
        for binding in self.keymap_bindings:
            if binding.get("commandId") == command_id and binding.get("enabled", True):
                return binding
        return None

    def key_binding_for_chord(self, key_chord: str) -> Optional[Dict[str, Any]]:
        candidates = set(self._equivalent_key_chords(key_chord))
        for binding in self.keymap_bindings:
            if (
                binding.get("keyChord") in candidates
                and binding.get("enabled", True)
                and (binding.get("trigger") is None or binding["trigger"].get("kind") == "single-press")
            ):
                return binding
        return None

    def bindings_for_chord(self, key_chord: str, app_id: str, mode: str = "global") -> List[Dict[str, Any]]:
        trace = self.binding_resolution_trace(key_chord, app_id, mode)
        accepted = [row for row in trace if row.get("accepted")]
        accepted.sort(key=lambda row: (int(row.get("rank", 99)), int(row.get("index", 0))))
        return [self.keymap_bindings[int(row.get("index", 0))] for row in accepted]

    def binding_resolution_trace(self, key_chord: str, app_id: str, mode: str = "global") -> List[Dict[str, Any]]:
        trace: List[Dict[str, Any]] = []
        candidates = set(self._equivalent_key_chords(key_chord))
        for idx, binding in enumerate(self.keymap_bindings):
            if binding.get("keyChord") not in candidates:
                continue

            scope = str(binding.get("scope", "global"))
            b_app = binding.get("appId")
            enabled = bool(binding.get("enabled", True))

            row: Dict[str, Any] = {
                "index": idx,
                "commandId": str(binding.get("commandId", "")),
                "scope": scope,
                "appId": b_app,
                "enabled": enabled,
                "accepted": False,
                "rank": 99,
                "layer": "rejected",
                "reason": "unknown",
            }

            if not enabled:
                row["reason"] = "disabled"
                trace.append(row)
                continue

            if b_app not in (None, app_id):
                row["reason"] = "app-mismatch"
                trace.append(row)
                continue

            is_app_match = b_app == app_id
            rank = 99
            layer = "rejected"
            reason = "scope-mismatch"

            if scope == "app-override" and is_app_match:
                rank = 0
                layer = "app-override"
                reason = "matched-app-override"
            elif scope == "global" and is_app_match:
                rank = 1
                layer = "global-app"
                reason = "matched-global-app"
            elif scope == "virtualized" and mode == "virtualized" and b_app is None:
                rank = 2
                layer = "virtualized"
                reason = "matched-virtualized"
            elif scope == "global" and b_app is None:
                rank = 3
                layer = "global-shared"
                reason = "matched-global-shared"

            if rank < 99:
                row["accepted"] = True
                row["rank"] = rank
                row["layer"] = layer
            row["reason"] = reason
            trace.append(row)

        return trace

    def profile_policy(self, profile_id: str, command_id: str) -> Optional[Dict[str, Any]]:
        profile = self.profiles.get(profile_id)
        if profile is None:
            return None
        for policy in profile.get("commandPolicies", []):
            if policy.get("commandId") == command_id:
                return policy
        return None

    def profile_multi_press_enabled(self, profile_id: str) -> bool:
        profile = self.profiles.get(profile_id)
        if profile is None:
            return True
        return bool(profile.get("multiPressEnabled", True))

    def profile_fallback_order(self, profile_id: str) -> List[str]:
        profile = self.profiles.get(profile_id)
        if profile is None:
            return ["binding", "palette"]

        raw = profile.get("fallbackOrder", ["binding", "palette"])
        if not isinstance(raw, list):
            return ["binding", "palette"]

        allowed = {"binding", "palette", "none"}
        order = [str(x) for x in raw if str(x) in allowed]
        return order or ["binding", "palette"]


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_runtime_config(repo_root: Path) -> RuntimeConfig:
    config_root = repo_root / "config" / "hotkeys"

    catalog_raw = _load_json(config_root / "commands" / "tier1-commands.v1.json")
    keymap_raw = _load_json(config_root / "global-keymap.v1.json")

    profiles = {
        "beginner": _load_json(config_root / "profiles" / "beginner.json"),
        "balanced": _load_json(config_root / "profiles" / "balanced.json"),
        "expert": _load_json(config_root / "profiles" / "expert.json"),
    }

    catalog = {cmd["id"]: cmd for cmd in catalog_raw}
    bindings = list(keymap_raw.get("bindings", []))

    return RuntimeConfig(command_catalog=catalog, keymap_bindings=bindings, profiles=profiles)
