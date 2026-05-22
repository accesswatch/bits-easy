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
    "cmd.clip.browser.open",
    "cmd.clip.browser.filter",
    "cmd.clip.browser.sort",
    "cmd.clip.browser.batchAction",
    "cmd.clip.browser.compare",
    "cmd.clip.browser.reorder",
    "cmd.clip.browser.split",
    "cmd.clip.browser.merge",
    "cmd.clip.browser.exportPack",
    "cmd.clip.browser.importPack",
    "cmd.merge.setModeAppend",
    "cmd.merge.setModeReplace",
    "cmd.merge.setDividerLine",
    "cmd.merge.setDividerSpace",
    "cmd.merge.setDividerParagraph",
    "cmd.merge.setCustomSeparator",
    "cmd.merge.toggleClearOnPaste",
    "cmd.merge.applyProfile",
    "cmd.merge.commit",
]

REQUIRED_TEST_FILES = [
    "tests/test_selection_clipboard_e2e.py",
    "tests/test_dispatcher_integration.py",
    "tests/test_pocketclips_studio.py",
    "tests/test_v1_v11_completion.py",
]

REQUIRED_FIXTURE_MARKERS = [
    "drift",
    "unsupported",
    "fallback",
]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    repo = Path(__file__).resolve().parents[1]

    catalog = load_json(repo / "config" / "hotkeys" / "commands" / "tier1-commands.v1.json")
    profiles = [
        load_json(repo / "config" / "hotkeys" / "profiles" / "beginner.json"),
        load_json(repo / "config" / "hotkeys" / "profiles" / "balanced.json"),
        load_json(repo / "config" / "hotkeys" / "profiles" / "expert.json"),
    ]

    ids = {row.get("id", "") for row in catalog}
    missing_commands = [cid for cid in REQUIRED_COMMANDS if cid not in ids]

    missing_tests = [f for f in REQUIRED_TEST_FILES if not (repo / f).exists()]

    merged_test_text = "\n".join((repo / f).read_text(encoding="utf-8") for f in REQUIRED_TEST_FILES if (repo / f).exists()).lower()
    missing_markers = [m for m in REQUIRED_FIXTURE_MARKERS if m not in merged_test_text]

    speech_modes = {p.get("speechMode", "") for p in profiles}
    braille_modes = {p.get("brailleMode", "") for p in profiles}
    parity_ok = (len(speech_modes) >= 2 and len(braille_modes) >= 1)

    if missing_commands or missing_tests or missing_markers or not parity_ok:
        print("E01 parity closure failed.")
        if missing_commands:
            print("Missing commands:")
            for cmd in missing_commands:
                print(f" - {cmd}")
        if missing_tests:
            print("Missing test files:")
            for path in missing_tests:
                print(f" - {path}")
        if missing_markers:
            print("Missing fixture markers:")
            for marker in missing_markers:
                print(f" - {marker}")
        if not parity_ok:
            print("Speech and braille parity profile spread is insufficient.")
        return 1

    print("E01 parity closure check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
