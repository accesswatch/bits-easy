import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime import classify_surface, fallback_steps_for


class SurfaceContextTests(unittest.TestCase):
    def test_outlook_modes(self):
        compose = classify_surface("outlook", "editableText", "Compose editor")
        self.assertEqual(compose.mode, "outlook-compose")

        msg_list = classify_surface("outlook", "list", "Message list")
        self.assertEqual(msg_list.mode, "outlook-message-list")

    def test_browser_modes(self):
        doc = classify_surface("edge", "document", "web area")
        self.assertEqual(doc.mode, "browser-document")

        edit = classify_surface("chrome", "editableText", "search")
        self.assertEqual(edit.mode, "browser-editable")

    def test_fallbacks_are_contextual(self):
        steps = fallback_steps_for("outlook-message-list", "cmd.selection.markEnd")
        self.assertTrue(any("Open the message" in s for s in steps))


if __name__ == "__main__":
    unittest.main()
