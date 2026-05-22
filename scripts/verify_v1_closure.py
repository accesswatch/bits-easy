from __future__ import annotations

import json
from pathlib import Path
import sys


REQUIRED_COMMANDS = [
    "cmd.selection.markStart",
    "cmd.selection.markEnd",
    "cmd.selection.readContext",
    "cmd.selection.jumpStart",
    "cmd.selection.cancel",
    "cmd.clip.copyToSlot",
    "cmd.clip.pasteFromSlot",
    "cmd.clip.protectSlot",
    "cmd.clip.unprotectSlot",
    "cmd.clip.deleteSlot",
    "cmd.clip.editSlot",
    "cmd.clip.describeSlot",
    "cmd.merge.setModeAppend",
    "cmd.merge.setModeReplace",
    "cmd.merge.setDividerLine",
    "cmd.merge.setDividerSpace",
    "cmd.merge.setDividerParagraph",
    "cmd.merge.setCustomSeparator",
    "cmd.merge.toggleClearOnPaste",
    "cmd.merge.applyProfile",
    "cmd.merge.commit",
    "cmd.text.expansion.upsert",
    "cmd.text.expansion.expand",
    "cmd.text.expansion.list",
    "cmd.text.expansion.rename",
    "cmd.text.expansion.delete",
    "cmd.text.quickInsert",
    "cmd.text.expansion.setPrimary",
    "cmd.help.availableHotkeys",
    "cmd.profile.hotkeyDiagnostics",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    cmd_file = repo_root / "config" / "hotkeys" / "commands" / "tier1-commands.v1.json"
    keymap_file = repo_root / "config" / "hotkeys" / "global-keymap.v1.json"

    catalog = load_json(cmd_file)
    keymap = load_json(keymap_file)

    ids = {row["id"] for row in catalog}
    missing = [cid for cid in REQUIRED_COMMANDS if cid not in ids]
    if missing:
        print("V1 closure failed: missing required command IDs")
        for m in missing:
            print(f" - {m}")
        return 1

    known_bindings = {b.get("commandId", "") for b in keymap.get("bindings", [])}
    if "cmd.system.emergencyStop" not in known_bindings:
        print("V1 closure failed: emergency stop binding missing")
        return 1

    print("V1 closure check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
