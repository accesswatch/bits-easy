import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime import AppAdapter, AppContext, RuntimeDispatcher, BitsEasyRuntime, load_runtime_config


class ReleaseParityMatrixTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.config = load_runtime_config(self.repo_root)
        self.runtime = BitsEasyRuntime(
            adapters={
                "edge": AppAdapter("edge", supports_selection=True),
                "chrome": AppAdapter("chrome", supports_selection=True),
                "firefox": AppAdapter("firefox", supports_selection=True),
                "outlook": AppAdapter("outlook", supports_selection=False),
                "word": AppAdapter("word", supports_selection=True),
                "notepad": AppAdapter("notepad", supports_selection=True),
                "vscode": AppAdapter("vscode", supports_selection=True),
            }
        )

    @staticmethod
    def _ctx(app: str, text: str = "release parity sample text") -> AppContext:
        return AppContext(
            app_id=app,
            window_id=f"win-{app}",
            control_id="main-editor",
            buffer=text,
            caret=min(5, len(text)),
            clipboard_text=text,
        )

    def _selection_parity_state(self, dispatcher: RuntimeDispatcher, app: str) -> str:
        ctx = self._ctx(app)
        self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.selection.markStart").result.ok)
        ctx.caret = min(len(ctx.buffer), ctx.caret + 7)
        mark_end = dispatcher.dispatch_command(ctx, "cmd.selection.markEnd").result
        self.assertTrue(mark_end.ok)

        payload = mark_end.payload or {}
        if bool(payload.get("fallbackUsed", False)):
            return "fallback-only"
        if float(payload.get("confidence", 0.0)) >= 0.9:
            return "native-range"
        return "normalized-partial"

    def test_cross_app_release_parity_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced", data_root=base / "data")

            for app in ("edge", "chrome", "firefox", "outlook", "word", "notepad", "vscode"):
                ctx = self._ctx(app)

                self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.selection.markStart").result.ok)
                mark_end = dispatcher.dispatch_command(ctx, "cmd.selection.markEnd")
                self.assertNotIn("Unknown command", mark_end.result.message)
                self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.selection.readContext").result.ok)
                self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.selection.cancel").result.ok)
                self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.context.capabilityEnvelope", commandId="cmd.selection.markEnd").result.ok)

                self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.clip.copyToSlot", slot=1).result.ok)
                self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.clip.browser.open").result.ok)
                self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.clip.browser.search", query="release").result.ok)
                self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.clip.browser.compare", slotA=1, slotB=1).result.ok)
                self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.clip.library.ingestSlot", slot=1).result.ok)
                self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.clip.library.timeline", limit=5).result.ok)

            ctx = self._ctx("edge")
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.template.apply", template="tasks", database="release-db").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.entry.add", values={"title": "ship", "status": "todo"}).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.dashboard").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.search.advanced", query="ship", filters={"status": "todo"}).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.jamal.sync.plan", incomingEntries=[], strategy="prefer-incoming").result.ok)

            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.quickCapture", text="release note").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.notes.category.tree").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.retrieve.query", query="release hardening").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.retrieve.visited.report").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.journal.trends", windowDays=30).result.ok)

    def test_selection_surface_parity_matrix_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced", data_root=base / "data")

            expected = {
                "edge": "native-range",
                "chrome": "native-range",
                "firefox": "native-range",
                "word": "native-range",
                "notepad": "native-range",
                "vscode": "native-range",
                "outlook": "fallback-only",
            }

            observed = {app: self._selection_parity_state(dispatcher, app) for app in expected}
            self.assertEqual(observed, expected)

    def test_selection_surface_parity_acceptance_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced", data_root=base / "data")

            apps = ["edge", "chrome", "firefox", "word", "notepad", "vscode", "outlook"]
            states = [self._selection_parity_state(dispatcher, app) for app in apps]

            native = states.count("native-range")
            normalized = states.count("normalized-partial")
            fallback = states.count("fallback-only")

            native_or_normalized = native + normalized
            self.assertGreaterEqual(native_or_normalized, 6)
            self.assertLessEqual(fallback, 1)


if __name__ == "__main__":
    unittest.main()

