import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime.operation_journal import OperationJournal


class OperationJournalTests(unittest.TestCase):
    def test_record_list_and_rollback_guard(self):
        journal = OperationJournal()

        rec = journal.record(
            app_id="edge",
            command_id="cmd.capture.quickInbox.route",
            action_type="mutating",
            summary="Quick capture routed.",
            reversible=False,
        )
        self.assertTrue(rec.ok)
        eid = rec.payload["entryId"]

        listing = journal.list_entries(app_id="edge")
        self.assertEqual(listing.payload["count"], 1)

        rollback = journal.rollback(eid)
        self.assertFalse(rollback.ok)

    def test_persistence_and_rollback_handler_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = Path(tmpdir) / "journal.json"
            journal = OperationJournal(store)
            rec = journal.record(
                app_id="edge",
                command_id="cmd.capture.quickInbox.route",
                action_type="mutating",
                summary="Quick capture routed.",
                reversible=True,
                rollback_action={
                    "commandId": "cmd.capture.quickInbox.route",
                    "kwargs": {"captureId": "cap-0001", "target": "inbox"},
                },
            )
            self.assertTrue(rec.ok)
            eid = rec.payload["entryId"]

            reloaded = OperationJournal(store)
            prep = reloaded.rollback(eid)
            self.assertTrue(prep.ok)
            self.assertEqual(prep.payload["rollbackAction"]["commandId"], "cmd.capture.quickInbox.route")

            marked = reloaded.mark_rollback_applied(eid, success=True)
            self.assertTrue(marked.ok)

            after = reloaded.list_entries(app_id="edge")
            self.assertEqual(after.payload["items"][0]["rollbackStatus"], "applied")


if __name__ == "__main__":
    unittest.main()

