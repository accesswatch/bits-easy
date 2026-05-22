import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime import AppAdapter, AppContext, RuntimeDispatcher, SpellforgeRuntime, load_runtime_config


class AiAssistantPlatformTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.config = load_runtime_config(self.repo_root)
        self.runtime = SpellforgeRuntime(adapters={"edge": AppAdapter("edge", supports_selection=True)})

    def _ctx(self, app: str = "edge", buffer: str = "alpha") -> AppContext:
        return AppContext(
            app_id=app,
            window_id=f"win-{app}",
            control_id="main-editor",
            buffer=buffer,
            caret=0,
            clipboard_text=buffer,
        )

    def test_ai_platform_and_hardening_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced", data_root=base / "data")
            ctx = self._ctx()

            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.ai.key.set", provider="openai", key="k-123").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.ai.billingStatus", provider="openai").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.ai.session.new", title="Release prep").result.ok)
            sessions = dispatcher.dispatch_command(ctx, "cmd.ai.session.list")
            self.assertTrue(sessions.result.ok)
            self.assertGreaterEqual(sessions.result.payload["count"], 1)
            sid = sessions.result.payload["items"][0]["sessionId"]
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.ai.session.load", sessionId=sid).result.ok)

            self.assertTrue(
                dispatcher.dispatch_command(
                    ctx,
                    "cmd.ai.tool.run",
                    tool="summarize",
                    text="This is long. Keep first sentence only.",
                    replace=True,
                ).result.ok
            )

            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.ai.prompt.create", name="release-note", text="Summarize changes").result.ok)
            listed = dispatcher.dispatch_command(ctx, "cmd.ai.prompt.list", query="release")
            self.assertTrue(listed.result.ok)
            self.assertEqual(listed.result.payload["count"], 1)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.ai.prompt.insert", name="release-note").result.ok)

            doc_path = base / "doc.txt"
            doc_path.write_text("The branch is hardened for release readiness.", encoding="utf-8")
            uploaded = dispatcher.dispatch_command(ctx, "cmd.ai.doc.upload", path=str(doc_path), title="release-doc")
            self.assertTrue(uploaded.result.ok)
            doc_id = uploaded.result.payload["documentId"]
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.ai.doc.ask", documentId=doc_id, question="What changed?").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.ai.doc.followUp", documentId=doc_id, question="Anything else?").result.ok)

            img = base / "generated-image.txt"
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.ai.image.generate", prompt="release banner", outPath=str(img)).result.ok)
            self.assertTrue(img.exists())

            audio = base / "audio.txt"
            audio.write_text("spoken notes", encoding="utf-8")
            self.assertTrue(
                dispatcher.dispatch_command(
                    ctx,
                    "cmd.ai.transcribe",
                    inPath=str(audio),
                    speakerSeparation=True,
                    translateTo="es",
                ).result.ok
            )

            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.ai.session.save", sessionId=sid).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.ai.session.clear").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.ai.session.delete", sessionId=sid).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.ai.key.delete", provider="openai").result.ok)

            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.capture.quickInbox").result.ok)
            trends = dispatcher.dispatch_command(ctx, "cmd.journal.trends", windowDays=30)
            self.assertTrue(trends.result.ok)
            self.assertIn("topCommands", trends.result.payload)

            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.clip.copyToSlot", slot=1).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.clip.library.ingestSlot", slot=1).result.ok)
            timeline = dispatcher.dispatch_command(ctx, "cmd.clip.library.timeline", limit=20)
            self.assertTrue(timeline.result.ok)
            self.assertIn("discoverability", timeline.result.payload)


if __name__ == "__main__":
    unittest.main()
