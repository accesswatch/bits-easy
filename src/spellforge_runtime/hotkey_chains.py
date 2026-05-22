from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from .diagnostics import get_logger
from .engine import RuntimeResult

_logger = get_logger("spellforge.hotkey_chains")


class HotkeyChainStore:
    def __init__(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self._chains: Dict[str, List[str]] = {}
        self._load()

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            payload = json.loads(self.storage_path.read_text(encoding="utf-8"))
            self._chains = {
                str(name): [str(cmd) for cmd in commands]
                for name, commands in (payload.get("chains", {}) or {}).items()
            }
        except Exception:
            _logger.exception("Spellforge: loading hotkey chains at %s failed", self.storage_path)
            self._chains = {}

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "chains": self._chains}
        self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def create_chain(self, name: str, command_ids: List[str]) -> RuntimeResult:
        chain_name = name.strip()
        if not chain_name:
            return RuntimeResult(ok=False, message="Chain name cannot be empty.")
        cmds = [str(c).strip() for c in command_ids if str(c).strip()]
        if not cmds:
            return RuntimeResult(ok=False, message="Chain must include at least one command.")
        self._chains[chain_name] = cmds
        self._save()
        return RuntimeResult(ok=True, message="Hotkey chain saved.", payload={"chain": chain_name, "count": len(cmds)})

    def list_chains(self) -> RuntimeResult:
        items = [
            {"chain": name, "commands": cmds, "count": len(cmds)}
            for name, cmds in sorted(self._chains.items(), key=lambda row: row[0].lower())
        ]
        return RuntimeResult(ok=True, message="Hotkey chains ready.", payload={"items": items, "count": len(items)})

    def get_chain(self, name: str) -> RuntimeResult:
        chain_name = name.strip()
        cmds = self._chains.get(chain_name)
        if cmds is None:
            return RuntimeResult(ok=False, message="Hotkey chain not found.")
        return RuntimeResult(ok=True, message="Hotkey chain loaded.", payload={"chain": chain_name, "commands": list(cmds)})
