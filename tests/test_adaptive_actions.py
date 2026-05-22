import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime.adaptive_actions import AdaptiveActionEngine


class AdaptiveActionEngineTests(unittest.TestCase):
    def test_summarize_extract_rewrite(self):
        engine = AdaptiveActionEngine()
        text = "We should follow up with the team next week and create an action list for onboarding tasks."

        summary = engine.summarize(text)
        self.assertTrue(summary.ok)
        self.assertIn("confidence", summary.payload)

        actions = engine.extract_actions(text)
        self.assertTrue(actions.ok)
        self.assertGreaterEqual(len(actions.payload["items"]), 1)

        rewrite = engine.rewrite_beginner("Please utilize the guide approximately once per day.")
        self.assertTrue(rewrite.ok)
        self.assertIn("use", rewrite.payload["content"])


if __name__ == "__main__":
    unittest.main()
