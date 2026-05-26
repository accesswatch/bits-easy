import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime import AppAdapter, AppContext, RuntimeDispatcher, BitsEasyRuntime, load_runtime_config


class V4FeatureCompletionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.config = load_runtime_config(self.repo_root)
        self.runtime = BitsEasyRuntime(adapters={"edge": AppAdapter("edge", supports_selection=True)})

    def _ctx(self, app: str = "edge", buffer: str = "alpha") -> AppContext:
        return AppContext(
            app_id=app,
            window_id=f"win-{app}",
            control_id="main-editor",
            buffer=buffer,
            caret=0,
            clipboard_text=buffer,
        )

    def test_retrieval_notes_file_context_and_jamal_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced", data_root=base / "data")
            ctx = self._ctx("edge", "quick content")

            q = dispatcher.dispatch_command(ctx, "cmd.retrieve.query", query="release notes")
            self.assertTrue(q.result.ok)
            self.assertTrue(
                dispatcher.dispatch_command(
                    ctx,
                    "cmd.retrieve.anchor.set",
                    domain="example.com",
                    page="/docs",
                    index=1,
                    phrase="release",
                ).result.ok
            )
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.retrieve.trail.open", index=0, domain="example.com", page="/docs").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.retrieve.visited.report").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.retrieve.trail.return").result.ok)

            n1 = dispatcher.dispatch_command(ctx, "cmd.notes.quickCapture", text="First note")
            n2 = dispatcher.dispatch_command(ctx, "cmd.notes.quickCapture", text="Second note")
            self.assertTrue(n1.result.ok)
            self.assertTrue(n2.result.ok)
            note_a = n1.result.payload["noteId"]
            note_b = n2.result.payload["noteId"]
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.relate", noteA=note_a, noteB=note_b).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.attachment.add", noteId=note_a, path=str(base / "a.txt")).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.category.tree").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.related.graph", noteId=note_a).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.attachment.action", noteId=note_a, path=str(base / "a.txt"), action="copy").result.ok)
            notes_backup = base / "notes-backup.json"
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.backup.export", outPath=str(notes_backup)).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.backup.restore", inPath=str(notes_backup)).result.ok)

            f1 = base / "f1.txt"
            f1.write_text("one", encoding="utf-8")
            folder = base / "folder"
            folder.mkdir(parents=True, exist_ok=True)
            f2 = folder / "f2.txt"
            f2.write_text("two", encoding="utf-8")
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.file.browse", path=str(base)).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.file.copy", source=str(f1), destination=str(base / "f1-copy.txt"), confirm=True).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.file.move", source=str(base / "f1-copy.txt"), destination=str(base / "f1-moved.txt"), confirm=True).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.file.rename", path=str(base / "f1-moved.txt"), newName="f1-renamed.txt", confirm=True).result.ok)
            self.assertFalse(dispatcher.dispatch_command(ctx, "cmd.file.delete", path=str(base / "f1-renamed.txt"), confirm=False).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.file.delete", path=str(base / "f1-renamed.txt"), confirm=True).result.ok)
            archive = base / "files.zip"
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.file.zip.create", sources=[str(folder)], outPath=str(archive)).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.file.path.copy", path=str(f2)).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.file.tag.batch", paths=[str(f2)]).result.ok)

            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.context.capabilityEnvelope", commandId="cmd.selection.copy").result.ok)
            drift_safe = dispatcher.dispatch_command(ctx, "cmd.context.returnSourceDriftSafe")
            self.assertNotIn("Unknown command", drift_safe.result.message)

            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.create", name="inventory").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.field.define", name="name", fieldType="text", required=True).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.entry.add", values={"name": "local"}).result.ok)
            plan = dispatcher.dispatch_command(
                ctx,
                "cmd.jamal.sync.plan",
                incomingEntries=[{"entryId": "rec-00001", "values": {"name": "remote"}}],
                strategy="merge-values",
            )
            self.assertTrue(plan.result.ok)
            plan_id = plan.result.payload["planId"]
            self.assertFalse(dispatcher.dispatch_command(ctx, "cmd.jamal.sync.applyPlan", planId=plan_id, confirm=False).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.jamal.sync.applyPlan", planId=plan_id, confirm=True).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.jamal.sync.rollback", database="inventory").result.ok)


if __name__ == "__main__":
    unittest.main()

