import json
import hashlib
import tempfile
import unittest
from pathlib import Path

from bits_easy_runtime import AppAdapter, AppContext, RuntimeDispatcher, BitsEasyRuntime, load_runtime_config


class HotkeyPresetParityTests(unittest.TestCase):
    def test_export_import_hotkey_preset(self):
        repo_root = Path(__file__).resolve().parents[1]
        config = load_runtime_config(repo_root)
        runtime = BitsEasyRuntime(adapters={"edge": AppAdapter("edge", supports_selection=True)})
        dispatcher = RuntimeDispatcher(runtime, config, profile_id="balanced")
        ctx = AppContext("edge", "w", "c", "", 0, "")

        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "preset.json"
            exported = dispatcher.dispatch_command(ctx, "cmd.profile.hotkeyPresetExport", outPath=str(out))
            self.assertTrue(exported.result.ok)

            payload = json.loads(out.read_text(encoding="utf-8"))
            payload["bindings"] = payload.get("bindings", [])[:2]
            base = {"version": payload.get("version", 0), "bindings": payload.get("bindings", [])}
            payload["integrity"] = hashlib.sha256(
                json.dumps(base, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            out.write_text(json.dumps(payload, indent=2), encoding="utf-8")

            imported = dispatcher.dispatch_command(ctx, "cmd.profile.hotkeyPresetImport", inPath=str(out))
            self.assertTrue(imported.result.ok)
            self.assertEqual(imported.result.payload["bindingCount"], 2)


if __name__ == "__main__":
    unittest.main()

