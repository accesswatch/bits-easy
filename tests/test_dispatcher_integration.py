import sys
import tempfile
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime import (
    AppAdapter,
    AppContext,
    DriftAwareAdapter,
    RuntimeDispatcher,
    SpellforgeRuntime,
    load_runtime_config,
)


class DispatcherIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.config = load_runtime_config(self.repo_root)
        self.runtime = SpellforgeRuntime(
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

        out = dispatcher.dispatch_key_chord(ctx, "CapsLock+OpenBracket")
        self.assertTrue(out.result.ok)
        self.assertEqual(out.plan.command_id, "cmd.selection.markStart")

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

    def test_hotkey_discoverability_and_diagnostics(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        discover = dispatcher.dispatch_command(ctx, "cmd.help.availableHotkeys")
        self.assertTrue(discover.result.ok)
        self.assertGreater(discover.result.payload["count"], 0)

        diag = dispatcher.dispatch_command(ctx, "cmd.profile.hotkeyDiagnostics")
        self.assertTrue(diag.result.ok)
        self.assertIn("collisionCount", diag.result.payload)

    def test_multi_press_dispatch_and_disable_override(self) -> None:
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        out_double = dispatcher.dispatch_key_chord(ctx, "CapsLock+Space", press_count=2)
        self.assertTrue(out_double.result.ok)
        self.assertEqual(out_double.plan.command_id, "cmd.help.availableHotkeys")
        self.assertEqual(out_double.result.payload["gesture"]["triggerKind"], "double-press")

        dispatcher.multi_press_enabled_override = False
        out_disabled = dispatcher.dispatch_key_chord(ctx, "CapsLock+Space", press_count=3)
        self.assertTrue(out_disabled.result.ok)
        self.assertEqual(out_disabled.plan.command_id, "cmd.palette.open")
        self.assertEqual(out_disabled.result.payload["gesture"]["triggerKind"], "single-press")

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

        open_view = dispatcher.dispatch_command(ctx, "cmd.clip.library.open")
        self.assertTrue(open_view.result.ok)

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

    def test_layered_keymap_precedence_app_override(self) -> None:
        # Same chord as global palette open, but app override should win for edge.
        self.config.keymap_bindings.insert(
            0,
            {
                "commandId": "cmd.help.availableHotkeys",
                "keyChord": "CapsLock+Space",
                "scope": "app-override",
                "appId": "edge",
                "enabled": True,
                "safetyGate": "none",
            },
        )
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        out = dispatcher.dispatch_key_chord(ctx, "CapsLock+Space", press_count=1)
        self.assertTrue(out.result.ok)
        self.assertEqual(out.plan.command_id, "cmd.help.availableHotkeys")

    def test_profile_fallback_order_executes_palette(self) -> None:
        self.config.profiles["balanced"]["fallbackOrder"] = ["palette"]
        dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced")
        ctx = self._ctx("edge", "alpha", 0)

        out = dispatcher.dispatch_key_chord(ctx, "CapsLock+Y", press_count=1)
        self.assertTrue(out.result.ok)
        self.assertEqual(out.plan.command_id, "cmd.palette.open")
        self.assertTrue(out.result.payload["gesture"]["fallbackUsed"])

    def test_virtualized_scope_precedence_when_context_is_virtualized(self) -> None:
        self.config.keymap_bindings.insert(
            0,
            {
                "commandId": "cmd.help.availableHotkeys",
                "keyChord": "CapsLock+Q",
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

        out = dispatcher.dispatch_key_chord(ctx, "CapsLock+Q", press_count=1)
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

        focused = dispatcher.dispatch_command(ctx, "cmd.profile.hotkeyDiagnostics", keyChord="CapsLock+Space")
        self.assertTrue(focused.result.ok)
        self.assertIn("CapsLock+Space", focused.result.payload["resolutionTrace"])

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
            dispatcher = RuntimeDispatcher(self.runtime, self.config, profile_id="balanced", data_root=Path(tmpdir) / "spellforge")
            ctx = self._ctx("edge", "alpha", 0)

            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.create", name="inventory").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.select", name="inventory").result.ok)
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
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.entry.detail", entryId=eid).result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.search", field="name", query="item").result.ok)
            self.assertTrue(dispatcher.dispatch_command(ctx, "cmd.db.sort", field="name", descending=False).result.ok)

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
