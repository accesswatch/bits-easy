import json
from pathlib import Path
import tempfile
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime import (
    AppAdapter,
    AppContext,
    CommandOrchestrator,
    RuntimeDispatcher,
    BitsEasyRuntime,
    load_runtime_config,
)


class OrchestratorTests(unittest.TestCase):
    def test_journal_and_intent_memory(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        config = load_runtime_config(repo_root)

        with tempfile.TemporaryDirectory() as tmpdir:
            runtime = BitsEasyRuntime(adapters={"edge": AppAdapter("edge", supports_selection=True)})
            dispatcher = RuntimeDispatcher(runtime=runtime, config=config, profile_id="balanced")
            journal = Path(tmpdir) / "journal.jsonl"
            orchestrator = CommandOrchestrator(dispatcher=dispatcher, journal_path=journal)

            ctx = AppContext(
                app_id="edge",
                window_id="win-edge",
                control_id="main-editor",
                buffer="alpha bravo charlie",
                caret=6,
                clipboard_text="",
            )

            out = orchestrator.execute(ctx, "cmd.selection.markStart", intent="selection workflow")
            self.assertTrue(out.result.ok)
            self.assertIn("cmd.selection.markStart", orchestrator.recent_commands)

            suggestions = orchestrator.suggestions_for_app("edge")
            self.assertIn("cmd.selection.markEnd", suggestions)

            explained = orchestrator.suggestion_details_for_app("edge")
            self.assertGreaterEqual(len(explained), 1)
            self.assertIn("score", explained[0])

            reset = orchestrator.reset_app_memory("edge")
            self.assertTrue(reset)
            self.assertIn("cmd.help.availableHotkeys", orchestrator.suggestions_for_app("edge"))

            lines = journal.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            row = json.loads(lines[0])
            self.assertEqual(row["commandId"], "cmd.selection.markStart")
            self.assertTrue(row["ok"])

    def test_per_app_ranking_persists(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        config = load_runtime_config(repo_root)

        with tempfile.TemporaryDirectory() as tmpdir:
            runtime = BitsEasyRuntime(adapters={"edge": AppAdapter("edge", supports_selection=True)})
            dispatcher = RuntimeDispatcher(runtime=runtime, config=config, profile_id="balanced")
            journal = Path(tmpdir) / "journal.jsonl"
            memory = Path(tmpdir) / "intent-memory.json"

            orchestrator = CommandOrchestrator(dispatcher=dispatcher, journal_path=journal, intent_store_path=memory)
            ctx = AppContext(
                app_id="edge",
                window_id="win-edge",
                control_id="main-editor",
                buffer="alpha bravo",
                caret=3,
                clipboard_text="",
            )

            orchestrator.execute(ctx, "cmd.capture.quickInbox", intent="clip and copy workflow")
            orchestrator.execute(ctx, "cmd.capture.quickInbox", intent="clip and copy workflow")

            reloaded = CommandOrchestrator(dispatcher=dispatcher, journal_path=journal, intent_store_path=memory)
            top = reloaded.suggestion_details_for_app("edge")[0]
            self.assertEqual(top["commandId"], "cmd.capture.quickInbox")


if __name__ == "__main__":
    unittest.main()

