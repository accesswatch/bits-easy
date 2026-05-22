import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime import AppContext, OutlookLiveAdapter, WordLiveAdapter
from spellforge_runtime.live_adapters import FocusSnapshot


class LiveAdapterEdgeCaseTests(unittest.TestCase):
    def test_outlook_message_list_unsupported(self):
        adapter = OutlookLiveAdapter(
            snapshot_provider=lambda: FocusSnapshot(
                app_id="outlook",
                window_id="100",
                control_id="message list",
                role="list",
                text="Inbox row",
                caret=0,
                variant="message-list",
            )
        )
        ctx = AppContext("outlook", "100", "message list", "Inbox row", 0)
        with self.assertRaises(Exception):
            adapter.normalize_range(ctx, 0, 3)

    def test_outlook_reading_pane_sentence_slice(self):
        text = "Subject line. Reading pane message body here. Signature."
        adapter = OutlookLiveAdapter(
            snapshot_provider=lambda: FocusSnapshot(
                app_id="outlook",
                window_id="100",
                control_id="reading pane",
                role="document",
                text=text,
                caret=24,
                variant="reading-pane",
            )
        )
        ctx = AppContext("outlook", "100", "reading pane", text, 24)
        sel = adapter.normalize_range(ctx, 0, 1)
        self.assertIn("Reading pane message body", sel.text)

    def test_word_table_line_fallback(self):
        text = "Row 1\nCell Alpha\nCell Beta"
        adapter = WordLiveAdapter(
            snapshot_provider=lambda: FocusSnapshot(
                app_id="word",
                window_id="100",
                control_id="document",
                role="table",
                text=text,
                caret=10,
                variant="table",
            )
        )
        ctx = AppContext("word", "100", "document", text, 10)
        sel = adapter.normalize_range(ctx, 0, 1)
        self.assertIn("Cell Alpha", sel.text)


if __name__ == "__main__":
    unittest.main()
