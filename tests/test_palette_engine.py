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
            self.assertEqual(rows_after[0].command_id, "cmd.clip.copyToSlot")

            self.assertTrue(any(r.command_id == top_before for r in rows))


if __name__ == "__main__":
    unittest.main()
