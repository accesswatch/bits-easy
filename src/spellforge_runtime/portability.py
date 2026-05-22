from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict


def _canonical_content(payload: Dict[str, object]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def export_portability_bundle(repo_root: Path | str, out_file: Path | str) -> Path:
    root = Path(repo_root)
    out = Path(out_file)

    bundle: Dict[str, object] = {
        "version": 1,
        "profiles": {},
        "hotkeys": {},
        "settings": {},
        "slots": {},
    }

    for name in ("beginner", "balanced", "expert"):
        p = root / "config" / "hotkeys" / "profiles" / f"{name}.json"
        if p.exists():
            bundle["profiles"][name] = json.loads(p.read_text(encoding="utf-8"))

    keymap = root / "config" / "hotkeys" / "global-keymap.v1.json"
    commands = root / "config" / "hotkeys" / "commands" / "tier1-commands.v1.json"
    if keymap.exists():
        bundle["hotkeys"]["globalKeymap"] = json.loads(keymap.read_text(encoding="utf-8"))
    if commands.exists():
        bundle["hotkeys"]["commandCatalog"] = json.loads(commands.read_text(encoding="utf-8"))

    appdata = Path.home() / "AppData" / "Roaming" / "Spellforge"
    settings = appdata / "settings.json"
    slots = appdata / "clip-slots.json"
    if settings.exists():
        bundle["settings"] = json.loads(settings.read_text(encoding="utf-8"))
    if slots.exists():
        bundle["slots"] = json.loads(slots.read_text(encoding="utf-8"))

    canonical_payload = {
        "version": bundle["version"],
        "profiles": bundle["profiles"],
        "hotkeys": bundle["hotkeys"],
        "settings": bundle["settings"],
        "slots": bundle["slots"],
    }
    bundle["integrity"] = hashlib.sha256(_canonical_content(canonical_payload).encode("utf-8")).hexdigest()

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return out


def import_portability_bundle(repo_root: Path | str, in_file: Path | str, overwrite_existing: bool = False) -> Dict[str, int]:
    root = Path(repo_root)
    src = Path(in_file)
    payload = json.loads(src.read_text(encoding="utf-8"))

    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise ValueError("Incompatible portability bundle version.")

    expected = hashlib.sha256(
        _canonical_content(
            {
                "version": payload.get("version"),
                "profiles": payload.get("profiles", {}),
                "hotkeys": payload.get("hotkeys", {}),
                "settings": payload.get("settings", {}),
                "slots": payload.get("slots", {}),
            }
        ).encode("utf-8")
    ).hexdigest()
    integrity = str(payload.get("integrity", ""))
    if integrity and integrity != expected:
        raise ValueError("Portability bundle integrity check failed.")

    restored = {"profiles": 0, "hotkeys": 0, "settings": 0, "slots": 0, "conflicts": 0}

    def maybe_write(path: Path, data: object, *, count_key: str) -> None:
        if path.exists() and not overwrite_existing:
            restored["conflicts"] += 1
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        restored[count_key] += 1

    profiles = payload.get("profiles", {})
    for name, data in profiles.items():
        out = root / "config" / "hotkeys" / "profiles" / f"{name}.json"
        maybe_write(out, data, count_key="profiles")

    hotkeys = payload.get("hotkeys", {})
    if "globalKeymap" in hotkeys:
        out = root / "config" / "hotkeys" / "global-keymap.v1.json"
        maybe_write(out, hotkeys["globalKeymap"], count_key="hotkeys")
    if "commandCatalog" in hotkeys:
        out = root / "config" / "hotkeys" / "commands" / "tier1-commands.v1.json"
        maybe_write(out, hotkeys["commandCatalog"], count_key="hotkeys")

    appdata = Path.home() / "AppData" / "Roaming" / "Spellforge"
    appdata.mkdir(parents=True, exist_ok=True)
    if payload.get("settings"):
        maybe_write(appdata / "settings.json", payload["settings"], count_key="settings")
    if payload.get("slots"):
        maybe_write(appdata / "clip-slots.json", payload["slots"], count_key="slots")

    return restored
