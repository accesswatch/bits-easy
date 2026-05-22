from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .config import RuntimeConfig
from .clip_library import ClipLibraryStore
from .engine import AppContext, RuntimeResult, SpellforgeRuntime
from .health import IntegrationHealthTracker
from .shortcut_catalog import ShortcutCatalogStore
from .multipress import MultiPressResolver
from .pocketclips import PocketClipsStudio
from .portability import export_portability_bundle, import_portability_bundle
from .text_expansion import TextExpansionStore
from .shortcuts import ShortcutsStore
from .tagging import TaggingSession
from .table_capture import TableCaptureExtractor
from .hotkey_chains import HotkeyChainStore
from .outlook_tagging import OutlookTaggingSession
from .dialog_paths import DialogPathInserter
from .progress_cues import ProgressCueEngine
from .speech_history import SpeechHistory
from .symbols import SymbolAssistant
from .window_bookmarks import WindowBookmarks
from .system_report import SystemReportService
from .adaptive_actions import AdaptiveActionEngine
from .quick_capture import QuickCaptureInbox
from .operation_journal import OperationJournal
from .google_calendar_sync import GoogleCalendarSync
from .google_contacts_sync import GoogleContactsSync
from .time_diary import TimeDiaryService
from .tasks_calendar import TaskIcsBridge
from .contacts_social import ContactsSocialService
from .structured_records import StructuredRecordService
from .notes_workspace import NotesWorkspaceService
from .authoring_engine import AuthoringEngine
from .retrieval_layer import RetrievalLayer
from .backup_migration import BackupMigrationService
from .joplin_bridge import JoplinBridge
from .nvda_readiness import NvdaReadinessService
from .utility_ops import UtilityOpsService
from .missions_context import MissionsContextService
from .workflow_portability import WorkflowPortabilityService


@dataclass
class DispatchPlan:
    command_id: str
    confirmation: str
    preview: str
    safety_gate: str


@dataclass
class DispatchOutcome:
    plan: DispatchPlan
    result: RuntimeResult


class RuntimeDispatcher:
    def __init__(
        self,
        runtime: SpellforgeRuntime,
        config: RuntimeConfig,
        profile_id: str,
        data_root: Path | str | None = None,
    ):
        self.runtime = runtime
        self.config = config
        self.profile_id = profile_id
        self.multi_press_enabled_override: Optional[bool] = None
        base_dir = Path(data_root) if data_root is not None else (Path.home() / "AppData" / "Roaming" / "Spellforge")
        self._studio = PocketClipsStudio(runtime)
        self._health = IntegrationHealthTracker(base_dir / "integration-health.jsonl")
        self._expansions = TextExpansionStore(base_dir / "text-expansions.json")
        self._cuts = ShortcutCatalogStore(base_dir / "shortcut-catalog.json")
        self._library = ClipLibraryStore(runtime, base_dir / "clip-library.json")
        self._shortcuts = ShortcutsStore(base_dir / "shortcuts.json")
        self._tagging = TaggingSession()
        self._table_capture = TableCaptureExtractor()
        self._chains = HotkeyChainStore(base_dir / "hotkey-chains.json")
        self._outlook_tags = OutlookTaggingSession()
        self._dialog_paths = DialogPathInserter()
        self._progress = ProgressCueEngine()
        self._speech_history = SpeechHistory()
        self._symbols = SymbolAssistant()
        self._bookmarks = WindowBookmarks(base_dir / "window-bookmarks.json")
        self._system_report = SystemReportService()
        self._adaptive = AdaptiveActionEngine()
        self._capture = QuickCaptureInbox(base_dir / "quick-capture.json")
        self._journal = OperationJournal(base_dir / "operation-journal.json")
        self._google_calendar = GoogleCalendarSync(
            base_dir / "google-calendar-credentials.json",
            base_dir / "google-calendar-token.json",
        )
        self._google_contacts = GoogleContactsSync(
            base_dir / "google-contacts-credentials.json",
            base_dir / "google-contacts-token.json",
        )
        self._time_diary = TimeDiaryService(base_dir / "time-diary.json")
        self._tasks = TaskIcsBridge(
            base_dir / "tasks.json",
            calendar_sync=self._google_calendar,
        )
        self._contacts_social = ContactsSocialService(
            base_dir / "contacts-social.json",
            google_sync=self._google_contacts,
        )
        self._records = StructuredRecordService(base_dir / "structured-records.json")
        self._notes = NotesWorkspaceService(base_dir / "notes-workspace.json")
        self._author = AuthoringEngine()
        self._retrieval = RetrievalLayer(base_dir / "retrieval-memory.json")
        self._backup = BackupMigrationService(base_dir / "backup-config.json")
        self._joplin = JoplinBridge(base_dir / "joplin-bridge.json")
        self._nvda = NvdaReadinessService()
        self._utility_ops = UtilityOpsService(base_dir / "utility-ops.json")
        self._missions = MissionsContextService(base_dir / "missions.json")
        self._workflow_pack = WorkflowPortabilityService()
        self._latest_result: Dict[str, Any] = {
            "confidence": 0.0,
            "fallbacks": ["cmd.palette.open"],
            "summary": "",
        }
        self._last_action = ""

    def _rollback_action_for(self, command_id: str, kwargs: Dict[str, Any], result: RuntimeResult) -> Optional[Dict[str, Any]]:
        if command_id == "cmd.capture.quickInbox.route":
            payload = result.payload or {}
            capture_id = str(payload.get("captureId", "")).strip()
            previous_route = str(payload.get("previousRoute", "")).strip()
            if capture_id and previous_route:
                return {
                    "commandId": "cmd.capture.quickInbox.route",
                    "kwargs": {"captureId": capture_id, "target": previous_route},
                }

        if command_id == "cmd.tags.session.tag":
            path = str(kwargs.get("path", "")).strip()
            if path:
                return {"commandId": "cmd.tags.session.untag", "kwargs": {"path": path}}
        if command_id == "cmd.tags.session.untag":
            path = str(kwargs.get("path", "")).strip()
            if path:
                return {"commandId": "cmd.tags.session.tag", "kwargs": {"path": path}}

        if command_id == "cmd.tags.outlook.tag":
            message_id = str(kwargs.get("messageId", "")).strip()
            if message_id:
                return {"commandId": "cmd.tags.outlook.untag", "kwargs": {"messageId": message_id}}
        if command_id == "cmd.tags.outlook.untag":
            message_id = str(kwargs.get("messageId", "")).strip()
            sender = str(kwargs.get("sender", "")).strip()
            subject = str(kwargs.get("subject", "")).strip()
            if message_id:
                return {
                    "commandId": "cmd.tags.outlook.tag",
                    "kwargs": {"messageId": message_id, "sender": sender, "subject": subject},
                }

        if command_id == "cmd.shortcuts.launcher.add":
            shortcut_id = str(kwargs.get("shortcutId", "")).strip()
            if shortcut_id:
                return {"commandId": "cmd.shortcuts.launcher.remove", "kwargs": {"shortcutId": shortcut_id}}
        if command_id == "cmd.shortcuts.launcher.remove":
            shortcut_id = str(kwargs.get("shortcutId", "")).strip()
            if shortcut_id:
                return {"commandId": "cmd.shortcuts.launcher.add", "kwargs": {"shortcutId": shortcut_id}}

        if command_id == "cmd.shortcuts.drive.map":
            drive_letter = str(kwargs.get("driveLetter", "")).strip()
            if drive_letter:
                return {"commandId": "cmd.shortcuts.drive.unmap", "kwargs": {"driveLetter": drive_letter}}

        if command_id == "cmd.db.delete":
            db_name = str(kwargs.get("name", "")).strip()
            if db_name:
                return {"commandId": "cmd.db.restore", "kwargs": {"name": db_name}}

        return None

    def _resolve_confirmation(self, command_meta: Dict[str, Any], policy: Optional[Dict[str, Any]], safety_gate: str) -> str:
        if policy and policy.get("confirmation") and policy["confirmation"] != "inherit":
            return policy["confirmation"]

        if safety_gate == "always-confirm" or command_meta.get("requiresConfirmation", False):
            return "always"
        if safety_gate == "low-confidence-confirm":
            return "adaptive"
        return "inherit"

    def _resolve_preview(self, policy: Optional[Dict[str, Any]]) -> str:
        if policy and policy.get("preview"):
            return policy["preview"]
        return "inherit"

    def _plan_for_command(self, command_id: str) -> DispatchPlan:
        command_meta = self.config.command(command_id)
        if command_meta is None:
            return DispatchPlan(
                command_id=command_id,
                confirmation="inherit",
                preview="inherit",
                safety_gate="none",
            )

        binding = self.config.key_binding_for_command(command_id)
        safety_gate = "none" if binding is None else binding.get("safetyGate", "none")
        policy = self.config.profile_policy(self.profile_id, command_id)

        return DispatchPlan(
            command_id=command_id,
            confirmation=self._resolve_confirmation(command_meta, policy, safety_gate),
            preview=self._resolve_preview(policy),
            safety_gate=safety_gate,
        )

    def _bindings_for_context(self, context: AppContext) -> list[dict]:
        visible: list[dict] = []
        for binding in self.config.keymap_bindings:
            if not binding.get("enabled", True):
                continue
            scope = str(binding.get("scope", "global"))
            if scope not in ("global", "app-override"):
                continue
            app_id = binding.get("appId")
            if app_id not in (None, context.app_id):
                continue
            visible.append(binding)
        return visible

    def _mode_for_context(self, context: AppContext) -> str:
        control_id = (context.control_id or "").lower()
        if "virtual" in control_id:
            return "virtualized"
        return "global"

    def _fallback_for_unbound_chord(self, context: AppContext, key_chord: str) -> Optional[DispatchOutcome]:
        for fallback in self.config.profile_fallback_order(self.profile_id):
            if fallback == "binding":
                binding = self.config.key_binding_for_chord(key_chord)
                if binding is not None:
                    return self.dispatch_command(context, str(binding.get("commandId", "cmd.palette.open")))
            elif fallback == "palette":
                return self.dispatch_command(context, "cmd.palette.open")
            elif fallback == "none":
                continue
        return None

    def _hotkey_discoverability(self, context: AppContext) -> RuntimeResult:
        rows = []
        for binding in self._bindings_for_context(context):
            trig = binding.get("trigger") or {"kind": "single-press"}
            rows.append(
                {
                    "commandId": binding.get("commandId", ""),
                    "keyChord": binding.get("keyChord", ""),
                    "trigger": trig.get("kind", "single-press"),
                    "scope": binding.get("scope", "global"),
                    "appId": binding.get("appId"),
                }
            )
        rows.sort(key=lambda r: (r["keyChord"], r["trigger"], r["commandId"]))
        return RuntimeResult(
            ok=True,
            message=f"Available hotkeys for {context.app_id} ready.",
            payload={"hotkeys": rows, "count": len(rows), "appId": context.app_id},
        )

    def _hotkey_diagnostics(self, context: AppContext, *, key_chord: str = "") -> RuntimeResult:
        grouped: Dict[str, list[dict]] = {}
        for binding in self._bindings_for_context(context):
            key = f"{binding.get('keyChord','')}|{(binding.get('trigger') or {}).get('kind','single-press')}"
            grouped.setdefault(key, []).append(binding)

        collisions = []
        for key, items in grouped.items():
            if len(items) <= 1:
                continue
            chord, trig = key.split("|", 1)
            collisions.append(
                {
                    "keyChord": chord,
                    "trigger": trig,
                    "commands": [str(i.get("commandId", "")) for i in items],
                    "remediation": [
                        "Assign one command to a different key chord.",
                        "Move one command to palette-only execution.",
                        "Keep only one enabled binding for this trigger.",
                    ],
                }
            )

        unique_chords = sorted({str(b.get("keyChord", "")) for b in self._bindings_for_context(context) if str(b.get("keyChord", ""))})
        if key_chord.strip():
            trace_chords = [key_chord.strip()]
        else:
            trace_chords = unique_chords[:8]

        trace = {}
        mode = self._mode_for_context(context)
        for chord in trace_chords:
            rows = self.config.binding_resolution_trace(chord, context.app_id, mode)
            accepted = [r for r in rows if r.get("accepted")]
            accepted.sort(key=lambda r: (int(r.get("rank", 99)), int(r.get("index", 0))))
            chosen = accepted[0] if accepted else None
            trace[chord] = {
                "chosen": None if chosen is None else {
                    "commandId": chosen.get("commandId", ""),
                    "layer": chosen.get("layer", ""),
                    "rank": chosen.get("rank", 99),
                },
                "candidates": [
                    {
                        "commandId": r.get("commandId", ""),
                        "scope": r.get("scope", ""),
                        "appId": r.get("appId"),
                        "accepted": bool(r.get("accepted", False)),
                        "layer": r.get("layer", ""),
                        "rank": r.get("rank", 99),
                        "reason": r.get("reason", ""),
                    }
                    for r in rows
                ],
            }

        return RuntimeResult(
            ok=True,
            message="Hotkey diagnostics ready.",
            payload={
                "appId": context.app_id,
                "mode": mode,
                "bindingCount": len(self._bindings_for_context(context)),
                "collisionCount": len(collisions),
                "collisions": collisions,
                "precedence": [
                    "app-override(app match)",
                    "global(app-scoped)",
                    "virtualized(current mode)",
                    "global(shared)",
                ],
                "fallbackOrder": self.config.profile_fallback_order(self.profile_id),
                "resolutionTrace": trace,
            },
        )

    def dispatch_key_chord(
        self,
        context: AppContext,
        key_chord: str,
        *,
        press_count: int = 1,
        hold_duration_ms: int = 0,
        **kwargs: Any,
    ) -> DispatchOutcome:
        mode = self._mode_for_context(context)
        trace_rows = self.config.binding_resolution_trace(key_chord, context.app_id, mode)
        accepted = [r for r in trace_rows if r.get("accepted")]
        accepted.sort(key=lambda r: (int(r.get("rank", 99)), int(r.get("index", 0))))
        layered = [self.config.keymap_bindings[int(r.get("index", 0))] for r in accepted]
        resolver = MultiPressResolver(layered)
        profile_enabled = self.config.profile_multi_press_enabled(self.profile_id)
        multi_press_enabled = profile_enabled if self.multi_press_enabled_override is None else bool(self.multi_press_enabled_override)
        resolved = resolver.resolve(
            key_chord,
            press_count,
            hold_duration_ms=hold_duration_ms,
            multi_press_enabled=multi_press_enabled,
        )
        if resolved is None:
            fallback = self._fallback_for_unbound_chord(context, key_chord)
            if fallback is not None:
                if fallback.result.payload is None:
                    fallback.result.payload = {}
                fallback.result.payload["gesture"] = {
                    "triggerKind": "single-press",
                    "pressCount": press_count,
                    "fallbackUsed": True,
                    "reason": "profile-fallback-order",
                    "announcement": "Fallback route executed based on profile ordering.",
                }
                return fallback

            return DispatchOutcome(
                plan=DispatchPlan(
                    command_id="cmd.none",
                    confirmation="inherit",
                    preview="inherit",
                    safety_gate="none",
                ),
                result=RuntimeResult(
                    ok=False,
                    message=f"No active command is bound to key chord {key_chord}.",
                ),
            )

        out = self.dispatch_command(context, resolved.matched_command_id, **kwargs)
        if out.result.payload is None:
            out.result.payload = {}
        chosen_row = next((r for r in accepted if str(r.get("commandId", "")) == resolved.matched_command_id), accepted[0] if accepted else None)
        out.result.payload["gesture"] = {
            "triggerKind": resolved.trigger_kind,
            "pressCount": resolved.used_press_count,
            "fallbackUsed": resolved.fallback_used,
            "reason": resolved.reason,
            "announcement": resolved.announcement,
            "chosenLayer": None if chosen_row is None else chosen_row.get("layer", ""),
            "rejectedCandidates": [
                {
                    "commandId": r.get("commandId", ""),
                    "reason": r.get("reason", ""),
                    "scope": r.get("scope", ""),
                }
                for r in trace_rows
                if not r.get("accepted")
            ],
        }
        return out

    def dispatch_command(self, context: AppContext, command_id: str, **kwargs: Any) -> DispatchOutcome:
        plan = self._plan_for_command(command_id)

        if command_id == "cmd.selection.markStart":
            result = self.runtime.mark_selection_start(context)
        elif command_id == "cmd.palette.open":
            result = RuntimeResult(ok=True, message="Command palette opened.")
        elif command_id == "cmd.selection.summarize":
            source = context.clipboard_text.strip() or context.buffer.strip()
            result = self._adaptive.summarize(source)
            if result.ok:
                self._latest_result = {
                    "confidence": float((result.payload or {}).get("confidence", 0.0)),
                    "fallbacks": list((result.payload or {}).get("fallbacks", ["cmd.palette.open"])),
                    "summary": str((result.payload or {}).get("content", "")),
                }
        elif command_id == "cmd.selection.extractActions":
            source = context.clipboard_text.strip() or context.buffer.strip()
            result = self._adaptive.extract_actions(source)
            if result.ok:
                items = list((result.payload or {}).get("items", []))
                self._latest_result = {
                    "confidence": float((result.payload or {}).get("confidence", 0.0)),
                    "fallbacks": list((result.payload or {}).get("fallbacks", ["cmd.palette.open"])),
                    "summary": "; ".join(str(x) for x in items[:3]),
                }
        elif command_id == "cmd.selection.rewriteBeginner":
            source = context.clipboard_text.strip() or context.buffer.strip()
            result = self._adaptive.rewrite_beginner(source)
            if result.ok:
                self._latest_result = {
                    "confidence": float((result.payload or {}).get("confidence", 0.0)),
                    "fallbacks": list((result.payload or {}).get("fallbacks", ["cmd.palette.open"])),
                    "summary": str((result.payload or {}).get("content", ""))[:120],
                }
        elif command_id == "cmd.capture.quickInbox":
            text = context.clipboard_text.strip() or context.buffer.strip()
            result = self._capture.capture(text, source_app=context.app_id, window_id=context.window_id)
        elif command_id == "cmd.capture.quickInbox.route":
            result = self._capture.route(
                str(kwargs.get("captureId", "")),
                str(kwargs.get("target", "")),
            )
        elif command_id == "cmd.capture.quickInbox.list":
            result = self._capture.list_items(route=str(kwargs.get("route", "")))
        elif command_id == "cmd.journal.list":
            result = self._journal.list_entries(
                app_id=str(kwargs.get("appId", "")),
                action_type=str(kwargs.get("actionType", "")),
            )
        elif command_id == "cmd.journal.rollback":
            entry_id = str(kwargs.get("entryId", ""))
            prep = self._journal.rollback(entry_id)
            if not prep.ok:
                result = prep
            else:
                rollback_action = ((prep.payload or {}).get("rollbackAction") or {})
                rollback_command = str(rollback_action.get("commandId", ""))
                rollback_kwargs = rollback_action.get("kwargs", {})
                if not rollback_command:
                    result = RuntimeResult(ok=False, message="Rollback handler is missing command metadata.")
                else:
                    rollback_outcome = self.dispatch_command(
                        context,
                        rollback_command,
                        __skipJournal=True,
                        **(rollback_kwargs if isinstance(rollback_kwargs, dict) else {}),
                    )
                    self._journal.mark_rollback_applied(entry_id, success=rollback_outcome.result.ok)
                    result = RuntimeResult(
                        ok=rollback_outcome.result.ok,
                        message=(
                            "Rollback executed successfully."
                            if rollback_outcome.result.ok
                            else f"Rollback failed: {rollback_outcome.result.message}"
                        ),
                        payload={
                            "entryId": entry_id,
                            "rollbackCommandId": rollback_command,
                            "rollbackResult": rollback_outcome.result.payload or {},
                        },
                    )
        elif command_id == "cmd.time.speak":
            result = self._time_diary.speak_time(include_seconds=False)
        elif command_id == "cmd.time.speakSeconds":
            result = self._time_diary.speak_time(include_seconds=True)
        elif command_id == "cmd.time.insert":
            result = self._time_diary.insert_time(include_seconds=bool(kwargs.get("includeSeconds", False)))
        elif command_id == "cmd.date.insert":
            result = self._time_diary.insert_date()
        elif command_id == "cmd.time.stopwatch.start":
            result = self._time_diary.stopwatch_start()
        elif command_id == "cmd.time.stopwatch.stop":
            result = self._time_diary.stopwatch_stop()
        elif command_id == "cmd.time.stopwatch.clear":
            result = self._time_diary.stopwatch_clear()
        elif command_id == "cmd.time.stopwatch.elapsed":
            result = self._time_diary.stopwatch_elapsed()
        elif command_id == "cmd.time.stopwatch.setPrecision":
            result = self._time_diary.stopwatch_set_precision(int(kwargs.get("decimals", 1)))
        elif command_id == "cmd.time.countdown.start":
            result = self._time_diary.countdown_start(int(kwargs.get("minutes", 1)))
        elif command_id == "cmd.time.countdown.status":
            result = self._time_diary.countdown_status()
        elif command_id == "cmd.time.countdown.stop":
            result = self._time_diary.countdown_stop()
        elif command_id == "cmd.time.alarm.set":
            result = self._time_diary.alarm_set(str(kwargs.get("at", "")))
        elif command_id == "cmd.time.alarm.cancel":
            result = self._time_diary.alarm_cancel()
        elif command_id == "cmd.time.alarm.status":
            result = self._time_diary.alarm_status()
        elif command_id == "cmd.time.monitor.start":
            result = self._time_diary.monitor_start(braille_mode=bool(kwargs.get("brailleMode", False)))
        elif command_id == "cmd.time.monitor.stop":
            result = self._time_diary.monitor_stop()
        elif command_id == "cmd.time.monitor.status":
            result = self._time_diary.monitor_status()
        elif command_id == "cmd.diary.create":
            result = self._time_diary.appointment_create(
                str(kwargs.get("title", "")),
                str(kwargs.get("startsAt", "")),
                notes=str(kwargs.get("notes", "")),
            )
        elif command_id == "cmd.diary.listMonth":
            result = self._time_diary.appointment_list_month(
                int(kwargs.get("year", 1970)),
                int(kwargs.get("month", 1)),
            )
        elif command_id == "cmd.date.dayOfWeek":
            result = self._time_diary.day_of_week(str(kwargs.get("date", "")))
        elif command_id == "cmd.date.addDays":
            result = self._time_diary.date_add_days(str(kwargs.get("date", "")), int(kwargs.get("days", 0)))
        elif command_id == "cmd.tasks.create":
            result = self._tasks.create_task(
                str(kwargs.get("title", "")),
                str(kwargs.get("dueAt", "")),
                category=str(kwargs.get("category", "general")),
                priority=str(kwargs.get("priority", "normal")),
            )
        elif command_id == "cmd.tasks.complete":
            result = self._tasks.complete_task(str(kwargs.get("taskId", "")))
        elif command_id == "cmd.tasks.list":
            result = self._tasks.list_tasks(
                status=str(kwargs.get("status", "")),
                category=str(kwargs.get("category", "")),
                priority=str(kwargs.get("priority", "")),
            )
        elif command_id == "cmd.tasks.exportIcs":
            result = self._tasks.export_ics(Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "tasks.ics"))))
        elif command_id == "cmd.tasks.syncGoogleCalendar":
            result = self._tasks.sync_to_google_calendar(dry_run=bool(kwargs.get("dryRun", True)))
        elif command_id == "cmd.contacts.create":
            result = self._contacts_social.create_contact(
                str(kwargs.get("name", "")),
                str(kwargs.get("email", "")),
                str(kwargs.get("phone", "")),
            )
        elif command_id == "cmd.contacts.search":
            result = self._contacts_social.search_contacts(str(kwargs.get("query", "")))
        elif command_id == "cmd.contacts.insertField":
            result = self._contacts_social.insert_field(
                str(kwargs.get("contactId", "")),
                str(kwargs.get("field", "")),
            )
        elif command_id == "cmd.contacts.copyField":
            result = self._contacts_social.copy_field(
                str(kwargs.get("contactId", "")),
                str(kwargs.get("field", "")),
            )
        elif command_id == "cmd.contacts.syncGoogle":
            result = self._contacts_social.sync_google_contacts(dry_run=bool(kwargs.get("dryRun", True)))
        elif command_id == "cmd.mail.extractSender":
            result = self._contacts_social.mail_extract_sender(
                str(kwargs.get("name", "")),
                str(kwargs.get("email", "")),
            )
        elif command_id == "cmd.mail.attachments.action":
            result = self._contacts_social.mail_attachment_actions(
                [str(x) for x in list(kwargs.get("attachments", []))],
                str(kwargs.get("action", "list")),
            )
        elif command_id == "cmd.whatsapp.recent":
            result = self._contacts_social.whatsapp_recent(
                str(kwargs.get("chatId", "")),
                [str(x) for x in list(kwargs.get("messages", []))],
            )
        elif command_id == "cmd.whatsapp.voice":
            result = self._contacts_social.whatsapp_voice_control(str(kwargs.get("mode", "record")))
        elif command_id == "cmd.x.timeline":
            result = self._contacts_social.x_timeline(
                [str(x) for x in list(kwargs.get("items", []))],
                int(kwargs.get("cursor", 0)),
            )
        elif command_id == "cmd.social.orbit.summary":
            result = self._contacts_social.social_orbit_summary(
                {
                    str(k): [str(x) for x in list(v)]
                    for k, v in dict(kwargs.get("accountItems", {})).items()
                }
            )
        elif command_id == "cmd.social.nickname.upsert":
            result = self._contacts_social.nickname_upsert(
                str(kwargs.get("source", "")),
                str(kwargs.get("nickname", "")),
            )
        elif command_id == "cmd.social.nickname.replace":
            result = self._contacts_social.nickname_replace(str(kwargs.get("text", "")))
        elif command_id == "cmd.social.notifications.set":
            result = self._contacts_social.notification_set(
                str(kwargs.get("channel", "")),
                enabled=bool(kwargs.get("enabled", True)),
                mentions_only=bool(kwargs.get("mentionsOnly", False)),
            )
        elif command_id == "cmd.db.create":
            result = self._records.create_database(str(kwargs.get("name", "")))
        elif command_id == "cmd.db.select":
            result = self._records.select_database(str(kwargs.get("name", "")))
        elif command_id == "cmd.db.delete":
            result = self._records.delete_database(
                str(kwargs.get("name", "")),
                confirm=bool(kwargs.get("confirm", False)),
            )
        elif command_id == "cmd.db.restore":
            result = self._records.restore_database(str(kwargs.get("name", "")))
        elif command_id == "cmd.db.field.define":
            result = self._records.define_field(
                str(kwargs.get("name", "")),
                field_type=str(kwargs.get("fieldType", "text")),
                required=bool(kwargs.get("required", False)),
                help_text=str(kwargs.get("helpText", "")),
                validator=str(kwargs.get("validator", "")),
                choices=[str(x) for x in list(kwargs.get("choices", []))],
            )
        elif command_id == "cmd.db.entry.add":
            result = self._records.add_entry(dict(kwargs.get("values", {})))
        elif command_id == "cmd.db.entry.edit":
            result = self._records.edit_entry(
                str(kwargs.get("entryId", "")),
                dict(kwargs.get("values", {})),
            )
        elif command_id == "cmd.db.entry.delete":
            result = self._records.delete_entry(
                str(kwargs.get("entryId", "")),
                confirm=bool(kwargs.get("confirm", False)),
            )
        elif command_id == "cmd.db.entry.list":
            result = self._records.list_entries(columns=[str(x) for x in list(kwargs.get("columns", []))] or None)
        elif command_id == "cmd.db.entry.detail":
            result = self._records.entry_detail(str(kwargs.get("entryId", "")))
        elif command_id == "cmd.db.search":
            result = self._records.search_entries(
                str(kwargs.get("field", "")),
                str(kwargs.get("query", "")),
            )
        elif command_id == "cmd.db.sort":
            result = self._records.sort_entries(
                str(kwargs.get("field", "")),
                descending=bool(kwargs.get("descending", False)),
            )
        elif command_id == "cmd.db.export.csv":
            result = self._records.export_csv(Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "records.csv"))))
        elif command_id == "cmd.db.export.text":
            result = self._records.export_text(Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "records.txt"))))
        elif command_id == "cmd.jamal.import":
            result = self._records.jamal_import(
                Path(str(kwargs.get("inPath", ""))),
                database_name=str(kwargs.get("database", "")),
            )
        elif command_id == "cmd.jamal.export":
            result = self._records.jamal_export(Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "jamal-export.json"))))
        elif command_id == "cmd.jamal.launch":
            result = self._records.jamal_launch(Path(str(kwargs.get("datasetPath", Path.cwd() / "dist" / "jamal-export.json"))))
        elif command_id == "cmd.jamal.return":
            result = self._records.jamal_return()
        elif command_id == "cmd.jamal.sync":
            result = self._records.jamal_sync(
                [dict(x) for x in list(kwargs.get("incomingEntries", []))],
                apply=bool(kwargs.get("apply", False)),
            )
        elif command_id == "cmd.notes.quickCapture":
            result = self._notes.quick_note(str(kwargs.get("text", "")), context.app_id)
        elif command_id == "cmd.notes.mode.set":
            result = self._notes.set_mode(str(kwargs.get("mode", "simple")))
        elif command_id == "cmd.notes.category.create":
            result = self._notes.category_create(
                str(kwargs.get("category", "")),
                parent=str(kwargs.get("parent", "")),
            )
        elif command_id == "cmd.notes.category.move":
            result = self._notes.category_move(
                str(kwargs.get("category", "")),
                new_parent=str(kwargs.get("parent", "")),
            )
        elif command_id == "cmd.notes.relate":
            result = self._notes.relate_notes(
                str(kwargs.get("noteA", "")),
                str(kwargs.get("noteB", "")),
            )
        elif command_id == "cmd.notes.attachment.add":
            result = self._notes.attachment_add(
                str(kwargs.get("noteId", "")),
                str(kwargs.get("path", "")),
            )
        elif command_id == "cmd.notes.field.set":
            result = self._notes.field_set(
                str(kwargs.get("noteId", "")),
                str(kwargs.get("key", "")),
                str(kwargs.get("value", "")),
            )
        elif command_id == "cmd.notes.help.set":
            result = self._notes.help_set(
                str(kwargs.get("text", "")),
                app_id=str(kwargs.get("appId", "")),
                domain=str(kwargs.get("domain", "")),
                page=str(kwargs.get("page", "")),
            )
        elif command_id == "cmd.notes.help.resolve":
            result = self._notes.help_resolve(
                app_id=str(kwargs.get("appId", context.app_id)),
                domain=str(kwargs.get("domain", "")),
                page=str(kwargs.get("page", "")),
            )
        elif command_id == "cmd.notes.snapshot.create":
            result = self._notes.snapshot_create(str(kwargs.get("reason", "manual")))
        elif command_id == "cmd.notes.snapshot.restore":
            result = self._notes.snapshot_restore(int(kwargs.get("index", -1)))
        elif command_id == "cmd.author.markdown.insert":
            result = self._author.markdown_insert(
                str(kwargs.get("kind", "")),
                str(kwargs.get("text", "")),
            )
        elif command_id == "cmd.author.html.semantic":
            result = self._author.html_semantic(
                str(kwargs.get("title", "")),
                [str(x) for x in list(kwargs.get("items", []))],
            )
        elif command_id == "cmd.author.html.validate":
            result = self._author.html_validate(str(kwargs.get("html", "")))
        elif command_id == "cmd.author.export.html":
            result = self._author.export_html(
                str(kwargs.get("markdown", "")),
                Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "author-export.html"))),
            )
        elif command_id == "cmd.author.export.word":
            result = self._author.export_word_stub(
                str(kwargs.get("markdown", "")),
                Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "author-export.docx"))),
            )
        elif command_id == "cmd.author.a11y.lint":
            result = self._author.accessibility_lint(str(kwargs.get("markdown", "")))
        elif command_id == "cmd.author.a11y.fixPreview":
            result = self._author.accessibility_fix_preview(str(kwargs.get("markdown", "")))
        elif command_id == "cmd.retrieve.query":
            result = self._retrieval.query(
                str(kwargs.get("query", "")),
                provider_order=[str(x) for x in list(kwargs.get("providerOrder", []))] or None,
            )
        elif command_id == "cmd.retrieve.revisit":
            idx = kwargs.get("index")
            result = self._retrieval.revisit(
                index=None if idx is None else int(idx),
                reset_visited=bool(kwargs.get("resetVisited", False)),
            )
        elif command_id == "cmd.retrieve.parse":
            result = self._retrieval.parse_resilient(str(kwargs.get("raw", "")))
        elif command_id == "cmd.retrieve.summarize":
            result = self._retrieval.summarize_actions([dict(x) for x in list(kwargs.get("results", []))])
        elif command_id == "cmd.backup.target.set":
            result = self._backup.set_target(str(kwargs.get("path", "")))
        elif command_id == "cmd.backup.source.add":
            result = self._backup.add_source(str(kwargs.get("path", "")))
        elif command_id == "cmd.backup.settings.create":
            result = self._backup.backup_settings(
                dict(kwargs.get("files", {})),
                Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "settings-backup.json"))),
            )
        elif command_id == "cmd.backup.settings.restore":
            result = self._backup.restore_settings(Path(str(kwargs.get("inPath", ""))))
        elif command_id == "cmd.backup.selected.run":
            result = self._backup.backup_selected(
                [str(x) for x in list(kwargs.get("selectedPaths", []))],
                Path(str(kwargs.get("outDir", Path.cwd() / "dist" / "selected-backup"))),
            )
        elif command_id == "cmd.backup.migrate":
            result = self._backup.migrate_profile(
                Path(str(kwargs.get("fromDir", ""))),
                Path(str(kwargs.get("toDir", ""))),
                dry_run=bool(kwargs.get("dryRun", False)),
            )
        elif command_id == "cmd.joplin.import":
            result = self._joplin.import_notes(Path(str(kwargs.get("inPath", ""))))
        elif command_id == "cmd.joplin.export":
            result = self._joplin.export_notes(
                [dict(x) for x in list(kwargs.get("notes", []))],
                Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "joplin-export.json"))),
            )
        elif command_id == "cmd.joplin.mapping.set":
            result = self._joplin.set_mapping_profile(
                dict(kwargs.get("tagMap", {})),
                dict(kwargs.get("attachmentMap", {})),
            )
        elif command_id == "cmd.joplin.refresh":
            result = self._joplin.refresh_linked(
                [dict(x) for x in list(kwargs.get("incomingNotes", []))],
                apply=bool(kwargs.get("apply", False)),
            )
        elif command_id == "cmd.joplin.refresh.rollback":
            result = self._joplin.rollback_refresh()
        elif command_id == "cmd.nvda.readiness.baseline":
            result = self._nvda.baseline()
        elif command_id == "cmd.nvda.readiness.api":
            result = self._nvda.api_break_checklist()
        elif command_id == "cmd.nvda.readiness.security":
            result = self._nvda.security_alignment()
        elif command_id == "cmd.utility.notifications.import":
            result = self._utility_ops.import_rules(
                dict(kwargs.get("rules", {})),
                confirm=bool(kwargs.get("confirm", False)),
            )
        elif command_id == "cmd.utility.notifications.restore":
            result = self._utility_ops.restore_rules()
        elif command_id == "cmd.utility.audio.split":
            result = self._utility_ops.audio_split(
                int(kwargs.get("speechPan", -80)),
                int(kwargs.get("appPan", 80)),
            )
        elif command_id == "cmd.utility.audio.restoreBalance":
            result = self._utility_ops.audio_restore_balance()
        elif command_id == "cmd.utility.audio.cycleCard":
            result = self._utility_ops.audio_cycle_card()
        elif command_id == "cmd.context.whereAmI":
            result = self._missions.where_am_i(
                context,
                self._last_action,
                self._mode_for_context(context),
            )
        elif command_id == "cmd.missions.start":
            result = self._missions.missions_start(str(kwargs.get("profileId", self.profile_id)))
        elif command_id == "cmd.missions.complete":
            result = self._missions.missions_complete(
                str(kwargs.get("profileId", self.profile_id)),
                str(kwargs.get("missionId", "")),
            )
        elif command_id == "cmd.missions.status":
            result = self._missions.missions_status(str(kwargs.get("profileId", self.profile_id)))
        elif command_id == "cmd.workflow.pack.export":
            result = self._workflow_pack.export_pack(
                dict(kwargs.get("pack", {})),
                Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "workflow-pack.json"))),
            )
        elif command_id == "cmd.workflow.pack.import":
            result = self._workflow_pack.import_pack(
                Path(str(kwargs.get("inPath", ""))),
                reject_on_conflict=bool(kwargs.get("rejectOnConflict", True)),
            )
        elif command_id == "cmd.selection.markEnd":
            result = self.runtime.mark_selection_end(context)
        elif command_id == "cmd.selection.readContext":
            result = self.runtime.read_selection_context(context)
        elif command_id == "cmd.selection.jumpStart":
            result = self.runtime.jump_selection_start(context)
        elif command_id == "cmd.selection.cancel":
            result = self.runtime.cancel_selection(context)
        elif command_id == "cmd.context.returnSource":
            result = self.runtime.restore_source_anchor(context)
        elif command_id == "cmd.clip.copyToSlot":
            slot = int(kwargs.get("slot", 1))
            result = self.runtime.copy_to_slot(context, slot=slot, text=kwargs.get("text"))
        elif command_id == "cmd.clip.pasteFromSlot":
            slot = int(kwargs.get("slot", 1))
            result = self.runtime.paste_from_slot(slot=slot)
        elif command_id == "cmd.clip.protectSlot":
            slot = int(kwargs.get("slot", 1))
            result = self.runtime.protect_slot(slot=slot)
        elif command_id == "cmd.clip.unprotectSlot":
            slot = int(kwargs.get("slot", 1))
            result = self.runtime.unprotect_slot(slot=slot)
        elif command_id == "cmd.clip.deleteSlot":
            slot = int(kwargs.get("slot", 1))
            result = self.runtime.delete_slot(slot=slot)
        elif command_id == "cmd.clip.editSlot":
            slot = int(kwargs.get("slot", 1))
            content = str(kwargs.get("content", ""))
            result = self.runtime.edit_slot(slot=slot, content=content)
        elif command_id == "cmd.clip.describeSlot":
            slot = int(kwargs.get("slot", 1))
            result = self.runtime.describe_slot(slot=slot)
        elif command_id == "cmd.merge.setModeAppend":
            result = self.runtime.set_merge_mode_append()
        elif command_id == "cmd.merge.setModeReplace":
            result = self.runtime.set_merge_mode_replace()
        elif command_id == "cmd.merge.setDividerLine":
            result = self.runtime.set_merge_divider_line()
        elif command_id == "cmd.merge.setDividerSpace":
            result = self.runtime.set_merge_divider_space()
        elif command_id == "cmd.merge.setDividerParagraph":
            result = self.runtime.set_merge_divider_paragraph()
        elif command_id == "cmd.merge.setCustomSeparator":
            separator = str(kwargs.get("separator", "\n"))
            result = self.runtime.set_merge_custom_separator(separator)
        elif command_id == "cmd.merge.toggleClearOnPaste":
            result = self.runtime.toggle_clear_on_paste()
        elif command_id == "cmd.merge.applyProfile":
            profile = str(kwargs.get("profile", "meeting")).lower()
            if profile == "email":
                self.runtime.set_merge_mode_append()
                self.runtime.set_merge_divider_paragraph()
                self.runtime.set_clear_on_paste(False)
            elif profile == "research":
                self.runtime.set_merge_mode_append()
                self.runtime.set_merge_divider_line()
                self.runtime.set_clear_on_paste(False)
            else:
                self.runtime.set_merge_mode_replace()
                self.runtime.set_merge_divider_space()
                self.runtime.set_clear_on_paste(True)
            result = RuntimeResult(ok=True, message="Merge profile applied.", payload={"profile": profile})
        elif command_id == "cmd.merge.commit":
            result = self.runtime.merge_commit()
        elif command_id == "cmd.text.expansion.upsert":
            result = self._expansions.upsert(
                abbreviation=str(kwargs.get("abbreviation", "")),
                content=str(kwargs.get("content", "")),
                title=kwargs.get("title"),
                overwrite=bool(kwargs.get("overwrite", False)),
            )
        elif command_id == "cmd.text.expansion.expand":
            result = self._expansions.expand(str(kwargs.get("abbreviation", "")))
        elif command_id == "cmd.text.expansion.list":
            result = self._expansions.list_entries()
        elif command_id == "cmd.text.expansion.rename":
            result = self._expansions.rename(
                abbreviation=str(kwargs.get("abbreviation", "")),
                new_title=str(kwargs.get("title", "")),
            )
        elif command_id == "cmd.text.expansion.delete":
            result = self._expansions.delete(str(kwargs.get("abbreviation", "")))
        elif command_id == "cmd.text.expansion.setPrimary":
            result = self._expansions.set_primary(str(kwargs.get("abbreviation", "")))
        elif command_id == "cmd.text.quickInsert":
            result = self._expansions.quick_insert()
        elif command_id == "cmd.clip.browser.open":
            rows = self._studio.list_slots(sort_by=str(kwargs.get("sortBy", "slot")))
            result = RuntimeResult(
                ok=True,
                message="PocketClips browser opened.",
                payload={"slots": [r.__dict__ for r in rows]},
            )
        elif command_id == "cmd.clip.browser.filter":
            rows = self._studio.list_slots(
                source_app=str(kwargs.get("sourceApp", "")),
                only_protected=kwargs.get("onlyProtected"),
                sort_by=str(kwargs.get("sortBy", "slot")),
            )
            result = RuntimeResult(ok=True, message="PocketClips filter applied.", payload={"slots": [r.__dict__ for r in rows]})
        elif command_id == "cmd.clip.browser.sort":
            rows = self._studio.list_slots(sort_by=str(kwargs.get("sortBy", "slot")))
            result = RuntimeResult(ok=True, message="PocketClips sort applied.", payload={"slots": [r.__dict__ for r in rows]})
        elif command_id == "cmd.clip.browser.batchAction":
            result = self._studio.batch_action(slots=list(kwargs.get("slots", [])), action=str(kwargs.get("action", "")))
        elif command_id == "cmd.clip.browser.compare":
            result = self._studio.compare_slots(int(kwargs.get("slotA", 1)), int(kwargs.get("slotB", 2)))
        elif command_id == "cmd.clip.browser.reorder":
            result = self._studio.reorder_slot(
                from_slot=int(kwargs.get("fromSlot", 1)),
                to_slot=int(kwargs.get("toSlot", 2)),
                overwrite=bool(kwargs.get("overwrite", False)),
            )
        elif command_id == "cmd.clip.browser.split":
            result = self._studio.split_slot(
                slot=int(kwargs.get("slot", 1)),
                separator=str(kwargs.get("separator", "\n")),
            )
        elif command_id == "cmd.clip.browser.merge":
            result = self._studio.merge_slots(
                slot_a=int(kwargs.get("slotA", 1)),
                slot_b=int(kwargs.get("slotB", 2)),
                separator=str(kwargs.get("separator", "\n")),
            )
        elif command_id == "cmd.clip.browser.exportPack":
            out_path = Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "slot-pack.json")))
            result = self._studio.export_pack(slots=list(kwargs.get("slots", [1])), out_path=out_path)
        elif command_id == "cmd.clip.browser.importPack":
            in_path = Path(str(kwargs.get("inPath", "")))
            result = self._studio.import_pack(in_path=in_path, overwrite=bool(kwargs.get("overwrite", False)))
        elif command_id == "cmd.profile.portabilityBackup":
            out_path = Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "spellforge-portability.json")))
            out = export_portability_bundle(Path.cwd(), out_path)
            result = RuntimeResult(ok=True, message="Portability bundle exported.", payload={"path": str(out)})
        elif command_id == "cmd.profile.portabilityRestore":
            in_path = Path(str(kwargs.get("inPath", "")))
            try:
                restored = import_portability_bundle(
                    Path.cwd(),
                    in_path,
                    overwrite_existing=bool(kwargs.get("overwriteExisting", False)),
                )
                result = RuntimeResult(ok=True, message="Portability bundle restored.", payload={"restored": restored})
            except Exception as exc:
                result = RuntimeResult(ok=False, message=f"Portability restore failed: {exc}")
        elif command_id == "cmd.profile.integrationHealth":
            report = self._health.report()
            result = RuntimeResult(
                ok=True,
                message="Integration health report ready.",
                payload={
                    "totalCommands": report.total_commands,
                    "successCount": report.success_count,
                    "failureCount": report.failure_count,
                    "successRate": report.success_rate,
                    "byApp": report.by_app,
                    "topFailures": report.top_failures,
                },
            )
        elif command_id == "cmd.help.availableHotkeys":
            result = self._hotkey_discoverability(context)
        elif command_id == "cmd.profile.hotkeyDiagnostics":
            result = self._hotkey_diagnostics(context, key_chord=str(kwargs.get("keyChord", "")))
        elif command_id == "cmd.result.readConfidence":
            conf = float(self._latest_result.get("confidence", 0.0))
            mode = "high" if conf >= 0.8 else "low"
            result = RuntimeResult(
                ok=True,
                message="Confidence summary ready.",
                payload={
                    "confidence": conf,
                    "mode": mode,
                    "summary": str(self._latest_result.get("summary", "")),
                },
            )
        elif command_id == "cmd.result.openFallbacks":
            result = RuntimeResult(
                ok=True,
                message="Fallback options ready.",
                payload={"fallbackCommandIds": list(self._latest_result.get("fallbacks", ["cmd.palette.open"]))},
            )
        elif command_id == "cmd.shortcuts.create":
            result = self._shortcuts.create_shortcut(
                name=str(kwargs.get("name", "")),
                target=str(kwargs.get("target", "")),
                target_type=str(kwargs.get("targetType", "file")),
            )
        elif command_id == "cmd.shortcuts.list":
            result = self._shortcuts.list_shortcuts(
                target_type=str(kwargs.get("targetType", "")),
                category=str(kwargs.get("category", "")),
            )
        elif command_id == "cmd.shortcuts.assignCategory":
            result = self._shortcuts.assign_category(
                shortcut_id=str(kwargs.get("shortcutId", "")),
                category=str(kwargs.get("category", "general")),
            )
        elif command_id == "cmd.shortcuts.createPreset":
            result = self._shortcuts.create_preset(
                preset_name=str(kwargs.get("preset", "")),
                shortcut_ids=[str(x) for x in list(kwargs.get("shortcutIds", []))],
            )
        elif command_id == "cmd.shortcuts.runPreset":
            result = self._shortcuts.run_preset(str(kwargs.get("preset", "")))
        elif command_id == "cmd.shortcuts.launcher.open":
            result = self._shortcuts.list_launcher()
        elif command_id == "cmd.shortcuts.launcher.add":
            result = self._shortcuts.add_to_launcher(str(kwargs.get("shortcutId", "")))
        elif command_id == "cmd.shortcuts.launcher.addFocusedApp":
            result = self._shortcuts.add_focused_app(context.app_id)
        elif command_id == "cmd.shortcuts.launcher.remove":
            result = self._shortcuts.remove_from_launcher(str(kwargs.get("shortcutId", "")))
        elif command_id == "cmd.shortcuts.launcher.restoreDefaults":
            result = self._shortcuts.restore_launcher_defaults()
        elif command_id == "cmd.shortcuts.drive.map":
            result = self._shortcuts.map_drive(
                drive_letter=str(kwargs.get("driveLetter", "")),
                folder_path=str(kwargs.get("folderPath", "")),
            )
        elif command_id == "cmd.shortcuts.drive.unmap":
            result = self._shortcuts.unmap_drive(str(kwargs.get("driveLetter", "")))
        elif command_id == "cmd.shortcuts.drive.list":
            result = self._shortcuts.list_drive_mappings()
        elif command_id == "cmd.tags.session.tag":
            result = self._tagging.tag(str(kwargs.get("path", "")))
        elif command_id == "cmd.tags.session.untag":
            result = self._tagging.untag(str(kwargs.get("path", "")))
        elif command_id == "cmd.tags.session.report":
            result = self._tagging.report()
        elif command_id == "cmd.tags.session.count":
            result = self._tagging.count()
        elif command_id == "cmd.tags.session.cancel":
            result = self._tagging.cancel()
        elif command_id == "cmd.tags.session.batchCopy":
            result = self._tagging.batch_action("copy", target=str(kwargs.get("target", "")))
        elif command_id == "cmd.tags.session.batchCut":
            result = self._tagging.batch_action("cut", target=str(kwargs.get("target", "")))
        elif command_id == "cmd.tags.session.batchDelete":
            result = self._tagging.batch_action("delete")
        elif command_id == "cmd.tags.session.batchPlaylistAdd":
            result = self._tagging.batch_action("playlist-add", target=str(kwargs.get("playlist", "")))
        elif command_id == "cmd.tags.outlook.tag":
            result = self._outlook_tags.tag_message(
                message_id=str(kwargs.get("messageId", "")),
                sender=str(kwargs.get("sender", "")),
                subject=str(kwargs.get("subject", "")),
            )
        elif command_id == "cmd.tags.outlook.untag":
            result = self._outlook_tags.untag_message(str(kwargs.get("messageId", "")))
        elif command_id == "cmd.tags.outlook.report":
            result = self._outlook_tags.report()
        elif command_id == "cmd.tags.outlook.cancel":
            result = self._outlook_tags.cancel()
        elif command_id == "cmd.tags.outlook.batchMove":
            result = self._outlook_tags.batch_action("move", folder=str(kwargs.get("folder", "")))
        elif command_id == "cmd.tags.outlook.batchCopy":
            result = self._outlook_tags.batch_action("copy", folder=str(kwargs.get("folder", "")))
        elif command_id == "cmd.tags.outlook.batchDelete":
            result = self._outlook_tags.batch_action("delete")
        elif command_id == "cmd.table.capture":
            rows = kwargs.get("rows", [])
            result = self._table_capture.capture(rows, separator=str(kwargs.get("separator", " | ")))
        elif command_id == "cmd.table.capture.exportClipboard":
            result = self._table_capture.export_buffer(block_separator=str(kwargs.get("blockSeparator", "\n\n")))
        elif command_id == "cmd.table.capture.clearBuffer":
            result = self._table_capture.clear_buffer()
        elif command_id == "cmd.profile.hotkeyChainCreate":
            result = self._chains.create_chain(
                str(kwargs.get("name", "")),
                [str(x) for x in list(kwargs.get("commandIds", []))],
            )
        elif command_id == "cmd.profile.hotkeyChainList":
            result = self._chains.list_chains()
        elif command_id == "cmd.profile.hotkeyChainRun":
            chain = self._chains.get_chain(str(kwargs.get("name", "")))
            if not chain.ok:
                result = chain
            else:
                commands = list((chain.payload or {}).get("commands", []))
                steps = []
                ok = True
                for cid in commands:
                    out = self.dispatch_command(context, cid)
                    steps.append(
                        {
                            "commandId": cid,
                            "ok": out.result.ok,
                            "message": out.result.message,
                        }
                    )
                    if not out.result.ok:
                        ok = False
                        break
                result = RuntimeResult(
                    ok=ok,
                    message="Hotkey chain executed." if ok else "Hotkey chain stopped on failure.",
                    payload={"chain": (chain.payload or {}).get("chain", ""), "steps": steps},
                )
        elif command_id == "cmd.shortcuts.dialog.detect":
            result = self._dialog_paths.detect(str(kwargs.get("windowTitle", "")))
        elif command_id == "cmd.shortcuts.dialog.insertPath":
            shortcut_id = str(kwargs.get("shortcutId", "")).strip()
            folder_path = str(kwargs.get("folderPath", "")).strip()
            if shortcut_id:
                lookup = self._shortcuts.get_shortcut(shortcut_id)
                if not lookup.ok:
                    result = lookup
                else:
                    folder_path = str((lookup.payload or {}).get("target", ""))
                    result = self._dialog_paths.insert_path(
                        folder_path,
                        window_title=str(kwargs.get("windowTitle", "")),
                        supports_insertion=bool(kwargs.get("supportsInsertion", True)),
                    )
            else:
                result = self._dialog_paths.insert_path(
                    folder_path,
                    window_title=str(kwargs.get("windowTitle", "")),
                    supports_insertion=bool(kwargs.get("supportsInsertion", True)),
                )
        elif command_id == "cmd.utility.progressCues.plan":
            result = self._progress.cue_plan(
                int(kwargs.get("totalSteps", 100)),
                tutorial=bool(kwargs.get("tutorial", False)),
            )
        elif command_id == "cmd.speech.history.capture":
            result = self._speech_history.append(str(kwargs.get("text", "")))
        elif command_id == "cmd.speech.history.browse":
            result = self._speech_history.browse(str(kwargs.get("direction", "next")))
        elif command_id == "cmd.speech.history.copyItem":
            result = self._speech_history.copy_item(int(kwargs.get("index", 0)))
        elif command_id == "cmd.speech.history.copyRange":
            result = self._speech_history.copy_range(
                int(kwargs.get("start", 0)),
                int(kwargs.get("end", 0)),
                separator=str(kwargs.get("separator", "\n")),
            )
        elif command_id == "cmd.speech.history.virtualView":
            result = self._speech_history.open_virtual_view()
        elif command_id == "cmd.utility.symbol.insertByCode":
            result = self._symbols.insert_by_code(str(kwargs.get("code", "")))
        elif command_id == "cmd.utility.symbol.search":
            result = self._symbols.search(str(kwargs.get("query", "")))
        elif command_id == "cmd.utility.symbol.recent":
            result = self._symbols.recent()
        elif command_id == "cmd.utility.windowBookmark.assign":
            result = self._bookmarks.assign(
                int(kwargs.get("slot", 1)),
                window_id=str(kwargs.get("windowId", context.window_id)),
                app_id=str(kwargs.get("appId", context.app_id)),
                name=str(kwargs.get("name", "")),
            )
        elif command_id == "cmd.utility.windowBookmark.recall":
            result = self._bookmarks.recall(int(kwargs.get("slot", 1)))
        elif command_id == "cmd.utility.windowBookmark.rename":
            result = self._bookmarks.rename(
                int(kwargs.get("slot", 1)),
                str(kwargs.get("name", "")),
            )
        elif command_id == "cmd.utility.windowBookmark.list":
            result = self._bookmarks.list_slots()
        elif command_id == "cmd.utility.systemReport.open":
            result = self._system_report.collect()
        elif command_id == "cmd.utility.systemReport.export":
            out_path = Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "system-report.txt")))
            result = self._system_report.export(out_path)
        elif command_id == "cmd.cuts.create":
            result = self._cuts.create_shortcut(
                name=str(kwargs.get("name", "")),
                target=str(kwargs.get("target", "")),
                target_type=str(kwargs.get("targetType", "file")),
            )
        elif command_id == "cmd.cuts.list":
            result = self._cuts.list_shortcuts(
                target_type=str(kwargs.get("targetType", "")),
                category=str(kwargs.get("category", "")),
            )
        elif command_id == "cmd.cuts.launch":
            result = self._cuts.launch_shortcut(str(kwargs.get("shortcutId", "")))
        elif command_id == "cmd.cuts.delete":
            result = self._cuts.delete_shortcut(str(kwargs.get("shortcutId", "")))
        elif command_id == "cmd.cuts.assignCategory":
            result = self._cuts.assign_category(
                str(kwargs.get("shortcutId", "")),
                str(kwargs.get("category", "general")),
            )
        elif command_id == "cmd.cuts.createPreset":
            result = self._cuts.create_preset(
                str(kwargs.get("preset", "")),
                [str(x) for x in list(kwargs.get("shortcutIds", []))],
            )
        elif command_id == "cmd.cuts.runPreset":
            result = self._cuts.run_preset(str(kwargs.get("preset", "")))
        elif command_id == "cmd.cuts.exportPresets":
            out_path = Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "shortcut-catalog-presets.json")))
            result = self._cuts.export_presets(out_path)
        elif command_id == "cmd.cuts.importPresets":
            in_path = Path(str(kwargs.get("inPath", "")))
            result = self._cuts.import_presets(in_path, overwrite=bool(kwargs.get("overwrite", False)))
        elif command_id == "cmd.cuts.dashboard":
            listing = self._cuts.list_shortcuts()
            items = (listing.payload or {}).get("items", []) if listing.ok else []
            by_category: Dict[str, int] = {}
            for row in items:
                cat = str(row.get("category", "general"))
                by_category[cat] = by_category.get(cat, 0) + 1
            result = RuntimeResult(
                ok=True,
                message="Shortcut Catalog dashboard ready.",
                payload={"total": len(items), "byCategory": by_category, "items": items[:20]},
            )
        elif command_id == "cmd.clip.library.open":
            result = self._library.open_library(
                archive_state=str(kwargs.get("archiveState", "")),
                category=str(kwargs.get("category", "")),
                folder_id=str(kwargs.get("folderId", "")),
            )
        elif command_id == "cmd.clip.library.ingestSlot":
            result = self._library.ingest_slot(int(kwargs.get("slot", 1)))
        elif command_id == "cmd.clip.library.createFolder":
            result = self._library.create_folder(
                folder_name=str(kwargs.get("folderName", "")),
                category=str(kwargs.get("category", "general")),
            )
        elif command_id == "cmd.clip.library.renameFolder":
            result = self._library.rename_folder(
                folder_id=str(kwargs.get("folderId", "")),
                new_name=str(kwargs.get("newName", "")),
            )
        elif command_id == "cmd.clip.library.deleteFolder":
            result = self._library.delete_folder(str(kwargs.get("folderId", "")))
        elif command_id == "cmd.clip.library.moveToFolder":
            result = self._library.move_to_folder(
                clip_id=str(kwargs.get("clipId", "")),
                folder_id=str(kwargs.get("folderId", "")),
            )
        elif command_id == "cmd.clip.library.linkToFolder":
            result = self._library.link_to_folder(
                clip_id=str(kwargs.get("clipId", "")),
                folder_id=str(kwargs.get("folderId", "")),
            )
        elif command_id == "cmd.clip.library.retainSlotAlias":
            result = self._library.retain_slot_alias(
                clip_id=str(kwargs.get("clipId", "")),
                alias=str(kwargs.get("slotAlias", "")),
            )
        elif command_id == "cmd.clip.library.restoreToSlot":
            result = self._library.restore_to_slot(
                clip_id=str(kwargs.get("clipId", "")),
                slot=int(kwargs.get("slot", 1)),
                mode=str(kwargs.get("mode", "replace")),
            )
        elif command_id == "cmd.clip.library.setRetentionPolicy":
            result = self._library.set_retention_policy(
                clip_id=str(kwargs.get("clipId", "")),
                policy=str(kwargs.get("policy", "keep-forever")),
            )
        elif command_id == "cmd.clip.library.listLinkedLocations":
            result = self._library.list_linked_locations(str(kwargs.get("clipId", "")))
        elif command_id == "cmd.profile.hotkeyPresetExport":
            out_path = Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "hotkey-preset.json")))
            import hashlib
            import json

            base = {"version": 1, "bindings": self.config.keymap_bindings}
            integrity = hashlib.sha256(json.dumps(base, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
            payload = {**base, "integrity": integrity}
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            result = RuntimeResult(ok=True, message="Hotkey preset exported.", payload={"path": str(out_path)})
        elif command_id == "cmd.profile.hotkeyPresetImport":
            in_path = Path(str(kwargs.get("inPath", "")))
            import hashlib
            import json

            if not in_path.exists():
                result = RuntimeResult(ok=False, message="Hotkey preset file not found.")
            else:
                try:
                    payload = json.loads(in_path.read_text(encoding="utf-8"))
                    base = {"version": payload.get("version", 0), "bindings": payload.get("bindings", [])}
                    expected = hashlib.sha256(json.dumps(base, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
                    if payload.get("integrity") and payload.get("integrity") != expected:
                        result = RuntimeResult(ok=False, message="Hotkey preset integrity check failed.")
                    else:
                        self.config.keymap_bindings = list(base["bindings"])
                        result = RuntimeResult(ok=True, message="Hotkey preset imported.", payload={"bindingCount": len(self.config.keymap_bindings)})
                except Exception as exc:
                    result = RuntimeResult(ok=False, message=f"Hotkey preset import failed: {exc}")
        else:
            result = RuntimeResult(
                ok=False,
                message=(
                    f"Command {command_id} is not implemented in the runtime dispatcher yet."
                ),
                next_steps=["Open palette for fallback actions."],
            )

        if result.payload is None:
            result.payload = {}
        result.payload["executionPolicy"] = {
            "confirmation": plan.confirmation,
            "preview": plan.preview,
            "safetyGate": plan.safety_gate,
        }

        command_meta = self.config.command(command_id) or {}
        safety_class = str(command_meta.get("safetyClass", "safe"))

        self._health.record(
            app_id=context.app_id,
            command_id=command_id,
            ok=result.ok,
            reason="" if result.ok else (result.code.value if result.code else "failure"),
        )

        skip_journal = bool(kwargs.get("__skipJournal", False))
        if result.ok and safety_class in ("mutating", "destructive") and not skip_journal:
            rollback_action = self._rollback_action_for(command_id, kwargs, result)
            reversible = rollback_action is not None
            self._journal.record(
                app_id=context.app_id,
                command_id=command_id,
                action_type=safety_class,
                summary=result.message,
                reversible=reversible,
                rollback_action=rollback_action,
            )

        self._last_action = f"{command_id}: {result.message}"

        return DispatchOutcome(plan=plan, result=result)
