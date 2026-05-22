import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime.system_report import SystemReportService
from spellforge_runtime.window_bookmarks import WindowBookmarks


class WindowBookmarksAndSystemReportTests(unittest.TestCase):
    def test_window_bookmark_lifecycle(self):
        with tempfile.TemporaryDirectory() as td:
            store = WindowBookmarks(Path(td) / "bookmarks.json")

            assigned = store.assign(1, window_id="win-1", app_id="edge", name="Edge Main")
            self.assertTrue(assigned.ok)

            recalled = store.recall(1)
            self.assertTrue(recalled.ok)
            self.assertEqual(recalled.payload["windowId"], "win-1")

            renamed = store.rename(1, "Primary Edge")
            self.assertTrue(renamed.ok)

            listing = store.list_slots()
            self.assertTrue(listing.ok)
            self.assertEqual(listing.payload["count"], 1)

    def test_system_report_collect_and_export(self):
        service = SystemReportService()
        collected = service.collect()
        self.assertTrue(collected.ok)
        self.assertIn("os", collected.payload)

        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "report.txt"
            exported = service.export(out)
            self.assertTrue(exported.ok)
            self.assertTrue(out.exists())


if __name__ == "__main__":
    unittest.main()
