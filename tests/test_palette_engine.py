import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime import PaletteEngine, load_runtime_config


class PaletteEngineTests(unittest.TestCase):
    def test_search_ranking_and_history_bias(self):
        repo_root = Path(__file__).resolve().parents[1]
        cfg = load_runtime_config(repo_root)

        with tempfile.TemporaryDirectory() as tmpdir:
            engine = PaletteEngine(cfg, Path(tmpdir) / "history.json")

            rows = engine.search("selection", app_id="word", limit=5)
            self.assertTrue(rows)
            top_before = rows[0].command_id

            engine.record_execution("cmd.clip.copyToSlot", tick=999999999)
            engine.record_execution("cmd.clip.copyToSlot", tick=1000000000)
            rows_after = engine.search("clip", app_id="outlook", limit=5)
            self.assertTrue(any(r.command_id == "cmd.clip.copyToSlot" for r in rows_after))
            ranked_ids = [r.command_id for r in rows_after]
            self.assertLessEqual(ranked_ids.index("cmd.clip.copyToSlot"), 1)

            self.assertTrue(any(r.command_id == top_before for r in rows))

    def test_ai_commands_are_gated_by_key_and_selection_activity(self):
        repo_root = Path(__file__).resolve().parents[1]
        cfg = load_runtime_config(repo_root)

        with tempfile.TemporaryDirectory() as tmpdir:
            engine = PaletteEngine(cfg, Path(tmpdir) / "history.json")

            # Without any AI key configured, only key setup should remain visible.
            rows_no_key = engine.search(
                "ai",
                app_id="word",
                limit=100,
                ai_key_enabled=False,
                has_selection_activity=False,
            )
            ids_no_key = {r.command_id for r in rows_no_key}
            self.assertIn("cmd.ai.key.set", ids_no_key)
            self.assertIn("cmd.ai.key.status", ids_no_key)
            self.assertIn("cmd.ai.key.storeStatus", ids_no_key)
            self.assertNotIn("cmd.ai.tool.run", ids_no_key)

            # With AI key but no selection activity and empty query, selection-driven AI tools stay hidden.
            rows_key_no_sel = engine.search(
                "",
                app_id="word",
                limit=200,
                ai_key_enabled=True,
                has_selection_activity=False,
            )
            ids_key_no_sel = {r.command_id for r in rows_key_no_sel}
            self.assertIn("cmd.ai.session.new", ids_key_no_sel)
            self.assertNotIn("cmd.ai.tool.run", ids_key_no_sel)

            # With selection activity, selection-driven AI tools are visible.
            rows_key_sel = engine.search(
                "",
                app_id="word",
                limit=200,
                ai_key_enabled=True,
                has_selection_activity=True,
            )
            ids_key_sel = {r.command_id for r in rows_key_sel}
            self.assertIn("cmd.ai.tool.run", ids_key_sel)


if __name__ == "__main__":
    unittest.main()
