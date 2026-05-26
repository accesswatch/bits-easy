import tempfile
import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime.shortcuts import ShortcutsStore


class ShortcutsStoreTests(unittest.TestCase):
    def test_shortcut_lifecycle_categories_and_presets(self):
        with tempfile.TemporaryDirectory() as td:
            store = ShortcutsStore(Path(td) / "shortcuts.json")

            created = store.create_shortcut(name="Docs", target="C:/docs", target_type="folder")
            self.assertTrue(created.ok)
            sid = created.payload["shortcutId"]

            categorized = store.assign_category(sid, "work")
            self.assertTrue(categorized.ok)

            listed = store.list_shortcuts(category="work")
            self.assertTrue(listed.ok)
            self.assertGreaterEqual(len(listed.payload["items"]), 1)

            preset = store.create_preset("daily", [sid])
            self.assertTrue(preset.ok)
            run = store.run_preset("daily")
            self.assertTrue(run.ok)
            self.assertEqual(len(run.payload["items"]), 1)

    def test_launcher_and_drive_mapping(self):
        with tempfile.TemporaryDirectory() as td:
            store = ShortcutsStore(Path(td) / "shortcuts.json")

            launcher = store.list_launcher()
            self.assertTrue(launcher.ok)
            self.assertGreaterEqual(launcher.payload["count"], 1)

            add_focused = store.add_focused_app("notepad")
            self.assertTrue(add_focused.ok)
            sid = add_focused.payload["shortcutId"]

            removed = store.remove_from_launcher(sid)
            self.assertTrue(removed.ok)

            restored = store.restore_launcher_defaults()
            self.assertTrue(restored.ok)
            self.assertGreaterEqual(restored.payload["launcherCount"], 1)

            mapped = store.map_drive("Z", "C:/work")
            self.assertTrue(mapped.ok)
            self.assertEqual(mapped.payload["driveLetter"], "Z:")

            listed = store.list_drive_mappings()
            self.assertTrue(listed.ok)
            self.assertEqual(listed.payload["count"], 1)

            unmapped = store.unmap_drive("Z")
            self.assertTrue(unmapped.ok)


if __name__ == "__main__":
    unittest.main()

