import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime import AppAdapter, AppContext, DriftAwareAdapter, RuntimeErrorCode, SpellforgeRuntime


class SelectionClipboardE2E(unittest.TestCase):
    def setUp(self) -> None:
        self.runtime = SpellforgeRuntime(
            adapters={
                "edge": AppAdapter("edge", supports_selection=True),
                "chrome": AppAdapter("chrome", supports_selection=True),
                "firefox": AppAdapter("firefox", supports_selection=True),
                "notepad": AppAdapter("notepad", supports_selection=True),
                "vscode": AppAdapter("vscode", supports_selection=True),
                "word": DriftAwareAdapter("word", supports_selection=True, drift_delta=2),
                "outlook": AppAdapter("outlook", supports_selection=False),
            }
        )

    def _ctx(self, app_id: str, buffer: str, caret: int, clipboard_text: str = "") -> AppContext:
        return AppContext(
            app_id=app_id,
            window_id=f"win-{app_id}",
            control_id="main-editor",
            buffer=buffer,
            caret=caret,
            clipboard_text=clipboard_text,
        )

    def test_selection_lifecycle_supported_apps(self) -> None:
        apps = ["edge", "chrome", "firefox", "notepad", "vscode"]
        for app_id in apps:
            with self.subTest(app_id=app_id):
                ctx = self._ctx(app_id, "alpha bravo charlie delta", 6)
                start = self.runtime.mark_selection_start(ctx)
                self.assertTrue(start.ok)
                self.assertIn("guidedFlow", start.payload)
                self.assertEqual(start.payload["guidedFlow"]["stage"], "start-set")
                marker_state_start = self.runtime.describe_selection_markers(ctx)
                self.assertTrue(marker_state_start.ok)
                self.assertTrue(marker_state_start.payload["startMarkerSet"])
                self.assertFalse(marker_state_start.payload["endMarkerSet"])
                self.assertEqual(marker_state_start.payload["startMeta"]["appId"], app_id)

                ctx.caret = 18
                end = self.runtime.mark_selection_end(ctx)
                self.assertTrue(end.ok)
                self.assertEqual(end.payload["length"], 12)
                self.assertIn("startSnippet", end.payload)
                self.assertIn("endSnippet", end.payload)
                self.assertIn("startMeta", end.payload)
                self.assertIn("endMeta", end.payload)
                self.assertEqual(end.payload["guidedFlow"]["stage"], "range-captured")

                read = self.runtime.read_selection_context(ctx)
                self.assertTrue(read.ok)
                self.assertIn("bravo", read.payload["startSnippet"])
                self.assertEqual(read.payload["guidedFlow"]["stage"], "status")

                marker_state_ready = self.runtime.describe_selection_markers(ctx)
                self.assertTrue(marker_state_ready.ok)
                self.assertEqual(marker_state_ready.payload["activeRangeStart"], 6)
                self.assertEqual(marker_state_ready.payload["activeRangeEnd"], 18)
                self.assertIn("telemetry", marker_state_ready.payload)
                self.assertGreaterEqual(marker_state_ready.payload["telemetry"]["app"].get("markEndCaptured", 0), 1)

                ctx.caret = 1
                jump = self.runtime.jump_selection_start(ctx)
                self.assertTrue(jump.ok)
                self.assertEqual(ctx.caret, 6)
                self.assertIn("guidedFlow", jump.payload)

                cancel = self.runtime.cancel_selection(ctx)
                self.assertTrue(cancel.ok)
                self.assertEqual(cancel.payload["guidedFlow"]["stage"], "cancelled")

    def test_clip_slot_lifecycle(self) -> None:
        ctx = self._ctx("edge", "first second third", 0, clipboard_text="clipboard")

        copy = self.runtime.copy_to_slot(ctx, slot=1, text="team notes")
        self.assertTrue(copy.ok)

        desc = self.runtime.describe_slot(1)
        self.assertTrue(desc.ok)
        self.assertFalse(desc.payload["empty"])
        self.assertEqual(desc.payload["sourceApp"], "edge")

        protect = self.runtime.protect_slot(1)
        self.assertTrue(protect.ok)

        blocked = self.runtime.copy_to_slot(ctx, slot=1, text="overwrite")
        self.assertFalse(blocked.ok)
        self.assertEqual(blocked.code, RuntimeErrorCode.PROTECTED_SLOT)

        unprotect = self.runtime.unprotect_slot(1)
        self.assertTrue(unprotect.ok)

        edit = self.runtime.edit_slot(1, "edited notes")
        self.assertTrue(edit.ok)

        paste = self.runtime.paste_from_slot(1)
        self.assertTrue(paste.ok)
        self.assertEqual(paste.payload["content"], "edited notes")

        delete = self.runtime.delete_slot(1)
        self.assertTrue(delete.ok)

        empty = self.runtime.paste_from_slot(1)
        self.assertFalse(empty.ok)
        self.assertEqual(empty.code, RuntimeErrorCode.EMPTY_SLOT)

    def test_merge_engine_determinism(self) -> None:
        self.runtime.set_merge_mode_append()
        self.runtime.set_merge_divider_line()

        r1 = self.runtime.merge_capture("item 1", source_tag="edge")
        r2 = self.runtime.merge_capture("item 2", source_tag="word")
        self.assertTrue(r1.ok)
        self.assertTrue(r2.ok)

        commit_a = self.runtime.merge_commit()
        self.assertTrue(commit_a.ok)

        # Re-run with same inputs in replace-reset path and compare output determinism.
        self.runtime = self.setUp_runtime()
        self.runtime.set_merge_mode_append()
        self.runtime.set_merge_divider_line()
        self.runtime.merge_capture("item 1", source_tag="edge")
        self.runtime.merge_capture("item 2", source_tag="word")
        commit_b = self.runtime.merge_commit()

        self.assertEqual(commit_a.payload["content"], commit_b.payload["content"])

    def setUp_runtime(self) -> SpellforgeRuntime:
        return SpellforgeRuntime(
            adapters={
                "edge": AppAdapter("edge", supports_selection=True),
                "chrome": AppAdapter("chrome", supports_selection=True),
                "firefox": AppAdapter("firefox", supports_selection=True),
                "notepad": AppAdapter("notepad", supports_selection=True),
                "vscode": AppAdapter("vscode", supports_selection=True),
                "word": DriftAwareAdapter("word", supports_selection=True, drift_delta=2),
                "outlook": AppAdapter("outlook", supports_selection=False),
            }
        )

    def test_anchor_restore_and_drift_handling(self) -> None:
        word_ctx = self._ctx("word", "document body content", 5)
        save = self.runtime.save_source_anchor(word_ctx)
        self.assertTrue(save.ok)

        # Move caret and restore via drift-aware adapter.
        word_ctx.caret = 15
        restore = self.runtime.restore_source_anchor(word_ctx)
        self.assertTrue(restore.ok)
        self.assertTrue(restore.payload["driftDetected"])
        self.assertIn("Retry exact restore", restore.next_steps[0])

    def test_outlook_unsupported_selection_fallback(self) -> None:
        ctx = self._ctx("outlook", "", 0, clipboard_text="email snippet from clipboard")

        start = self.runtime.mark_selection_start(ctx)
        self.assertTrue(start.ok)

        ctx.caret = 4
        end = self.runtime.mark_selection_end(ctx)
        self.assertTrue(end.ok)
        self.assertEqual(end.code, RuntimeErrorCode.UNSUPPORTED_SURFACE)
        self.assertTrue(end.payload["fallbackUsed"])

        read = self.runtime.read_selection_context(ctx)
        self.assertTrue(read.ok)
        self.assertGreater(read.payload["confidence"], 0.5)

    def test_unsupported_selection_uses_buffer_range_fallback_before_clipboard(self) -> None:
        ctx = self._ctx("outlook", "alpha bravo charlie", 6, clipboard_text="clipboard fallback")

        start = self.runtime.mark_selection_start(ctx)
        self.assertTrue(start.ok)

        ctx.caret = 11
        end = self.runtime.mark_selection_end(ctx)
        self.assertTrue(end.ok)
        self.assertEqual(end.code, RuntimeErrorCode.UNSUPPORTED_SURFACE)
        self.assertTrue(end.payload["fallbackUsed"])
        self.assertEqual(end.payload["fallbackSource"], "buffer-range")
        self.assertEqual(end.payload["guidedFlow"]["stage"], "fallback-captured")

        read = self.runtime.read_selection_context(ctx)
        self.assertTrue(read.ok)
        self.assertIn("bravo", read.payload["startSnippet"])


if __name__ == "__main__":
    unittest.main()
