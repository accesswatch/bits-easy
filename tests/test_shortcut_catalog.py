import json
import tempfile
import unittest
from pathlib import Path

from bits_easy_runtime.shortcut_catalog import ShortcutCatalogStore


class ShortcutCatalogStoreTests(unittest.TestCase):
    def test_shortcut_lifecycle_and_filters(self):
        with tempfile.TemporaryDirectory() as td:
            store = ShortcutCatalogStore(Path(td) / "cuts.json")

            created = store.create_shortcut(name="Docs", target="C:/docs", target_type="folder")
            self.assertTrue(created.ok)
            sid = created.payload["shortcutId"]

            assigned = store.assign_category(sid, "work")
            self.assertTrue(assigned.ok)

            listed = store.list_shortcuts(category="work")
            self.assertTrue(listed.ok)
            self.assertEqual(len(listed.payload["items"]), 1)

            launched = store.launch_shortcut(sid)
            self.assertTrue(launched.ok)
            self.assertEqual(launched.payload["targetType"], "folder")

            deleted = store.delete_shortcut(sid)
            self.assertTrue(deleted.ok)

    def test_presets_export_import_integrity(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            store = ShortcutCatalogStore(root / "cuts.json")
            sid_a = store.create_shortcut(name="Site", target="https://example.com", target_type="web").payload["shortcutId"]
            sid_b = store.create_shortcut(name="Repo", target="C:/code", target_type="folder").payload["shortcutId"]

            preset = store.create_preset("morning", [sid_a, sid_b])
            self.assertTrue(preset.ok)

            out = root / "cuts-pack.json"
            exported = store.export_presets(out)
            self.assertTrue(exported.ok)

            # Tamper and ensure integrity failure.
            payload = json.loads(out.read_text(encoding="utf-8"))
            payload["shortcuts"][sid_a]["target"] = "https://tampered.example"
            out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            bad = store.import_presets(out)
            self.assertFalse(bad.ok)

            # Re-export valid pack and import in second store.
            store.export_presets(out)
            store_b = ShortcutCatalogStore(root / "cuts-b.json")
            imported = store_b.import_presets(out)
            self.assertTrue(imported.ok)

            ran = store_b.run_preset("morning")
            self.assertTrue(ran.ok)
            self.assertEqual(len(ran.payload["items"]), 2)


if __name__ == "__main__":
    unittest.main()

