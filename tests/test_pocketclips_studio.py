import unittest
import tempfile
from pathlib import Path

from bits_easy_runtime.engine import AppAdapter, AppContext, BitsEasyRuntime
from bits_easy_runtime.pocketclips import PocketClipsStudio


class PocketClipsStudioTests(unittest.TestCase):
    def setUp(self):
        self.runtime = BitsEasyRuntime(
            adapters={
                "word": AppAdapter("word", supports_selection=True),
                "outlook": AppAdapter("outlook", supports_selection=False),
            },
            storage_path=None,
        )
        self.ctx = AppContext(
            app_id="word",
            window_id="w1",
            control_id="editor",
            buffer="Hello from Word",
            caret=5,
            clipboard_text="Hello from Word",
        )
        self.runtime.copy_to_slot(self.ctx, 1)
        self.runtime.copy_to_slot(self.ctx, 2, text="Hello from Outlook")
        self.studio = PocketClipsStudio(self.runtime)

    def test_list_and_compare_slots(self):
        rows = self.studio.list_slots(sort_by="size")
        self.assertGreaterEqual(len(rows), 2)

        cmp_result = self.studio.compare_slots(1, 2)
        self.assertTrue(cmp_result.ok)
        self.assertIn("addedWords", cmp_result.payload)
        self.assertIn("similarity", cmp_result.payload)
        self.assertIn("lineDiffPreview", cmp_result.payload)

    def test_batch_protect_then_unprotect(self):
        protect = self.studio.batch_action([1, 2], "protect")
        self.assertTrue(protect.ok)
        unprotect = self.studio.batch_action([1, 2], "unprotect")
        self.assertTrue(unprotect.ok)

    def test_search_and_favorites_and_copy_out(self):
        pin = self.studio.batch_action([2], "pin")
        self.assertTrue(pin.ok)

        rows = self.studio.list_slots(query="Outlook", favorites_only=True)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].slot, 2)
        self.assertTrue(rows[0].favorite)

        copied = self.studio.batch_action([1, 2], "copyOut", separator=" | ")
        self.assertTrue(copied.ok)
        self.assertIn("content", copied.payload)
        self.assertIn(" | ", copied.payload["content"])

        unpin = self.studio.batch_action([2], "unpin")
        self.assertTrue(unpin.ok)

    def test_slot_pack_integrity_and_malformed_reject(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "pack.json"
            out = self.studio.export_pack([1, 2], path)
            self.assertTrue(out.ok)

            payload = path.read_text(encoding="utf-8")
            self.assertIn("integrity", payload)

            tampered = payload.replace("Hello from", "H3llo from", 1)
            path.write_text(tampered, encoding="utf-8")
            bad = self.studio.import_pack(path)
            self.assertFalse(bad.ok)

            malformed = Path(td) / "bad.json"
            malformed.write_text("{not valid json", encoding="utf-8")
            malformed_result = self.studio.import_pack(malformed)
            self.assertFalse(malformed_result.ok)


if __name__ == "__main__":
    unittest.main()

