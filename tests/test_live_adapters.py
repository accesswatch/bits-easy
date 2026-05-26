import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime import (
    AppContext,
    BrowserLiveAdapter,
    OutlookLiveAdapter,
    WordLiveAdapter,
    app_id_from_focus_object,
    snapshot_from_focus_object,
)


class _AppModule:
    def __init__(self, app_name: str):
        self.appName = app_name


class _Point:
    def __init__(self, offset: int):
        self._offset = offset


class _TextInfo:
    def __init__(self, text: str, start: int = 0, end: int = 0):
        self.text = text
        self._start = _Point(start)
        self._end = _Point(end)


class _FocusObject:
    def __init__(self, app_name: str, all_text: str, selected_text: str, caret: int, sel_start: int, sel_end: int):
        self.appModule = _AppModule(app_name)
        self.windowHandle = 1001
        self.name = "editor"
        self.role = "editableText"
        self.value = all_text
        self._all_text = all_text
        self._selected_text = selected_text
        self._caret = caret
        self._sel_start = sel_start
        self._sel_end = sel_end

    def makeTextInfo(self, mode):
        if mode == "selection":
            return _TextInfo(self._selected_text, self._sel_start, self._sel_end)
        if mode == "all":
            return _TextInfo(self._all_text, 0, len(self._all_text))
        if mode == "caret":
            return _TextInfo("", self._caret, self._caret)
        raise RuntimeError("unsupported mode")


class LiveAdapterTests(unittest.TestCase):
    def test_app_id_detection(self):
        self.assertEqual(app_id_from_focus_object(_FocusObject("winword", "", "", 0, 0, 0)), "word")
        self.assertEqual(app_id_from_focus_object(_FocusObject("outlook", "", "", 0, 0, 0)), "outlook")
        self.assertEqual(app_id_from_focus_object(_FocusObject("msedge", "", "", 0, 0, 0)), "edge")
        self.assertEqual(app_id_from_focus_object(_FocusObject("chrome", "", "", 0, 0, 0)), "chrome")

    def test_snapshot_from_focus_object_extracts_selection(self):
        focus = _FocusObject(
            app_name="winword",
            all_text="alpha bravo charlie",
            selected_text="bravo",
            caret=11,
            sel_start=6,
            sel_end=11,
        )
        snapshot = snapshot_from_focus_object(focus)
        self.assertEqual(snapshot.app_id, "word")
        self.assertEqual(snapshot.selected_text, "bravo")
        self.assertEqual(snapshot.selection_start, 6)
        self.assertEqual(snapshot.selection_end, 11)

    def test_word_live_adapter_prefers_selected_text(self):
        focus = _FocusObject(
            app_name="winword",
            all_text="alpha bravo charlie",
            selected_text="bravo",
            caret=11,
            sel_start=6,
            sel_end=11,
        )
        adapter = WordLiveAdapter(snapshot_provider=lambda: snapshot_from_focus_object(focus))
        ctx = AppContext(
            app_id="word",
            window_id="1001",
            control_id="editor",
            buffer="alpha bravo charlie",
            caret=11,
            clipboard_text="",
        )
        sel = adapter.normalize_range(ctx, start=2, end=3)
        self.assertEqual(sel.text, "bravo")
        self.assertEqual(sel.start, 6)
        self.assertEqual(sel.end, 11)

    def test_browser_and_outlook_adapters_construct(self):
        focus = _FocusObject(
            app_name="chrome",
            all_text="page body text",
            selected_text="body",
            caret=9,
            sel_start=5,
            sel_end=9,
        )
        browser = BrowserLiveAdapter("chrome", snapshot_provider=lambda: snapshot_from_focus_object(focus))
        outlook = OutlookLiveAdapter(snapshot_provider=lambda: snapshot_from_focus_object(focus))

        ctx = AppContext(
            app_id="chrome",
            window_id="1001",
            control_id="editor",
            buffer="page body text",
            caret=9,
            clipboard_text="",
        )
        self.assertEqual(browser.normalize_range(ctx, 0, 1).text, "body")
        self.assertEqual(outlook.normalize_range(ctx, 0, 1).text, "body")


if __name__ == "__main__":
    unittest.main()

