import sys
import tempfile
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime import AppAdapter, AppContext, RuntimeDispatcher, SpellforgeRuntime, load_runtime_config


class AuthoringPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.config = load_runtime_config(self.repo_root)
        self.runtime = SpellforgeRuntime(adapters={"edge": AppAdapter("edge", supports_selection=True)})

    def _ctx(self, buffer: str, clipboard_text: str = "") -> AppContext:
        return AppContext(
            app_id="edge",
            window_id="win-edge",
            control_id="main-editor",
            buffer=buffer,
            caret=0,
            clipboard_text=clipboard_text or buffer,
        )

    def test_pipeline_polish_and_undo(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dispatcher = RuntimeDispatcher(
                self.runtime,
                self.config,
                profile_id="balanced",
                data_root=Path(tmpdir) / "data",
            )
            source = "first line\n\n[click here](https://example.com)"
            ctx = self._ctx(source)

            polished = dispatcher.dispatch_command(ctx, "cmd.author.pipeline.polish", text=source)
            self.assertTrue(polished.result.ok)
            self.assertEqual(polished.result.payload["stages"][0]["stage"], "transform")
            self.assertEqual(polished.result.payload["stages"][1]["stage"], "structure-check")
            self.assertEqual(polished.result.payload["stages"][2]["stage"], "style-pass")
            self.assertIn("# Draft", polished.result.payload["output"])
            self.assertIn("open the detailed guide", polished.result.payload["output"])

            undo = dispatcher.dispatch_command(
                ctx,
                "cmd.author.pipeline.undo",
                undoToken=polished.result.payload["undoToken"],
            )
            self.assertTrue(undo.result.ok)
            self.assertEqual(undo.result.payload["restored"], source)

    def test_template_hotkey_and_polish_hotkey(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dispatcher = RuntimeDispatcher(
                self.runtime,
                self.config,
                profile_id="balanced",
                data_root=Path(tmpdir) / "data",
            )
            ctx = self._ctx("draft line")

            template = dispatcher.dispatch_key_chord(ctx, "Control+Alt+Shift+N", press_count=1)
            self.assertTrue(template.result.ok)
            self.assertEqual(template.plan.command_id, "cmd.author.template.apply")
            self.assertIn("# Release Notes", template.result.payload["output"])
            self.assertTrue(template.result.payload["guided"])

            polished = dispatcher.dispatch_key_chord(ctx, "Control+Alt+Shift+A", press_count=1)
            self.assertTrue(polished.result.ok)
            self.assertEqual(polished.plan.command_id, "cmd.author.pipeline.polish")
            self.assertGreater(polished.result.payload["confidence"], 0.8)

    def test_html_fix_preview_and_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dispatcher = RuntimeDispatcher(
                self.runtime,
                self.config,
                profile_id="balanced",
                data_root=Path(tmpdir) / "data",
            )
            html = "<article><a href=\"https://example.com\">click here</a></article>"
            ctx = self._ctx("ignored")

            preview = dispatcher.dispatch_command(ctx, "cmd.author.html.fixPreview", html=html)
            self.assertTrue(preview.result.ok)
            self.assertTrue(preview.result.payload["nonDestructive"])
            self.assertGreaterEqual(preview.result.payload["count"], 1)
            self.assertIn("open the detailed guide", preview.result.payload["preview"])

            applied = dispatcher.dispatch_command(ctx, "cmd.author.html.fixApply", html=html)
            self.assertTrue(applied.result.ok)
            self.assertIn("undoToken", applied.result.payload)

            restored = dispatcher.dispatch_command(
                ctx,
                "cmd.author.pipeline.undo",
                undoToken=applied.result.payload["undoToken"],
            )
            self.assertTrue(restored.result.ok)
            self.assertEqual(restored.result.payload["restored"], html)

    def test_author_command_mission_telemetry_progression(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dispatcher = RuntimeDispatcher(
                self.runtime,
                self.config,
                profile_id="balanced",
                data_root=Path(tmpdir) / "data",
            )
            ctx = self._ctx("draft line")
            html = "<article><a>click here</a></article>"

            template = dispatcher.dispatch_command(
                ctx,
                "cmd.author.template.apply",
                template="release-notes",
                topic="Sprint",
            )
            self.assertTrue(template.result.ok)
            self.assertIn("missionTelemetry", template.result.payload)
            self.assertEqual(
                template.result.payload["missionTelemetry"]["missionId"],
                "author-template",
            )

            polish = dispatcher.dispatch_command(
                ctx,
                "cmd.author.pipeline.polish",
                text="line one\nclick here",
            )
            self.assertTrue(polish.result.ok)
            self.assertEqual(
                polish.result.payload["missionTelemetry"]["missionId"],
                "author-polish",
            )

            preview = dispatcher.dispatch_command(
                ctx,
                "cmd.author.html.fixPreview",
                html=html,
            )
            self.assertTrue(preview.result.ok)
            self.assertEqual(
                preview.result.payload["missionTelemetry"]["missionId"],
                "author-html-preview",
            )

            apply_out = dispatcher.dispatch_command(
                ctx,
                "cmd.author.html.fixApply",
                html=html,
            )
            self.assertTrue(apply_out.result.ok)
            self.assertEqual(
                apply_out.result.payload["missionTelemetry"]["missionId"],
                "author-html-apply",
            )

            undo = dispatcher.dispatch_command(
                ctx,
                "cmd.author.pipeline.undo",
                undoToken=apply_out.result.payload["undoToken"],
            )
            self.assertTrue(undo.result.ok)
            self.assertEqual(
                undo.result.payload["missionTelemetry"]["missionId"],
                "author-undo",
            )

            status = dispatcher.dispatch_command(
                ctx,
                "cmd.missions.status",
                profileId="balanced",
            )
            self.assertTrue(status.result.ok)
            completed = set(status.result.payload["completed"])
            self.assertTrue({
                "author-template",
                "author-polish",
                "author-html-preview",
                "author-html-apply",
                "author-undo",
            }.issubset(completed))

    def test_hotkey_discoverability_includes_author_mnemonics(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dispatcher = RuntimeDispatcher(
                self.runtime,
                self.config,
                profile_id="balanced",
                data_root=Path(tmpdir) / "data",
            )
            ctx = self._ctx("alpha")

            discover = dispatcher.dispatch_command(ctx, "cmd.help.availableHotkeys")
            self.assertTrue(discover.result.ok)
            hints = discover.result.payload.get("mnemonicHints", [])
            hint_commands = {row.get("commandId") for row in hints}
            self.assertIn("cmd.author.pipeline.polish", hint_commands)
            self.assertIn("cmd.author.template.apply", hint_commands)
            self.assertIn("cmd.author.pipeline.undo", hint_commands)


if __name__ == "__main__":
    unittest.main()
