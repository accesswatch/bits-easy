import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime import AppAdapter, AppContext, SpellforgeRuntime


class PersistenceAndCliTests(unittest.TestCase):
    def test_slot_persistence_survives_restart(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "slots.json"

            runtime_a = SpellforgeRuntime(
                adapters={"edge": AppAdapter("edge", supports_selection=True)},
                storage_path=storage,
            )
            ctx = AppContext(
                app_id="edge",
                window_id="win-edge",
                control_id="main-editor",
                buffer="",
                caret=0,
                clipboard_text="",
            )
            runtime_a.copy_to_slot(ctx, slot=1, text="persisted text")

            runtime_b = SpellforgeRuntime(
                adapters={"edge": AppAdapter("edge", supports_selection=True)},
                storage_path=storage,
            )
            paste = runtime_b.paste_from_slot(slot=1)
            self.assertTrue(paste.ok)
            self.assertEqual(paste.payload["content"], "persisted text")

    def test_cli_session_uses_json_keymap_and_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = Path(tmpdir) / "session-slots.json"
            script = Path(__file__).resolve().parents[1] / "scripts" / "hotkey-session.py"

            copy_proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--profile",
                    "beginner",
                    "--app",
                    "vscode",
                    "--storage",
                    str(storage),
                    "--press",
                    "CapsLock+1",
                    "--text",
                    "cli persisted",
                    "--slot",
                    "1",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            copy_out = json.loads(copy_proc.stdout.strip())
            self.assertTrue(copy_out["ok"])
            self.assertEqual(copy_out["commandId"], "cmd.clip.copyToSlot")

            describe_proc = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--profile",
                    "expert",
                    "--app",
                    "vscode",
                    "--storage",
                    str(storage),
                    "--press",
                    "CapsLock+4",
                    "--slot",
                    "1",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            describe_out = json.loads(describe_proc.stdout.strip())
            self.assertTrue(describe_out["ok"])
            self.assertEqual(describe_out["commandId"], "cmd.clip.describeSlot")
            self.assertEqual(describe_out["payload"]["sourceApp"], "vscode")


if __name__ == "__main__":
    unittest.main()
