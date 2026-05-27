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

        tsv = capture.export_buffer(format="tsv")
        self.assertTrue(tsv.ok)
        self.assertIn("Name\tValue", tsv.payload["content"])

        markdown = capture.export_buffer(format="markdown")
        self.assertTrue(markdown.ok)
        self.assertIn("| Name", markdown.payload["content"])

        html = capture.export_buffer(format="html")
        self.assertTrue(html.ok)
        self.assertIn("<table>", html.payload["content"])

        json_rows = capture.export_buffer(format="json")
        self.assertTrue(json_rows.ok)
        self.assertIn('"Name": "Alpha"', json_rows.payload["content"])

        cleared = capture.clear_buffer()
        self.assertTrue(cleared.ok)
        self.assertEqual(cleared.payload["cleared"], 2)

    def test_table_capture_granular_row_column_header_cell(self):
        capture = TableCaptureExtractor()
        seeded = capture.capture(
            [["Name", "Status"], ["Alpha", "Open"], ["Beta", "Closed"]],
            separator=" | ",
        )
        self.assertTrue(seeded.ok)

        header = capture.capture_header(separator=" | ")
        self.assertTrue(header.ok)
        self.assertEqual(header.payload["content"], "Name | Status")

        row = capture.capture_row(row_index=2, separator=" | ")
        self.assertTrue(row.ok)
        self.assertEqual(row.payload["content"], "Alpha | Open")

        column = capture.capture_column(column_index=2, separator="\n")
        self.assertTrue(column.ok)
        self.assertIn("Status", column.payload["content"])
        self.assertIn("Closed", column.payload["content"])

        cell = capture.capture_cell(row_index=3, column_index=2)
        self.assertTrue(cell.ok)
        self.assertEqual(cell.payload["content"], "Closed")

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

