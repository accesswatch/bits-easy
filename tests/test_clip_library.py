import unittest
import sys
from pathlib import Path
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime.clip_library import ClipLibraryStore
from spellforge_runtime.engine import AppAdapter, AppContext, SpellforgeRuntime


class ClipLibraryStoreTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.runtime = SpellforgeRuntime(adapters={"edge": AppAdapter("edge", supports_selection=True)})
        self.ctx = AppContext(
            app_id="edge",
            window_id="w1",
            control_id="editor",
            buffer="alpha bravo",
            caret=5,
            clipboard_text="alpha bravo",
        )
        self.runtime.copy_to_slot(self.ctx, 1, text="First clip")
        self.lib = ClipLibraryStore(self.runtime, Path(self._tmp.name) / "clip-library.json")

    def tearDown(self):
        self._tmp.cleanup()

    def test_archive_folder_link_restore(self):
        archived = self.lib.ingest_slot(1)
        self.assertTrue(archived.ok)
        clip_id = archived.payload["clipId"]

        folder = self.lib.create_folder("Work", category="project")
        self.assertTrue(folder.ok)
        folder_id = folder.payload["folderId"]

        moved = self.lib.move_to_folder(clip_id, folder_id)
        self.assertTrue(moved.ok)

        alias = self.lib.retain_slot_alias(clip_id, "Slot 1")
        self.assertTrue(alias.ok)

        linked = self.lib.link_to_folder(clip_id, folder_id)
        self.assertTrue(linked.ok)

        locations = self.lib.list_linked_locations(clip_id)
        self.assertTrue(locations.ok)
        self.assertGreaterEqual(len(locations.payload["locations"]), 1)

        restored = self.lib.restore_to_slot(clip_id, 2, mode="replace")
        self.assertTrue(restored.ok)

    def test_retention_and_folder_ops(self):
        archived = self.lib.ingest_slot(1)
        clip_id = archived.payload["clipId"]

        policy = self.lib.set_retention_policy(clip_id, "pin-protected")
        self.assertTrue(policy.ok)

        folder = self.lib.create_folder("Temp")
        folder_id = folder.payload["folderId"]
        renamed = self.lib.rename_folder(folder_id, "Temp2")
        self.assertTrue(renamed.ok)
        deleted = self.lib.delete_folder(folder_id)
        self.assertTrue(deleted.ok)


if __name__ == "__main__":
    unittest.main()
