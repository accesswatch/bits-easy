import sys
import tempfile
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime import (  # noqa: E402
    AppAdapter,
    AppContext,
    BitsEasyRuntime,
    RuntimeDispatcher,
    load_runtime_config,
)
from bits_easy_runtime.text_expansion import TextExpansionStore  # noqa: E402


class EasyTextStudioTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.config = load_runtime_config(self.repo_root)
        self.runtime = BitsEasyRuntime(
            adapters={"edge": AppAdapter("edge", supports_selection=True)}
        )
        self.dispatcher = RuntimeDispatcher(
            self.runtime,
            self.config,
            profile_id="balanced",
        )
        self.ctx = AppContext(
            app_id="edge",
            window_id="win-edge",
            control_id="main-editor",
            buffer="",
            caret=0,
            clipboard_text="",
        )

    def _fresh_store(self, tmp_dir: str) -> None:
        self.dispatcher._expansions = TextExpansionStore(
            Path(tmp_dir) / "easytext-studio.json"
        )

    def test_folder_tree_create_move_delete_reassign(self):
        with tempfile.TemporaryDirectory() as td:
            self._fresh_store(td)

            create_folder = self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.expansion.createFolder",
                folderName="Email",
            )
            self.assertTrue(create_folder.result.ok)
            folder_id = create_folder.result.payload["folderId"]

            upsert = self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.expansion.upsert",
                abbreviation="sig",
                title="Signature",
                content="Regards, Team",
                trigger="sig",
                folderId=folder_id,
            )
            self.assertTrue(upsert.result.ok)

            tree = self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.expansion.tree",
            )
            self.assertTrue(tree.result.ok)
            self.assertIn(folder_id, tree.result.payload["folders"])

            delete_folder = self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.expansion.deleteFolder",
                folderId=folder_id,
            )
            self.assertTrue(delete_folder.result.ok)

            listed = self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.expansion.list",
            )
            self.assertTrue(listed.result.ok)
            item = listed.result.payload["items"][0]
            self.assertEqual(item["folderId"], "root")

    def test_trigger_resolution_case_insensitive_and_insert_payload(self):
        with tempfile.TemporaryDirectory() as td:
            self._fresh_store(td)

            self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.expansion.upsert",
                abbreviation="sig",
                title="Signature",
                content="Yours sincerely\nName",
                trigger="sig",
            )

            resolve_upper = self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.expansion.resolveTrigger",
                trigger="SIG",
            )
            self.assertTrue(resolve_upper.result.ok)
            payload = resolve_upper.result.payload
            self.assertEqual(payload["abbreviation"], "sig")
            self.assertEqual(payload["insertText"], "Yours sincerely\nName")
            self.assertEqual(payload["insertTextSuffix"], " ")
            self.assertTrue(payload["insertViaClipboard"])

            resolve_missing = self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.expansion.resolveTrigger",
                trigger="notfound",
            )
            self.assertFalse(resolve_missing.result.ok)

    def test_hotkey_hint_primary_quick_insert_and_persistence(self):
        with tempfile.TemporaryDirectory() as td:
            self._fresh_store(td)

            self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.expansion.upsert",
                abbreviation="addr",
                title="Address",
                content="123 Main Street",
                trigger="addr",
                hotkeyHint="Alt+Win+F6",
            )

            set_hint = self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.expansion.setHotkeyHint",
                abbreviation="addr",
                hotkeyHint="Alt+Win+F7",
            )
            self.assertTrue(set_hint.result.ok)

            set_primary = self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.expansion.setPrimary",
                abbreviation="addr",
            )
            self.assertTrue(set_primary.result.ok)

            quick = self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.quickInsert",
            )
            self.assertTrue(quick.result.ok)
            self.assertEqual(
                quick.result.payload["content"],
                "123 Main Street",
            )

            # Reload from disk to verify persisted metadata.
            store_path = Path(td) / "easytext-studio.json"
            reloaded = TextExpansionStore(store_path)
            list_out = reloaded.list_entries()
            self.assertTrue(list_out.ok)
            self.assertEqual(len(list_out.payload["items"]), 1)
            item = list_out.payload["items"][0]
            self.assertEqual(item["trigger"], "addr")
            self.assertEqual(item["hotkeyHint"], "Alt+Win+F7")

    def test_dispatcher_supports_full_easytext_command_surface(self):
        with tempfile.TemporaryDirectory() as td:
            self._fresh_store(td)

            create_folder = self.dispatcher.dispatch_command(
                self.ctx,
                "cmd.text.expansion.createFolder",
                folderName="Work",
            )
            self.assertTrue(create_folder.result.ok)
            folder_id = create_folder.result.payload["folderId"]

            self.assertTrue(
                self.dispatcher.dispatch_command(
                    self.ctx,
                    "cmd.text.expansion.upsert",
                    abbreviation="todo",
                    title="Task Prefix",
                    content="TODO: ",
                    trigger="todo",
                ).result.ok
            )

            self.assertTrue(
                self.dispatcher.dispatch_command(
                    self.ctx,
                    "cmd.text.expansion.moveToFolder",
                    abbreviation="todo",
                    folderId=folder_id,
                ).result.ok
            )

            self.assertTrue(
                self.dispatcher.dispatch_command(
                    self.ctx,
                    "cmd.text.expansion.renameFolder",
                    folderId=folder_id,
                    folderName="Workflows",
                ).result.ok
            )

            self.assertTrue(
                self.dispatcher.dispatch_command(
                    self.ctx,
                    "cmd.text.expansion.rename",
                    abbreviation="todo",
                    title="Task Marker",
                ).result.ok
            )

            self.assertTrue(
                self.dispatcher.dispatch_command(
                    self.ctx,
                    "cmd.text.expansion.expand",
                    abbreviation="todo",
                ).result.ok
            )

            self.assertTrue(
                self.dispatcher.dispatch_command(
                    self.ctx,
                    "cmd.text.expansion.list",
                ).result.ok
            )

            self.assertTrue(
                self.dispatcher.dispatch_command(
                    self.ctx,
                    "cmd.text.expansion.tree",
                ).result.ok
            )

            self.assertTrue(
                self.dispatcher.dispatch_command(
                    self.ctx,
                    "cmd.text.expansion.delete",
                    abbreviation="todo",
                ).result.ok
            )


if __name__ == "__main__":
    unittest.main()
