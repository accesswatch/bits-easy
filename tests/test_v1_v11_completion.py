import sys
import tempfile
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime import AppAdapter, AppContext, RuntimeDispatcher, BitsEasyRuntime, load_runtime_config
from bits_easy_runtime.text_expansion import TextExpansionStore


class V1V11CompletionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.config = load_runtime_config(self.repo_root)
        self.runtime = BitsEasyRuntime(adapters={"edge": AppAdapter("edge", supports_selection=True)})
        self.dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        self.ctx = AppContext(
            app_id="edge",
            window_id="win-edge",
            control_id="main-editor",
            buffer="alpha bravo charlie",
            caret=0,
            clipboard_text="",
        )

    def test_text_expansion_lifecycle_and_quick_insert(self):
        with tempfile.TemporaryDirectory() as td:
            self.dispatcher._expansions = TextExpansionStore(Path(td) / "expansions.json")

            created = self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.expansion.upsert",
                abbreviation="sig",
                content="Regards, Team",
            )
            self.assertTrue(created.result.ok)

            conflict = self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.expansion.upsert",
                abbreviation="sig",
                content="Different",
            )
            self.assertFalse(conflict.result.ok)

            set_primary = self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.expansion.setPrimary",
                abbreviation="sig",
            )
            self.assertTrue(set_primary.result.ok)

            quick = self.dispatcher.dispatch_command(self.ctx, "cmd.text.quickInsert")
            self.assertTrue(quick.result.ok)
            self.assertEqual(quick.result.payload["content"], "Regards, Team")

            listed = self.dispatcher.dispatch_command(self.ctx, "cmd.text.expansion.list")
            self.assertTrue(listed.result.ok)
            self.assertEqual(len(listed.result.payload["items"]), 1)

            renamed = self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.expansion.rename",
                abbreviation="sig",
                title="Signature",
            )
            self.assertTrue(renamed.result.ok)

            deleted = self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.expansion.delete",
                abbreviation="sig",
            )
            self.assertTrue(deleted.result.ok)

    def test_merge_advanced_controls(self):
        divider = self.dispatcher.dispatch_command(self.ctx, "cmd.merge.setDivider", divider="line")
        self.assertTrue(divider.result.ok)

        custom = self.dispatcher.dispatch_command(self.ctx, "cmd.merge.setCustomSeparator", separator=" | ")
        self.assertTrue(custom.result.ok)

        profile = self.dispatcher.dispatch_command(self.ctx, "cmd.merge.applyProfile", profile="research")
        self.assertTrue(profile.result.ok)

        self.runtime.merge_capture("one")
        self.runtime.merge_capture("two")
        commit = self.dispatcher.dispatch_command(self.ctx, "cmd.merge.commit")
        self.assertTrue(commit.result.ok)
        self.assertIn("one", commit.result.payload["content"])

        toggle = self.dispatcher.dispatch_command(self.ctx, "cmd.merge.toggleClearOnPaste")
        self.assertTrue(toggle.result.ok)

    def test_manual_slot_workflows(self):
        self.runtime.copy_to_slot(self.ctx, 1, text="a\nb\nc")
        self.runtime.copy_to_slot(self.ctx, 2, text="target")

        split = self.dispatcher.dispatch_command(self.ctx, "cmd.clip.browser.split", slot=1, separator="\n")
        self.assertTrue(split.result.ok)

        merge = self.dispatcher.dispatch_command(self.ctx, "cmd.clip.browser.merge", slotA=1, slotB=2, separator=" ")
        self.assertTrue(merge.result.ok)

        reorder = self.dispatcher.dispatch_command(self.ctx, "cmd.clip.browser.reorder", fromSlot=1, toSlot=3, overwrite=True)
        self.assertTrue(reorder.result.ok)


if __name__ == "__main__":
    unittest.main()

