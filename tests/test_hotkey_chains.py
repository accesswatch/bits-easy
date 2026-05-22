import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime import AppAdapter, AppContext, RuntimeDispatcher, SpellforgeRuntime, load_runtime_config


class HotkeyChainTests(unittest.TestCase):
    def test_create_list_and_run_chain(self):
        repo_root = Path(__file__).resolve().parents[1]
        config = load_runtime_config(repo_root)
        runtime = SpellforgeRuntime(adapters={"edge": AppAdapter("edge", supports_selection=True)})
        dispatcher = RuntimeDispatcher(runtime, config, profile_id="balanced")
        ctx = AppContext("edge", "w1", "editor", "alpha", 0, "")

        created = dispatcher.dispatch_command(
            ctx,
            "cmd.profile.hotkeyChainCreate",
            name="quick-help",
            commandIds=["cmd.palette.open", "cmd.help.availableHotkeys"],
        )
        self.assertTrue(created.result.ok)

        listed = dispatcher.dispatch_command(ctx, "cmd.profile.hotkeyChainList")
        self.assertTrue(listed.result.ok)
        self.assertGreaterEqual(listed.result.payload["count"], 1)

        ran = dispatcher.dispatch_command(ctx, "cmd.profile.hotkeyChainRun", name="quick-help")
        self.assertTrue(ran.result.ok)
        self.assertEqual(len(ran.result.payload["steps"]), 2)


if __name__ == "__main__":
    unittest.main()
