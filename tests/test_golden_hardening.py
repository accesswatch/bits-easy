import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime import (
    AppAdapter,
    AppContext,
    RuntimeDispatcher,
    SpellforgeRuntime,
    load_runtime_config,
)


class GoldenHardeningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.config = load_runtime_config(self.repo_root)
        self.runtime = SpellforgeRuntime(
            adapters={
                "edge": AppAdapter("edge", supports_selection=True),
                "word": AppAdapter("word", supports_selection=True),
            }
        )

    def _ctx(self, app_id: str = "edge", buffer: str = "alpha bravo", caret: int = 0) -> AppContext:
        return AppContext(
            app_id=app_id,
            window_id=f"win-{app_id}",
            control_id="main-editor",
            buffer=buffer,
            caret=caret,
            clipboard_text=buffer,
        )

    def test_restart_resilience_for_completed_features(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            data_root = Path(tmpdir) / "spellforge"

            d1 = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced", data_root=data_root)
            ctx = self._ctx("edge", "capture me", 0)

            # E18 quick capture + journal
            cap = d1.dispatch_command(ctx, "cmd.capture.quickInbox")
            self.assertTrue(cap.result.ok)
            cap_id = cap.result.payload["captureId"]
            self.assertTrue(d1.dispatch_command(ctx, "cmd.capture.quickInbox.route", captureId=cap_id, target="notes").result.ok)

            # E07 time/tasks
            self.assertTrue(
                d1.dispatch_command(
                    ctx,
                    "cmd.tasks.create",
                    title="Prepare release",
                    dueAt="2026-05-21T16:00:00+00:00",
                    category="work",
                    priority="high",
                ).result.ok
            )

            # E08 contacts/social
            create_contact = d1.dispatch_command(
                ctx,
                "cmd.contacts.create",
                name="Jane Doe",
                email="jane@example.com",
                phone="555-0101",
            )
            self.assertTrue(create_contact.result.ok)

            # E10 db/records
            self.assertTrue(d1.dispatch_command(ctx, "cmd.db.create", name="inventory").result.ok)
            self.assertTrue(d1.dispatch_command(ctx, "cmd.db.field.define", name="name", fieldType="text", required=True).result.ok)
            self.assertTrue(d1.dispatch_command(ctx, "cmd.db.entry.add", values={"name": "item-a"}).result.ok)

            # Simulate restart
            d2 = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced", data_root=data_root)

            cap_list = d2.dispatch_command(ctx, "cmd.capture.quickInbox.list", route="notes")
            self.assertTrue(cap_list.result.ok)
            self.assertEqual(cap_list.result.payload["count"], 1)

            journal = d2.dispatch_command(ctx, "cmd.journal.list", appId="edge", actionType="mutating")
            self.assertTrue(journal.result.ok)
            self.assertGreaterEqual(journal.result.payload["count"], 1)

            tasks = d2.dispatch_command(ctx, "cmd.tasks.list", status="open", category="work", priority="high")
            self.assertTrue(tasks.result.ok)
            self.assertEqual(tasks.result.payload["count"], 1)

            contacts = d2.dispatch_command(ctx, "cmd.contacts.search", query="jane")
            self.assertTrue(contacts.result.ok)
            self.assertEqual(contacts.result.payload["count"], 1)

            self.assertTrue(d2.dispatch_command(ctx, "cmd.db.select", name="inventory").result.ok)
            entries = d2.dispatch_command(ctx, "cmd.db.entry.list")
            self.assertTrue(entries.result.ok)
            self.assertEqual(entries.result.payload["count"], 1)


if __name__ == "__main__":
    unittest.main()
