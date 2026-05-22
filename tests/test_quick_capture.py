import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime.quick_capture import QuickCaptureInbox


class QuickCaptureInboxTests(unittest.TestCase):
    def test_capture_route_and_list(self):
        inbox = QuickCaptureInbox()

        saved = inbox.capture("note text", source_app="edge", window_id="win-1")
        self.assertTrue(saved.ok)
        cid = saved.payload["captureId"]
        self.assertEqual(saved.payload["sourceApp"], "edge")

        routed = inbox.route(cid, "notes")
        self.assertTrue(routed.ok)

        listing = inbox.list_items(route="notes")
        self.assertTrue(listing.ok)
        self.assertEqual(listing.payload["count"], 1)

    def test_persistence_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = Path(tmpdir) / "capture.json"
            inbox = QuickCaptureInbox(store)
            saved = inbox.capture("persist me", source_app="word", window_id="win-1")
            self.assertTrue(saved.ok)

            restored = QuickCaptureInbox(store)
            listing = restored.list_items()
            self.assertEqual(listing.payload["count"], 1)
            self.assertEqual(listing.payload["items"][0]["sourceApp"], "word")


if __name__ == "__main__":
    unittest.main()
