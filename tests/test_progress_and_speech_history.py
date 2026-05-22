import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime.progress_cues import ProgressCueEngine
from spellforge_runtime.speech_history import SpeechHistory


class ProgressAndSpeechHistoryTests(unittest.TestCase):
    def test_progress_cue_plan_and_tutorial(self):
        engine = ProgressCueEngine(interval_percent=20)
        plan = engine.cue_plan(50, tutorial=True)
        self.assertTrue(plan.ok)
        self.assertGreaterEqual(len(plan.payload["cueSteps"]), 4)
        self.assertIn("tutorial", plan.payload)

    def test_speech_history_capture_browse_and_copy(self):
        history = SpeechHistory()
        self.assertTrue(history.append("first line").ok)
        self.assertTrue(history.append("second line").ok)
        self.assertTrue(history.append("third line").ok)

        prev = history.browse("left")
        self.assertTrue(prev.ok)
        self.assertEqual(prev.payload["text"], "second line")

        one = history.copy_item(1)
        self.assertTrue(one.ok)
        self.assertEqual(one.payload["text"], "second line")

        span = history.copy_range(0, 2, separator=" | ")
        self.assertTrue(span.ok)
        self.assertIn("first line | second line | third line", span.payload["text"])

        view = history.open_virtual_view()
        self.assertTrue(view.ok)
        self.assertEqual(view.payload["count"], 3)


if __name__ == "__main__":
    unittest.main()
