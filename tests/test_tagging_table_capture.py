import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime.table_capture import TableCaptureExtractor
from bits_easy_runtime.tagging import TaggingSession


class TaggingAndTableCaptureTests(unittest.TestCase):
    def test_tagging_session_batch_and_cancel(self):
        session = TaggingSession()

        a = session.tag("C:/tmp/a.txt")
        b = session.tag("C:/tmp/b.txt")
        self.assertTrue(a.ok)
        self.assertTrue(b.ok)

        count = session.count()
        self.assertTrue(count.ok)
        self.assertEqual(count.payload["count"], 2)

        report = session.report()
        self.assertTrue(report.ok)
        self.assertEqual(len(report.payload["items"]), 2)

        batch = session.batch_action("delete")
        self.assertTrue(batch.ok)
        self.assertTrue(batch.payload["confirmationRequired"])

        cancelled = session.cancel()
        self.assertTrue(cancelled.ok)
        self.assertEqual(cancelled.payload["cleared"], 2)

    def test_table_capture_append_and_export(self):
        capture = TableCaptureExtractor()

        first = capture.capture([["Name", "Value"], ["Alpha", "1"]], separator=",")
        second = capture.capture([["Beta", "2"]], separator=",")
        self.assertTrue(first.ok)
        self.assertTrue(second.ok)

        exported = capture.export_buffer(block_separator="\n")
        self.assertTrue(exported.ok)
        self.assertIn("Name,Value", exported.payload["content"])
        self.assertIn("Beta,2", exported.payload["content"])

        cleared = capture.clear_buffer()
        self.assertTrue(cleared.ok)
        self.assertEqual(cleared.payload["cleared"], 2)

    def test_tagging_duplicate_reports_already_tagged(self):
        session = TaggingSession()

        first = session.tag("C:/tmp/dup.txt")
        second = session.tag("C:/tmp/dup.txt")

        self.assertTrue(first.ok)
        self.assertTrue(second.ok)
        self.assertFalse(first.payload["alreadyTagged"])
        self.assertTrue(second.payload["alreadyTagged"])
        self.assertEqual(second.payload["count"], 1)


if __name__ == "__main__":
    unittest.main()

