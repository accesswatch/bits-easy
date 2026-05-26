import sys
import tempfile
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime import (
    AppAdapter,
    AppContext,
    DriftAwareAdapter,
    RuntimeResult,
    RuntimeDispatcher,
    BitsEasyRuntime,
    load_runtime_config,
)


class DispatcherIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.config = load_runtime_config(self.repo_root)
        self.runtime = BitsEasyRuntime(
            adapters={
                "edge": AppAdapter("edge", supports_selection=True),
                "word": DriftAwareAdapter("word", supports_selection=True, drift_delta=1),
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

    def test_key_chord_dispatch_selection_start(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="beginner")
        ctx = self._ctx("edge", "alpha bravo", 5)

        out = dispatcher.dispatch_key_chord(ctx, "Grave+OpenBracket")
        self.assertTrue(out.result.ok)
        self.assertEqual(out.plan.command_id, "cmd.selection.markStart")

    def test_key_chord_dispatch_marker_status(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha bravo", 5)
        dispatcher.dispatch_command(ctx, "cmd.selection.markStart")

        out = dispatcher.dispatch_key_chord(ctx, "Grave+Semicolon")
        self.assertTrue(out.result.ok)
        self.assertEqual(out.plan.command_id, "cmd.selection.markerStatus")
        self.assertIn("telemetry", out.result.payload)

    def test_item_chooser_integration_command_routes(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha bravo", 0)

        out = dispatcher.dispatch_command(ctx, "cmd.integration.itemChooser.open")
        self.assertTrue(out.result.ok)
        self.assertEqual(out.plan.command_id, "cmd.integration.itemChooser.open")
        payload = out.result.payload or {}
        action = payload.get("integrationAction", {})
        self.assertEqual(action.get("provider"), "screenItemChooser")
        self.assertEqual(action.get("action"), "open")
        self.assertFalse(bool(action.get("ocr", True)))

    def test_item_chooser_ocr_hotkey_dispatch(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        out = dispatcher.dispatch_key_chord(ctx, "Grave+Shift+O")
        self.assertTrue(out.result.ok)
        self.assertEqual(out.plan.command_id, "cmd.integration.itemChooser.openOcr")
        action = (out.result.payload or {}).get("integrationAction", {})
        self.assertTrue(bool(action.get("ocr", False)))

    def test_glow_health_command_routes(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        class _GlowStub:
            def health(self):
                return RuntimeResult(ok=True, message="ok", payload={"status": "ok"})

        dispatcher._glow = _GlowStub()
        out = dispatcher.dispatch_command(ctx, "cmd.integration.glow.health")
        self.assertTrue(out.result.ok)
        self.assertEqual((out.result.payload or {}).get("status"), "ok")

    def test_glow_audit_command_routes(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        class _GlowStub:
            def audit(self, file_path, fmt=""):
                return RuntimeResult(ok=True, message="audit", payload={"path": str(file_path), "format": fmt or "docx"})

        dispatcher._glow = _GlowStub()
        out = dispatcher.dispatch_command(
            ctx,
            "cmd.integration.glow.audit",
            path="C:/docs/sample.docx",
            format="docx",
        )
        self.assertTrue(out.result.ok)
        self.assertEqual((out.result.payload or {}).get("format"), "docx")

    def test_glow_hotkey_bindings_dispatch(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        class _GlowStub:
            def health(self):
                return RuntimeResult(ok=True, message="health", payload={"op": "health"})

            def audit(self, file_path, fmt=""):
                return RuntimeResult(ok=True, message="audit", payload={"op": "audit", "path": str(file_path), "format": fmt})

            def fix(self, file_path, fmt=""):
                return RuntimeResult(ok=True, message="fix", payload={"op": "fix", "path": str(file_path), "format": fmt})

            def convert(self, file_path, from_format="", to_format="markdown"):
                return RuntimeResult(
                    ok=True,
                    message="convert",
                    payload={"op": "convert", "path": str(file_path), "from": from_format, "to": to_format},
                )

            def report(self, file_path, fmt="", report_type="json"):
                return RuntimeResult(
                    ok=True,
                    message="report",
                    payload={"op": "report", "path": str(file_path), "format": fmt, "reportType": report_type},
                )

        dispatcher._glow = _GlowStub()

        out_health = dispatcher.dispatch_key_chord(ctx, "Grave+Y")
        self.assertTrue(out_health.result.ok)
        self.assertEqual(out_health.plan.command_id, "cmd.integration.glow.health")

        out_audit = dispatcher.dispatch_key_chord(ctx, "Grave+E", path="C:/tmp/a.docx", format="docx")
        self.assertTrue(out_audit.result.ok)
        self.assertEqual(out_audit.plan.command_id, "cmd.integration.glow.audit")

        out_fix = dispatcher.dispatch_key_chord(ctx, "Grave+Shift+V", path="C:/tmp/f.docx", format="docx")
        self.assertTrue(out_fix.result.ok)
        self.assertEqual(out_fix.plan.command_id, "cmd.integration.glow.fix")

        out_convert = dispatcher.dispatch_key_chord(
            ctx,
            "Grave+Shift+K",
            path="C:/tmp/c.docx",
            fromFormat="docx",
            toFormat="markdown",
        )
        self.assertTrue(out_convert.result.ok)
        self.assertEqual(out_convert.plan.command_id, "cmd.integration.glow.convert")

        out_report = dispatcher.dispatch_key_chord(
            ctx,
            "Grave+Shift+L",
            path="C:/tmp/r.docx",
            format="docx",
            reportType="json",
        )
        self.assertTrue(out_report.result.ok)
        self.assertEqual(out_report.plan.command_id, "cmd.integration.glow.report")

    def test_profile_policy_is_applied_to_clipboard_paste(self) -> None:
        ctx = self._ctx("edge", "alpha bravo charlie", 0)

        self.runtime.copy_to_slot(ctx, slot=1, text="payload")

        beginner = RuntimeDispatcher(self.runtime, self.config, profile_id="beginner")
        expert = RuntimeDispatcher(self.runtime, self.config, profile_id="expert")

        out_beginner = beginner.dispatch_command(ctx, "cmd.clip.pasteFromSlot", slot=1)
        out_expert = expert.dispatch_command(ctx, "cmd.clip.pasteFromSlot", slot=1)

        self.assertTrue(out_beginner.result.ok)
        self.assertEqual(out_beginner.plan.confirmation, "always")
        self.assertEqual(out_beginner.plan.preview, "always")

        self.assertTrue(out_expert.result.ok)
        self.assertEqual(out_expert.plan.confirmation, "adaptive")
        self.assertEqual(out_expert.plan.preview, "never")

    def test_safety_gate_keeps_delete_confirmation(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="expert")
        ctx = self._ctx("edge", "alpha", 0)

        self.runtime.copy_to_slot(ctx, slot=3, text="to delete")
        out = dispatcher.dispatch_command(ctx, "cmd.clip.deleteSlot", slot=3)

        self.assertTrue(out.result.ok)
        self.assertEqual(out.plan.confirmation, "always")
        self.assertEqual(out.plan.safety_gate, "always-confirm")

    def test_outlook_fallback_through_dispatcher(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("outlook", "", 0, clipboard_text="message snippet")

        start = dispatcher.dispatch_command(ctx, "cmd.selection.markStart")
        self.assertTrue(start.result.ok)

        ctx.caret = 5
        end = dispatcher.dispatch_command(ctx, "cmd.selection.markEnd")
        self.assertTrue(end.result.ok)
        self.assertEqual(end.plan.confirmation, "inherit")
        self.assertTrue(end.result.payload["executionPolicy"]["safetyGate"] in ["none", "low-confidence-confirm", "always-confirm"])

    def test_marker_status_command_reports_state(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha bravo charlie", 6)

        status_before = dispatcher.dispatch_command(ctx, "cmd.selection.markerStatus")
        self.assertFalse(status_before.result.ok)
        self.assertFalse(status_before.result.payload["startMarkerSet"])

        started = dispatcher.dispatch_command(ctx, "cmd.selection.markStart")
        self.assertTrue(started.result.ok)

        status_after_start = dispatcher.dispatch_command(ctx, "cmd.selection.markerStatus")
        self.assertTrue(status_after_start.result.ok)
        self.assertTrue(status_after_start.result.payload["startMarkerSet"])
        self.assertFalse(status_after_start.result.payload["endMarkerSet"])
        self.assertIn("startMeta", status_after_start.result.payload)
        self.assertIn("capturedAt", status_after_start.result.payload["startMeta"])

        ctx.caret = 17
        ended = dispatcher.dispatch_command(ctx, "cmd.selection.markEnd")
        self.assertTrue(ended.result.ok)

        status_ready = dispatcher.dispatch_command(ctx, "cmd.selection.markerStatus")
        self.assertTrue(status_ready.result.ok)
        self.assertEqual(status_ready.result.payload["activeRangeStart"], 6)
        self.assertEqual(status_ready.result.payload["activeRangeEnd"], 17)
        self.assertIn("telemetry", status_ready.result.payload)
        self.assertGreaterEqual(status_ready.result.payload["telemetry"]["app"].get("markEndCaptured", 0), 1)

    def test_hotkey_discoverability_and_diagnostics(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        discover = dispatcher.dispatch_command(ctx, "cmd.help.availableHotkeys")
        self.assertTrue(discover.result.ok)
        self.assertGreater(discover.result.payload["count"], 0)
        hints = discover.result.payload.get("mnemonicHints", [])
        hint_commands = {str(row.get("commandId", "")) for row in hints}
        self.assertIn("cmd.journal.undoLast", hint_commands)
        self.assertIn("cmd.clip.copyToSlot", hint_commands)
        self.assertIn("cmd.integration.itemChooser.open", hint_commands)
        self.assertIn("cmd.integration.itemChooser.openOcr", hint_commands)

        diag = dispatcher.dispatch_command(ctx, "cmd.profile.hotkeyDiagnostics")
        self.assertTrue(diag.result.ok)
        self.assertIn("collisionCount", diag.result.payload)

    def test_multi_press_dispatch_and_disable_override(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        out_single = dispatcher.dispatch_key_chord(ctx, "Grave", press_count=1)
        self.assertTrue(out_single.result.ok)
        self.assertEqual(out_single.plan.command_id, "cmd.palette.open")
        self.assertEqual(out_single.result.payload["gesture"]["triggerKind"], "single-press")

        out_double = dispatcher.dispatch_key_chord(ctx, "Grave", press_count=2)
        self.assertTrue(out_double.result.ok)
        self.assertEqual(out_double.plan.command_id, "cmd.help.availableHotkeys")
        self.assertEqual(out_double.result.payload["gesture"]["triggerKind"], "double-press")

        dispatcher.multi_press_enabled_override = False
        out_disabled = dispatcher.dispatch_key_chord(ctx, "Grave", press_count=3)
        self.assertTrue(out_disabled.result.ok)
        self.assertEqual(out_disabled.plan.command_id, "cmd.palette.open")
        self.assertEqual(out_disabled.result.payload["gesture"]["triggerKind"], "single-press")

    def test_marker_range_is_used_by_selection_actions(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha bravo charlie delta", 6, clipboard_text="clipboard fallback")

        started = dispatcher.dispatch_command(ctx, "cmd.selection.markStart")
        self.assertTrue(started.result.ok)

        ctx.caret = 18
        ended = dispatcher.dispatch_command(ctx, "cmd.selection.markEnd")
        self.assertTrue(ended.result.ok)

        summarize = dispatcher.dispatch_command(ctx, "cmd.selection.summarize")
        self.assertTrue(summarize.result.ok)
        payload = summarize.result.payload or {}
        self.assertIn("content", payload)
        self.assertIn("bravo", str(payload.get("content", "")).lower())

    def test_marker_range_reconstructs_action_source_when_cache_missing(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha bravo charlie delta", 6, clipboard_text="clipboard fallback")

        started = dispatcher.dispatch_command(ctx, "cmd.selection.markStart")
        self.assertTrue(started.result.ok)

        ctx.caret = 18
        ended = dispatcher.dispatch_command(ctx, "cmd.selection.markEnd")
        self.assertTrue(ended.result.ok)

        # Simulate cache loss; selection actions should reconstruct from markers.
        self.runtime._selection_cache.pop("edge", None)

        summarize = dispatcher.dispatch_command(ctx, "cmd.selection.summarize")
        self.assertTrue(summarize.result.ok)
        payload = summarize.result.payload or {}
        self.assertIn("content", payload)
        self.assertIn("bravo", str(payload.get("content", "")).lower())

    def test_clip_select_slot_hotkey_applies_binding_args(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha bravo", 0, clipboard_text="slot payload")

        selected = dispatcher.dispatch_key_chord(ctx, "Grave+F3")
        self.assertTrue(selected.result.ok)
        self.assertEqual(selected.plan.command_id, "cmd.clip.selectSlot")
        self.assertEqual((selected.result.payload or {}).get("slot"), 3)

        copied = dispatcher.dispatch_command(ctx, "cmd.clip.copyToSlot")
        self.assertTrue(copied.result.ok)
        self.assertEqual((copied.result.payload or {}).get("slot"), 3)

        described = dispatcher.dispatch_command(ctx, "cmd.clip.describeSlot")
        self.assertTrue(described.result.ok)
        self.assertEqual((described.result.payload or {}).get("slot"), 3)

    def test_shortcut_catalog_command_routes(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        created = dispatcher.dispatch_command(
            ctx,
            "cmd.cuts.create",
            name="Docs",
            target="C:/docs",
            targetType="folder",
        )
        self.assertTrue(created.result.ok)
        sid = created.result.payload["shortcutId"]

        cat = dispatcher.dispatch_command(ctx, "cmd.cuts.assignCategory", shortcutId=sid, category="work")
        self.assertTrue(cat.result.ok)

        listed = dispatcher.dispatch_command(ctx, "cmd.cuts.list", category="work")
        self.assertTrue(listed.result.ok)
        self.assertGreaterEqual(len(listed.result.payload["items"]), 1)

        preset = dispatcher.dispatch_command(ctx, "cmd.cuts.createPreset", preset="daily", shortcutIds=[sid])
        self.assertTrue(preset.result.ok)

        run = dispatcher.dispatch_command(ctx, "cmd.cuts.runPreset", preset="daily")
        self.assertTrue(run.result.ok)
        self.assertEqual(len(run.result.payload["items"]), 1)

        dashboard = dispatcher.dispatch_command(ctx, "cmd.cuts.dashboard")
        self.assertTrue(dashboard.result.ok)
        self.assertIn("total", dashboard.result.payload)

    def test_clip_library_entry_routes(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        self.runtime.copy_to_slot(ctx, slot=1, text="clip one")
        ingest = dispatcher.dispatch_command(ctx, "cmd.clip.library.ingestSlot", slot=1)
        self.assertTrue(ingest.result.ok)
        clip_id = ingest.result.payload["clipId"]

        folder = dispatcher.dispatch_command(ctx, "cmd.clip.library.createFolder", folderName="Work", category="project")
        self.assertTrue(folder.result.ok)
        folder_id = folder.result.payload["folderId"]

        move = dispatcher.dispatch_command(ctx, "cmd.clip.library.moveToFolder", clipId=clip_id, folderId=folder_id)
        self.assertTrue(move.result.ok)

        category = dispatcher.dispatch_command(ctx, "cmd.clip.library.assignCategory", clipId=clip_id, category="project")
        self.assertTrue(category.result.ok)

        alias = dispatcher.dispatch_command(
            ctx,
            "cmd.clip.library.retainSlotAlias",
            clipId=clip_id,
            slotAlias="Slot A",
            aliasStrategy="rename",
        )
        self.assertTrue(alias.result.ok)

        open_view = dispatcher.dispatch_command(ctx, "cmd.clip.library.open")
        self.assertTrue(open_view.result.ok)
        self.assertIn("smartViews", open_view.result.payload)

    def test_clip_browser_search_and_pin_routes(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha bravo", 0, clipboard_text="alpha bravo")
        self.runtime.copy_to_slot(ctx, slot=1, text="alpha note")
        self.runtime.copy_to_slot(ctx, slot=2, text="beta note")

        pin = dispatcher.dispatch_command(ctx, "cmd.clip.browser.batchAction", slots=[2], action="pin")
        self.assertTrue(pin.result.ok)

        search = dispatcher.dispatch_command(
            ctx,
            "cmd.clip.browser.search",
            query="beta",
            favoritesOnly=True,
        )
        self.assertTrue(search.result.ok)
        self.assertEqual(len(search.result.payload["slots"]), 1)
        self.assertEqual(search.result.payload["slots"][0]["slot"], 2)

    def test_shortcuts_e05_routes(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        created = dispatcher.dispatch_command(
            ctx,
            "cmd.shortcuts.create",
            name="Repo",
            target="C:/code",
            targetType="folder",
        )
        self.assertTrue(created.result.ok)
        sid = created.result.payload["shortcutId"]

        cat = dispatcher.dispatch_command(
            ctx,
            "cmd.shortcuts.assignCategory",
            shortcutId=sid,
            category="work",
        )
        self.assertTrue(cat.result.ok)

        preset = dispatcher.dispatch_command(
            ctx,
            "cmd.shortcuts.createPreset",
            preset="dev",
            shortcutIds=[sid],
        )
        self.assertTrue(preset.result.ok)

        run = dispatcher.dispatch_command(ctx, "cmd.shortcuts.runPreset", preset="dev")
        self.assertTrue(run.result.ok)
        self.assertEqual(len(run.result.payload["items"]), 1)

        focused = dispatcher.dispatch_command(ctx, "cmd.shortcuts.launcher.addFocusedApp")
        self.assertTrue(focused.result.ok)

        launcher = dispatcher.dispatch_command(ctx, "cmd.shortcuts.launcher.open")
        self.assertTrue(launcher.result.ok)
        self.assertGreaterEqual(launcher.result.payload["count"], 1)

        mapped = dispatcher.dispatch_command(
            ctx,
            "cmd.shortcuts.drive.map",
            driveLetter="Y",
            folderPath="C:/workspace",
        )
        self.assertTrue(mapped.result.ok)

        drives = dispatcher.dispatch_command(ctx, "cmd.shortcuts.drive.list")
        self.assertTrue(drives.result.ok)
        self.assertGreaterEqual(drives.result.payload["count"], 1)

    def test_tagging_and_table_capture_routes(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        tag_a = dispatcher.dispatch_command(ctx, "cmd.tags.session.tag", path="C:/tmp/a.txt")
        tag_b = dispatcher.dispatch_command(ctx, "cmd.tags.session.tag", path="C:/tmp/b.txt")
        self.assertTrue(tag_a.result.ok)
        self.assertTrue(tag_b.result.ok)

        count = dispatcher.dispatch_command(ctx, "cmd.tags.session.count")
        self.assertTrue(count.result.ok)
        self.assertEqual(count.result.payload["count"], 2)

        batch = dispatcher.dispatch_command(ctx, "cmd.tags.session.batchDelete")
        self.assertTrue(batch.result.ok)
        self.assertEqual(batch.result.payload["count"], 2)

        capture = dispatcher.dispatch_command(
            ctx,
            "cmd.table.capture",
            rows=[["ColA", "ColB"], ["1", "2"]],
            separator=",",
        )
        self.assertTrue(capture.result.ok)

        export = dispatcher.dispatch_command(ctx, "cmd.table.capture.exportClipboard")
        self.assertTrue(export.result.ok)
        self.assertIn("ColA,ColB", export.result.payload["content"])

    def test_tagging_route_inferrs_path_from_clipboard(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "", 0, clipboard_text='"C:/tmp/from-clipboard.txt"\nignored')

        tagged = dispatcher.dispatch_command(ctx, "cmd.tags.session.tag")
        self.assertTrue(tagged.result.ok)
        self.assertEqual(tagged.result.payload["path"], "C:/tmp/from-clipboard.txt")

        report = dispatcher.dispatch_command(ctx, "cmd.tags.session.report")
        self.assertTrue(report.result.ok)
        self.assertEqual(report.result.payload["count"], 1)
        self.assertEqual(report.result.payload["items"][0]["path"], "C:/tmp/from-clipboard.txt")

    def test_tagging_toggle_current_and_tag_from_selection(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "C:/tmp/from-selection.txt", 0)

        from_selection = dispatcher.dispatch_command(ctx, "cmd.tags.session.tagFromSelection")
        self.assertTrue(from_selection.result.ok)
        self.assertEqual(from_selection.result.payload["path"], "C:/tmp/from-selection.txt")

        toggled_off = dispatcher.dispatch_command(
            ctx,
            "cmd.tags.session.toggleCurrent",
            path="C:/tmp/from-selection.txt",
        )
        self.assertTrue(toggled_off.result.ok)
        self.assertEqual(toggled_off.result.payload["toggledTo"], "untagged")

        toggled_on = dispatcher.dispatch_key_chord(ctx, "Grave+Alt+G", press_count=1)
        self.assertTrue(toggled_on.result.ok)
        self.assertEqual(toggled_on.plan.command_id, "cmd.tags.session.toggleCurrent")
        self.assertEqual(toggled_on.result.payload["toggledTo"], "tagged")

        via_hotkey = dispatcher.dispatch_key_chord(ctx, "Grave+Alt+Shift+G", press_count=1)
        self.assertTrue(via_hotkey.result.ok)
        self.assertEqual(via_hotkey.plan.command_id, "cmd.tags.session.tagFromSelection")

    def test_glow_leader_sequence_help_and_routing(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        class _GlowStub:
            def health(self):
                return RuntimeResult(ok=True, message="health", payload={"op": "health"})

        dispatcher._glow = _GlowStub()

        leader = dispatcher.dispatch_key_chord(ctx, "Grave+G", press_count=1)
        self.assertTrue(leader.result.ok)
        self.assertEqual(leader.plan.command_id, "cmd.sequence.glow.leader")

        help_out = dispatcher.dispatch_key_chord(ctx, "Grave+Slash", press_count=1)
        self.assertTrue(help_out.result.ok)
        self.assertEqual(help_out.plan.command_id, "cmd.help.availableHotkeys")
        self.assertEqual((help_out.result.payload or {}).get("helpScope"), "glow")
        self.assertIn("virtualView", help_out.result.payload or {})

        leader_again = dispatcher.dispatch_key_chord(ctx, "Grave+G", press_count=1)
        self.assertTrue(leader_again.result.ok)
        routed = dispatcher.dispatch_key_chord(ctx, "Grave+Y", press_count=1)
        self.assertTrue(routed.result.ok)
        self.assertEqual(routed.plan.command_id, "cmd.integration.glow.health")

    def test_layered_keymap_precedence_app_override(self) -> None:
        # Same chord as global BITS-EASY helper key, but app override should win for edge.
        self.config.keymap_bindings.insert(
            0,
            {
                "commandId": "cmd.help.availableHotkeys",
                "keyChord": "Grave",
                "scope": "app-override",
                "appId": "edge",
                "enabled": True,
                "safetyGate": "none",
            },
        )
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        out = dispatcher.dispatch_key_chord(ctx, "Grave", press_count=1)
        self.assertTrue(out.result.ok)
        self.assertEqual(out.plan.command_id, "cmd.help.availableHotkeys")

    def test_profile_fallback_order_executes_palette(self) -> None:
        self.config.profiles["balanced"]["fallbackOrder"] = ["palette"]
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        out = dispatcher.dispatch_key_chord(ctx, "Grave+Shift+Q", press_count=1)
        self.assertTrue(out.result.ok)
        self.assertEqual(out.plan.command_id, "cmd.palette.open")
        self.assertTrue(out.result.payload["gesture"]["fallbackUsed"])

    def test_virtualized_scope_precedence_when_context_is_virtualized(self) -> None:
        self.config.keymap_bindings.insert(
            0,
            {
                "commandId": "cmd.help.availableHotkeys",
                "keyChord": "Grave+Q",
                "scope": "virtualized",
                "appId": None,
                "enabled": True,
                "safetyGate": "none",
            },
        )
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = AppContext(
            app_id="edge",
            window_id="win-edge",
            control_id="virtualized-pane",
            buffer="alpha",
            caret=0,
            clipboard_text="",
        )

        out = dispatcher.dispatch_key_chord(ctx, "Grave+Q", press_count=1)
        self.assertTrue(out.result.ok)
        self.assertEqual(out.plan.command_id, "cmd.help.availableHotkeys")

    def test_hotkey_diagnostics_exposes_precedence_and_fallback(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        diag = dispatcher.dispatch_command(ctx, "cmd.profile.hotkeyDiagnostics")
        self.assertTrue(diag.result.ok)
        self.assertIn("precedence", diag.result.payload)
        self.assertIn("fallbackOrder", diag.result.payload)
        self.assertIn("resolutionTrace", diag.result.payload)

        focused = dispatcher.dispatch_command(ctx, "cmd.profile.hotkeyDiagnostics", keyChord="Grave")
        self.assertTrue(focused.result.ok)
        self.assertIn("Grave", focused.result.payload["resolutionTrace"])

    def test_hotkey_chain_routes(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        created = dispatcher.dispatch_command(
            ctx,
            "cmd.profile.hotkeyChainCreate",
            name="chain-a",
            commandIds=["cmd.palette.open", "cmd.help.availableHotkeys"],
        )
        self.assertTrue(created.result.ok)

        listed = dispatcher.dispatch_command(ctx, "cmd.profile.hotkeyChainList")
        self.assertTrue(listed.result.ok)
        self.assertGreaterEqual(listed.result.payload["count"], 1)

        ran = dispatcher.dispatch_command(ctx, "cmd.profile.hotkeyChainRun", name="chain-a")
        self.assertTrue(ran.result.ok)
        self.assertEqual(len(ran.result.payload["steps"]), 2)

    def test_outlook_tagging_routes(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("outlook", "", 0)

        tag = dispatcher.dispatch_command(
            ctx,
            "cmd.tags.outlook.tag",
            messageId="m1",
            sender="alice@example.com",
            subject="Report",
        )
        self.assertTrue(tag.result.ok)

        report = dispatcher.dispatch_command(ctx, "cmd.tags.outlook.report")
        self.assertTrue(report.result.ok)
        self.assertEqual(report.result.payload["count"], 1)

        move = dispatcher.dispatch_command(ctx, "cmd.tags.outlook.batchMove", folder="Inbox/Archive")
        self.assertTrue(move.result.ok)
        self.assertEqual(move.result.payload["action"], "move")

    def test_dialog_path_insert_routes(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "", 0)

        created = dispatcher.dispatch_command(
            ctx,
            "cmd.shortcuts.create",
            name="Workspace",
            target="C:/workspace",
            targetType="folder",
        )
        self.assertTrue(created.result.ok)
        sid = created.result.payload["shortcutId"]

        detect = dispatcher.dispatch_command(ctx, "cmd.shortcuts.dialog.detect", windowTitle="Open File")
        self.assertTrue(detect.result.ok)
        self.assertEqual(detect.result.payload["kind"], "open")

        insert = dispatcher.dispatch_command(
            ctx,
            "cmd.shortcuts.dialog.insertPath",
            shortcutId=sid,
            windowTitle="Open File",
            supportsInsertion=False,
        )
        self.assertTrue(insert.result.ok)
        self.assertFalse(insert.result.payload["inserted"])
        self.assertGreaterEqual(len(insert.result.payload["fallbackGuidance"]), 1)

    def test_progress_and_speech_history_routes(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "", 0)

        plan = dispatcher.dispatch_command(ctx, "cmd.utility.progressCues.plan", totalSteps=40, tutorial=True)
        self.assertTrue(plan.result.ok)
        self.assertIn("cueSteps", plan.result.payload)

        self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.speech.history.capture", text="alpha").result.ok)
        self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.speech.history.capture", text="beta").result.ok)

        browse = dispatcher.dispatch_command(ctx, "cmd.speech.history.browse", direction="left")
        self.assertTrue(browse.result.ok)

        copy_range = dispatcher.dispatch_command(ctx, "cmd.speech.history.copyRange", start=0, end=1)
        self.assertTrue(copy_range.result.ok)
        self.assertIn("alpha", copy_range.result.payload["text"])

        vv = dispatcher.dispatch_command(ctx, "cmd.speech.history.virtualView")
        self.assertTrue(vv.result.ok)
        self.assertGreaterEqual(vv.result.payload["count"], 2)

    def test_symbol_assistant_routes(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "", 0)

        ins = dispatcher.dispatch_command(ctx, "cmd.utility.symbol.insertByCode", code="169")
        self.assertTrue(ins.result.ok)
        self.assertEqual(ins.result.payload["symbol"], "©")

        search = dispatcher.dispatch_command(ctx, "cmd.utility.symbol.search", query="trade")
        self.assertTrue(search.result.ok)
        self.assertGreaterEqual(search.result.payload["count"], 1)

        recent = dispatcher.dispatch_command(ctx, "cmd.utility.symbol.recent")
        self.assertTrue(recent.result.ok)
        self.assertEqual(recent.result.payload["code"], "169")

    def test_window_bookmarks_and_system_report_routes(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "", 0)

        assigned = dispatcher.dispatch_command(
            ctx,
            "cmd.utility.windowBookmark.assign",
            slot=1,
            windowId="win-edge-main",
            appId="edge",
            name="Edge Main",
        )
        self.assertTrue(assigned.result.ok)

        recall = dispatcher.dispatch_command(ctx, "cmd.utility.windowBookmark.recall", slot=1)
        self.assertTrue(recall.result.ok)
        self.assertEqual(recall.result.payload["windowId"], "win-edge-main")

        listing = dispatcher.dispatch_command(ctx, "cmd.utility.windowBookmark.list")
        self.assertTrue(listing.result.ok)
        self.assertGreaterEqual(listing.result.payload["count"], 1)

        report = dispatcher.dispatch_command(ctx, "cmd.utility.systemReport.open")
        self.assertTrue(report.result.ok)
        self.assertIn("os", report.result.payload)

    def test_adaptive_selection_and_confidence_routes(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx(
            "edge",
            "We should follow up with the team next week and define action owners.",
            0,
        )

        summary = dispatcher.dispatch_command(ctx, "cmd.selection.summarize")
        self.assertTrue(summary.result.ok)

        confidence = dispatcher.dispatch_command(ctx, "cmd.result.readConfidence")
        self.assertTrue(confidence.result.ok)
        self.assertIn("confidence", confidence.result.payload)

        fallbacks = dispatcher.dispatch_command(ctx, "cmd.result.openFallbacks")
        self.assertTrue(fallbacks.result.ok)
        self.assertGreaterEqual(len(fallbacks.result.payload["fallbackCommandIds"]), 1)

        actions = dispatcher.dispatch_command(ctx, "cmd.selection.extractActions")
        self.assertTrue(actions.result.ok)

        rewrite = dispatcher.dispatch_command(ctx, "cmd.selection.rewriteBeginner")
        self.assertTrue(rewrite.result.ok)

    def test_selection_commands_get_additive_ai_augmentation(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced", data_root=Path(tmpdir) / "data")
            ctx = self._ctx(
                "edge",
                "We should follow up with the team next week and define action owners.",
                0,
            )

            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.ai.key.set", provider="openai", key="k-live").result.ok)
            summary = dispatcher.dispatch_command(ctx, "cmd.selection.summarize")
            self.assertTrue(summary.result.ok)
            self.assertIn("content", summary.result.payload)
            self.assertIn("aiAugmentation", summary.result.payload)
            self.assertTrue(summary.result.payload["aiAugmentation"]["enabled"])

            capture = dispatcher.dispatch_command(ctx, "cmd.capture.quickInbox")
            self.assertTrue(capture.result.ok)
            self.assertIn("aiAugmentation", capture.result.payload)

            note = dispatcher.dispatch_command(
                ctx,
                "cmd.notes.quickCapture",
                text="Please rewrite this note for beginner clarity.",
            )
            self.assertTrue(note.result.ok)
            self.assertIn("aiAugmentation", note.result.payload)

            help_set = dispatcher.dispatch_command(
                ctx,
                "cmd.notes.help.set",
                text="Use shorter phrases and clear labels.",
                appId="edge",
            )
            self.assertTrue(help_set.result.ok)
            self.assertIn("aiAugmentation", help_set.result.payload)

            spell = dispatcher.dispatch_command(ctx, "cmd.spell.checkCurrentWord")
            self.assertTrue(spell.result.ok)
            self.assertIn("aiAugmentation", spell.result.payload)

    def test_quick_capture_routing_routes(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "capture this snippet", 0)

        saved = dispatcher.dispatch_command(ctx, "cmd.capture.quickInbox")
        self.assertTrue(saved.result.ok)
        capture_id = saved.result.payload["captureId"]

        routed = dispatcher.dispatch_command(
            ctx,
            "cmd.capture.quickInbox.route",
            captureId=capture_id,
            target="notes",
        )
        self.assertTrue(routed.result.ok)

        listed = dispatcher.dispatch_command(ctx, "cmd.capture.quickInbox.list", route="notes")
        self.assertTrue(listed.result.ok)
        self.assertGreaterEqual(listed.result.payload["count"], 1)

    def test_operation_journal_routes(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "capture this snippet", 0)

        saved = dispatcher.dispatch_command(ctx, "cmd.capture.quickInbox")
        capture_id = saved.result.payload["captureId"]
        dispatcher.dispatch_command(
            ctx,
            "cmd.capture.quickInbox.route",
            captureId=capture_id,
            target="clips",
        )

        journal = dispatcher.dispatch_command(ctx, "cmd.journal.list", appId="edge")
        self.assertTrue(journal.result.ok)
        self.assertGreaterEqual(journal.result.payload["count"], 1)

    def test_operation_journal_executes_rollback_handler(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "capture this snippet", 0)

        saved = dispatcher.dispatch_command(ctx, "cmd.capture.quickInbox")
        capture_id = saved.result.payload["captureId"]

        routed = dispatcher.dispatch_command(
            ctx,
            "cmd.capture.quickInbox.route",
            captureId=capture_id,
            target="notes",
        )
        self.assertTrue(routed.result.ok)

        journal = dispatcher.dispatch_command(ctx, "cmd.journal.list", appId="edge", actionType="mutating")
        items = list(journal.result.payload["items"])
        route_entry = next((x for x in reversed(items) if x["commandId"] == "cmd.capture.quickInbox.route"), None)
        self.assertIsNotNone(route_entry)

        rollback = dispatcher.dispatch_command(
            ctx,
            "cmd.journal.rollback",
            entryId=route_entry["entryId"],
        )
        self.assertTrue(rollback.result.ok)

        routed_items = dispatcher.dispatch_command(ctx, "cmd.capture.quickInbox.list", route="inbox")
        self.assertTrue(routed_items.result.ok)
        self.assertGreaterEqual(routed_items.result.payload["count"], 1)

    def test_operation_journal_undo_last_reversible_action(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "capture this snippet", 0)

        saved = dispatcher.dispatch_command(ctx, "cmd.capture.quickInbox")
        capture_id = saved.result.payload["captureId"]
        routed = dispatcher.dispatch_command(
            ctx,
            "cmd.capture.quickInbox.route",
            captureId=capture_id,
            target="notes",
        )
        self.assertTrue(routed.result.ok)

        undone = dispatcher.dispatch_command(ctx, "cmd.journal.undoLast")
        self.assertTrue(undone.result.ok)
        self.assertEqual(undone.result.payload["rolledBackCommandId"], "cmd.capture.quickInbox.route")
        self.assertIn("narration", undone.result.payload)
        self.assertIn("nextAction", undone.result.payload)

        inbox_items = dispatcher.dispatch_command(ctx, "cmd.capture.quickInbox.list", route="inbox")
        self.assertTrue(inbox_items.result.ok)
        self.assertGreaterEqual(inbox_items.result.payload["count"], 1)

    def test_operation_journal_undo_last_for_cuts_create(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        created = dispatcher.dispatch_command(
            ctx,
            "cmd.cuts.create",
            name="Temp Shortcut",
            target="C:/tmp/rollback-cut.txt",
            targetType="file",
        )
        self.assertTrue(created.result.ok)
        sid = created.result.payload["shortcutId"]

        undone = dispatcher.dispatch_command(ctx, "cmd.journal.undoLast")
        self.assertTrue(undone.result.ok)
        self.assertEqual(undone.result.payload["rolledBackCommandId"], "cmd.cuts.create")

        listed = dispatcher.dispatch_command(ctx, "cmd.cuts.list")
        self.assertTrue(listed.result.ok)
        ids = {row["shortcutId"] for row in listed.result.payload.get("items", [])}
        self.assertNotIn(sid, ids)

    def test_guided_prompt_is_added_on_first_core_mission_completion(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dispatcher = RuntimeDispatcher(
                self.runtime,
                self.config,
                profile_id="balanced",
                data_root=Path(tmpdir) / "data",
            )
            ctx = self._ctx("edge", "alpha bravo", 0)

            first = dispatcher.dispatch_command(ctx, "cmd.selection.markStart")
            self.assertTrue(first.result.ok)
            telemetry = first.result.payload.get("missionTelemetry", {})
            self.assertTrue(telemetry.get("firstCompletion", False))
            self.assertIn("guidedMissionPrompt", first.result.payload)

            second = dispatcher.dispatch_command(ctx, "cmd.selection.markStart")
            self.assertTrue(second.result.ok)
            second_telemetry = second.result.payload.get("missionTelemetry", {})
            self.assertFalse(second_telemetry.get("firstCompletion", True))

    def test_operation_journal_undo_last_for_cuts_assign_category(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dispatcher = RuntimeDispatcher(
                self.runtime,
                self.config,
                profile_id="balanced",
                data_root=Path(tmpdir) / "data",
            )
            ctx = self._ctx("edge", "alpha", 0)

            created = dispatcher.dispatch_command(
                ctx,
                "cmd.cuts.create",
                name="Categorized Shortcut",
                target="C:/tmp/cat-cut.txt",
                targetType="file",
            )
            self.assertTrue(created.result.ok)
            sid = created.result.payload["shortcutId"]

            categorized = dispatcher.dispatch_command(
                ctx,
                "cmd.cuts.assignCategory",
                shortcutId=sid,
                category="work",
            )
            self.assertTrue(categorized.result.ok)

            undone = dispatcher.dispatch_command(ctx, "cmd.journal.undoLast")
            self.assertTrue(undone.result.ok)
            self.assertEqual(
                undone.result.payload["rolledBackCommandId"],
                "cmd.cuts.assignCategory",
            )

            listed = dispatcher.dispatch_command(ctx, "cmd.cuts.list")
            self.assertTrue(listed.result.ok)
            row = next(
                x
                for x in listed.result.payload.get("items", [])
                if x.get("shortcutId") == sid
            )
            self.assertEqual(row.get("category"), "general")

    def test_operation_journal_undo_last_for_notes_category_move(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dispatcher = RuntimeDispatcher(
                self.runtime,
                self.config,
                profile_id="balanced",
                data_root=Path(tmpdir) / "data",
            )
            ctx = self._ctx("edge", "alpha", 0)

            created = dispatcher.dispatch_command(
                ctx,
                "cmd.notes.category.create",
                category="work",
            )
            self.assertTrue(created.result.ok)

            moved = dispatcher.dispatch_command(
                ctx,
                "cmd.notes.category.move",
                category="work",
                parent="projects",
            )
            self.assertTrue(moved.result.ok)

            undone = dispatcher.dispatch_command(ctx, "cmd.journal.undoLast")
            self.assertTrue(undone.result.ok)
            self.assertEqual(
                undone.result.payload["rolledBackCommandId"],
                "cmd.notes.category.move",
            )

            tree = dispatcher.dispatch_command(ctx, "cmd.notes.category.tree")
            self.assertTrue(tree.result.ok)
            root_children = tree.result.payload.get("tree", {}).get("root", [])
            self.assertIn("work", root_children)

    def test_guided_prompt_on_first_completion_for_notes_core(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dispatcher = RuntimeDispatcher(
                self.runtime,
                self.config,
                profile_id="balanced",
                data_root=Path(tmpdir) / "data",
            )
            ctx = self._ctx("edge", "quick note text", 0)

            out = dispatcher.dispatch_command(ctx, "cmd.notes.quickCapture", text="first")
            self.assertTrue(out.result.ok)
            telemetry = out.result.payload.get("missionTelemetry", {})
            self.assertEqual(telemetry.get("missionId"), "notes-core")
            self.assertTrue(telemetry.get("firstCompletion", False))
            self.assertIn("guidedMissionPrompt", out.result.payload)

    def test_journal_rollback_coverage_report_and_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dispatcher = RuntimeDispatcher(
                self.runtime,
                self.config,
                profile_id="balanced",
                data_root=Path(tmpdir) / "data",
            )
            ctx = self._ctx("edge", "alpha", 0)
            out_path = Path(tmpdir) / "rollback-coverage.md"

            report = dispatcher.dispatch_command(
                ctx,
                "cmd.journal.rollbackCoverage",
                outPath=str(out_path),
            )
            self.assertTrue(report.result.ok)
            payload = report.result.payload
            self.assertTrue(out_path.exists())
            self.assertGreater(payload["total"], 0)
            self.assertGreater(payload["rollbackCapablePercent"], 0.0)

            by_command = {row["commandId"]: row for row in payload.get("items", [])}
            required = [
                "cmd.cuts.create",
                "cmd.cuts.assignCategory",
                "cmd.notes.category.move",
                "cmd.notes.mode.set",
                "cmd.author.pipeline.polish",
                "cmd.author.template.apply",
                "cmd.author.html.fixApply",
            ]
            for command_id in required:
                self.assertIn(command_id, by_command)
                self.assertIn(by_command[command_id]["status"], ["full", "conditional"])

    def test_first_completion_guided_prompt_across_core_families(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dispatcher = RuntimeDispatcher(
                self.runtime,
                self.config,
                profile_id="balanced",
                data_root=Path(tmpdir) / "data",
            )

            sel_ctx = self._ctx("edge", "alpha bravo", 0)
            selection_out = dispatcher.dispatch_command(sel_ctx, "cmd.selection.markStart")
            self.assertTrue(selection_out.result.ok)
            self.assertIn("guidedMissionPrompt", selection_out.result.payload)
            self.assertEqual(selection_out.result.payload["missionTelemetry"]["missionId"], "select-range")

            clip_ctx = self._ctx("edge", "clip text", 0, clipboard_text="clip text")
            clip_out = dispatcher.dispatch_command(clip_ctx, "cmd.clip.copyToSlot", slot=3)
            self.assertTrue(clip_out.result.ok)
            self.assertIn("guidedMissionPrompt", clip_out.result.payload)
            self.assertEqual(clip_out.result.payload["missionTelemetry"]["missionId"], "clips-core")

            cuts_out = dispatcher.dispatch_command(
                self._ctx("edge", "alpha", 0),
                "cmd.cuts.create",
                name="mission-cut",
                target="C:/tmp/mission-cut.txt",
                targetType="file",
            )
            self.assertTrue(cuts_out.result.ok)
            self.assertIn("guidedMissionPrompt", cuts_out.result.payload)
            self.assertEqual(cuts_out.result.payload["missionTelemetry"]["missionId"], "cuts-core")

            notes_out = dispatcher.dispatch_command(
                self._ctx("edge", "note", 0),
                "cmd.notes.quickCapture",
                text="note first",
            )
            self.assertTrue(notes_out.result.ok)
            self.assertIn("guidedMissionPrompt", notes_out.result.payload)
            self.assertEqual(notes_out.result.payload["missionTelemetry"]["missionId"], "notes-core")

            diary_out = dispatcher.dispatch_command(
                self._ctx("edge", "diary", 0),
                "cmd.diary.create",
                title="Review",
                startsAt="2026-05-22T14:00:00+00:00",
                notes="weekly",
            )
            self.assertTrue(diary_out.result.ok)
            self.assertIn("guidedMissionPrompt", diary_out.result.payload)
            self.assertEqual(diary_out.result.payload["missionTelemetry"]["missionId"], "diary-core")

    def test_e07_e08_routes_with_google_sync_dry_run(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.time.speak").result.ok)
        self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.time.stopwatch.start").result.ok)
        self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.time.countdown.start", minutes=1).result.ok)
        self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.time.monitor.start", brailleMode=True).result.ok)

        appt = dispatcher.dispatch_command(
            ctx,
            "cmd.diary.create",
            title="Standup",
            startsAt="2026-05-21T14:00:00+00:00",
            notes="daily",
        )
        self.assertTrue(appt.result.ok)

        task = dispatcher.dispatch_command(
            ctx,
            "cmd.tasks.create",
            title="Prepare status",
            dueAt="2026-05-21T15:00:00+00:00",
            category="work",
            priority="high",
        )
        self.assertTrue(task.result.ok)
        self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.tasks.syncGoogleCalendar", dryRun=True).result.ok)

        contact = dispatcher.dispatch_command(
            ctx,
            "cmd.contacts.create",
            name="Jane Doe",
            email="jane@example.com",
            phone="555-0101",
        )
        self.assertTrue(contact.result.ok)
        cid = contact.result.payload["contactId"]

        self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.contacts.search", query="jane").result.ok)
        self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.contacts.insertField", contactId=cid, field="email").result.ok)
        self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.contacts.syncGoogle", dryRun=True).result.ok)
        self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.mail.extractSender", name="Jane", email="jane@example.com").result.ok)
        self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.whatsapp.voice", mode="send").result.ok)
        self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.x.timeline", items=["a", "b"], cursor=1).result.ok)
        self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.social.orbit.summary", accountItems={"mastodon": ["one"]}).result.ok)

    def test_e10_database_and_jamal_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced", data_root=Path(tmpdir) / "bits_easy")
            ctx = self._ctx("edge", "alpha", 0)

            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.create", name="inventory").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.select", name="inventory").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.list").result.ok)
            self.assertTrue(
                dispatcher.dispatch_command(
                    ctx,
                    "cmd.db.field.define",
                    name="name",
                    fieldType="text",
                    required=True,
                ).result.ok
            )

            added = dispatcher.dispatch_command(ctx, "cmd.db.entry.add", values={"name": "item-a"})
            self.assertTrue(added.result.ok)
            eid = added.result.payload["entryId"]

            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.entry.list").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.entry.grid", sortBy="name", limit=10).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.entry.detail", entryId=eid).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.search", field="name", query="item").result.ok)
            self.assertTrue(
                dispatcher.dispatch_command(
                    ctx,
                    "cmd.db.search.advanced",
                    query="item",
                    filters={"name": "item"},
                    limit=5,
                ).result.ok
            )
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.sort", field="name", descending=False).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.dashboard").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.export.json", outPath="dist/records-e10.json").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.template.apply", template="tasks", database="tasks-db").result.ok)

            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.jamal.export", outPath="dist/jamal-e10.json").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.jamal.launch", datasetPath="dist/jamal-e10.json").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.jamal.return").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.jamal.import", inPath="dist/jamal-e10.json", database="inventory-import").result.ok)
            self.assertTrue(
                dispatcher.dispatch_command(
                    ctx,
                    "cmd.jamal.sync",
                    incomingEntries=[{"entryId": eid, "values": {"name": "item-b"}}],
                    apply=False,
                ).result.ok
            )


if __name__ == "__main__":
    unittest.main()

