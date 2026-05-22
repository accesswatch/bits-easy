import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime.outlook_tagging import OutlookTaggingSession


class OutlookTaggingTests(unittest.TestCase):
    def test_outlook_tagging_batch_flow(self):
        session = OutlookTaggingSession()

        a = session.tag_message("m1", "alice@example.com", "Status")
        b = session.tag_message("m2", "bob@example.com", "Plan")
        self.assertTrue(a.ok)
        self.assertTrue(b.ok)

        report = session.report()
        self.assertTrue(report.ok)
        self.assertEqual(report.payload["count"], 2)

        move = session.batch_action("move", folder="Inbox/Work")
        self.assertTrue(move.ok)
        self.assertEqual(move.payload["action"], "move")

        delete = session.batch_action("delete")
        self.assertTrue(delete.ok)
        self.assertTrue(delete.payload["confirmationRequired"])

        cancel = session.cancel()
        self.assertTrue(cancel.ok)
        self.assertEqual(cancel.payload["cleared"], 2)


if __name__ == "__main__":
    unittest.main()
