import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime import AppContext, OutlookLiveAdapter, WordLiveAdapter
from bits_easy_runtime.live_adapters import FocusSnapshot, detect_outlook_layout_signature
from bits_easy_runtime import BrowserLiveAdapter


class _Focus:
    def __init__(self, *, role: str, name: str, value: str = ""):
        self.role = role
        self.name = name
        self.value = value


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
        with self.assertRaises(Exception) as exc:
            adapter.normalize_range(ctx, 0, 3)
        self.assertIn("layout signature", str(exc.exception).lower())

    def test_outlook_reading_pane_prefers_native_selection_text(self):
        text = "Subject line. Reading pane message body here. Signature."
        adapter = OutlookLiveAdapter(
            snapshot_provider=lambda: FocusSnapshot(
                app_id="outlook",
                window_id="100",
                control_id="reading pane",
                role="document",
                text=text,
                caret=24,
                selected_text="Reading pane message body here.",
                variant="reading-pane",
            )
        )
        ctx = AppContext("outlook", "100", "reading pane", text, 24)
        sel = adapter.normalize_range(ctx, 13, 44)
        self.assertEqual(sel.text, "Reading pane message body here.")

    def test_word_surface_prefers_native_selection_text(self):
        text = "Row 1\nCell Alpha\nCell Beta"
        adapter = WordLiveAdapter(
            snapshot_provider=lambda: FocusSnapshot(
                app_id="word",
                window_id="100",
                control_id="document",
                role="table",
                text=text,
                caret=10,
                selected_text="Cell Alpha",
            )
        )
        ctx = AppContext("word", "100", "document", text, 10)
        sel = adapter.normalize_range(ctx, 6, 16)
        self.assertEqual(sel.text, "Cell Alpha")

    def test_outlook_layout_signature_detects_preview_and_folder_pane_aliases(self):
        self.assertEqual(
            detect_outlook_layout_signature(_Focus(role="pane", name="Preview Pane")),
            "outlook-layout-reading-pane",
        )
        self.assertEqual(
            detect_outlook_layout_signature(_Focus(role="treeView", name="Folder Pane")),
            "outlook-layout-folder-pane",
        )
        self.assertEqual(
            detect_outlook_layout_signature(_Focus(role="toolbar", name="Ribbon")),
            "outlook-layout-ribbon",
        )
        self.assertEqual(
            detect_outlook_layout_signature(_Focus(role="edit", name="Search")),
            "outlook-layout-search",
        )
        self.assertEqual(
            detect_outlook_layout_signature(_Focus(role="list", name="Search Results")),
            "outlook-layout-search-results",
        )

    def test_interactive_surface_falls_back_to_full_label_when_range_invalid(self):
        adapter = BrowserLiveAdapter(
            "chrome",
            snapshot_provider=lambda: FocusSnapshot(
                app_id="chrome",
                window_id="w1",
                control_id="lnk-1",
                role="link",
                text="Open advanced options",
                caret=0,
                selected_text="",
            ),
        )
        ctx = AppContext("chrome", "w1", "lnk-1", "", 0)
        sel = adapter.normalize_range(ctx, 0, 0)
        self.assertEqual(sel.text, "Open advanced options")
        self.assertEqual(sel.start, 0)
        self.assertEqual(sel.end, len("Open advanced options"))
        self.assertEqual(sel.source_kind, "interactive-label-fallback")


if __name__ == "__main__":
    unittest.main()

