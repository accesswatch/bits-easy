import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime.dialog_paths import DialogPathInserter


class DialogPathTests(unittest.TestCase):
    def test_detect_and_insert_with_fallback(self):
        ins = DialogPathInserter()

        detected = ins.detect("Open File")
        self.assertTrue(detected.ok)
        self.assertEqual(detected.payload["kind"], "open")

        inserted = ins.insert_path("C:/work", window_title="Open File", supports_insertion=True)
        self.assertTrue(inserted.ok)
        self.assertTrue(inserted.payload["inserted"])

        fallback = ins.insert_path("C:/work", window_title="Open File", supports_insertion=False)
        self.assertTrue(fallback.ok)
        self.assertFalse(fallback.payload["inserted"])
        self.assertGreaterEqual(len(fallback.payload["fallbackGuidance"]), 1)


if __name__ == "__main__":
    unittest.main()
