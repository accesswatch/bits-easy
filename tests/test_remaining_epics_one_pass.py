import json
import sys
import tempfile
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime import AppAdapter, AppContext, RuntimeDispatcher, BitsEasyRuntime, load_runtime_config


class RemainingEpicsOnePassTests(unittest.TestCase):
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

    def test_one_pass_remaining_epics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced", data_root=base / "data")
            ctx = self._ctx("edge", "quick content")

            # E04 Notes / ThoughtDock
            n1 = dispatcher.dispatch_command(ctx, "cmd.notes.quickCapture", text="First note")
            n2 = dispatcher.dispatch_command(ctx, "cmd.notes.quickCapture", text="Second note")
            self.assertTrue(n1.result.ok)
            self.assertTrue(n2.result.ok)
            note_a = n1.result.payload["noteId"]
            note_b = n2.result.payload["noteId"]
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.mode.set", mode="advanced").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.category.create", category="projects").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.category.move", category="projects", parent="root").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.relate", noteA=note_a, noteB=note_b).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.attachment.add", noteId=note_a, path="C:/tmp/a.txt").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.field.set", noteId=note_a, key="owner", value="qa").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.help.set", text="global help text").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.help.resolve").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.snapshot.create", reason="before restore").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.snapshot.restore").result.ok)

            # E03 Writing / Export
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.author.markdown.insert", kind="table", text="").result.ok)
            html = dispatcher.dispatch_command(ctx, "cmd.author.html.semantic", title="Doc", items=["one", "two"])
            self.assertTrue(html.result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.author.html.validate", html=html.result.payload["html"]).result.ok)
            out_html = base / "author.html"
            out_docx = base / "author.docx"
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.author.export.html", markdown="# Title\n- item", outPath=str(out_html)).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.author.export.word", markdown="# Title\n- item", outPath=str(out_docx)).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.author.a11y.lint", markdown="[click here](https://x)").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.author.a11y.fixPreview", markdown="click here").result.ok)
            polished = dispatcher.dispatch_command(ctx, "cmd.author.pipeline.polish", text="line one\nclick here")
            self.assertTrue(polished.result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.author.pipeline.undo", undoToken=polished.result.payload["undoToken"]).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.author.template.apply", template="release-notes", topic="Sprint 12").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.author.html.fixPreview", html="<article><a>click here</a></article>").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.author.html.fixApply", html="<article><a>click here</a></article>").result.ok)

            # E09 Retrieval
            routed = dispatcher.dispatch_command(ctx, "cmd.retrieve.query", query="release notes", providerOrder=["local", "broken", "web"])
            self.assertTrue(routed.result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.retrieve.revisit", index=0).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.retrieve.parse", raw='{"a":1}').result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.retrieve.summarize", results=routed.result.payload["results"]).result.ok)

            # E11 Backup / Migration
            backup_target = base / "backups"
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.backup.target.set", path=str(backup_target.resolve())).result.ok)
            src_dir = base / "sourceA"
            src_dir.mkdir(parents=True, exist_ok=True)
            src_file = src_dir / "f.txt"
            src_file.write_text("x", encoding="utf-8")
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.backup.source.add", path=str(src_dir.resolve())).result.ok)
            settings_file = base / "settings.json"
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.backup.settings.create", files={"profile": "balanced"}, outPath=str(settings_file)).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.backup.settings.restore", inPath=str(settings_file)).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.backup.selected.run", selectedPaths=[str(src_file)], outDir=str(base / "sel")).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.backup.migrate", fromDir=str(src_dir), toDir=str(base / "mig"), dryRun=True).result.ok)

            # E16 Joplin Interop
            joplin_in = base / "joplin-in.json"
            joplin_in.write_text(json.dumps({"notes": [{"title": "A", "body": "# hi", "tags": ["t"]}]}), encoding="utf-8")
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.joplin.import", inPath=str(joplin_in)).result.ok)
            joplin_out = base / "joplin-out.json"
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.joplin.export", notes=[{"title": "B", "body": "body"}], outPath=str(joplin_out)).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.joplin.mapping.set", tagMap={"a": "b"}, attachmentMap={"x": "y", "z": "y"}).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.joplin.refresh", incomingNotes=[{"id": "1", "conflict": True}], apply=False).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.joplin.refresh", incomingNotes=[{"id": "1"}], apply=True).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.joplin.refresh.rollback").result.ok)

            # E19 NVDA readiness
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.nvda.readiness.baseline").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.nvda.readiness.api").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.nvda.readiness.security").result.ok)

            # Remaining E13
            self.assertFalse(dispatcher.dispatch_command(ctx, "cmd.utility.notifications.import", rules={"a": 1}, confirm=False).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.utility.notifications.import", rules={"a": 1}, confirm=True).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.utility.notifications.restore").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.utility.audio.split", speechPan=-80, appPan=80).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.utility.audio.restoreBalance").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.utility.audio.cycleCard").result.ok)

            # Remaining E18
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.context.whereAmI").result.ok)
            start = dispatcher.dispatch_command(ctx, "cmd.missions.start", profileId="balanced")
            self.assertTrue(start.result.ok)
            mission_id = start.result.payload["next"]
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.missions.complete", profileId="balanced", missionId=mission_id).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.missions.status", profileId="balanced").result.ok)
            pack = base / "workflow-pack.json"
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.workflow.pack.export", pack={"settings": {}, "chains": [], "templates": []}, outPath=str(pack)).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.workflow.pack.import", inPath=str(pack), rejectOnConflict=True).result.ok)


if __name__ == "__main__":
    unittest.main()

