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
from .spellcheck import SpellCheckService
from .surface_context import classify_surface, fallback_steps_for
from .file_ops import FileOpsService
from .ai_assistant import AiAssistantService
from .glow_client import GlowMcpService


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
        self._studio = PocketClipsStudio(runtime, storage_path=base_dir / "pocketclips-studio.json")
        self._health = IntegrationHealthTracker(base_dir / "integration-health.jsonl")
        self._expansions = TextExpansionStore(base_dir / "text-expansions.json")
        self._cuts = ShortcutCatalogStore(base_dir / "shortcut-catalog.json")
        self._library = ClipLibraryStore(runtime, base_dir / "clip-library.json")
        self._shortcuts = ShortcutsStore(base_dir / "shortcuts.json")
        self._tagging = TaggingSession()
        self._file_ops = FileOpsService(self._tagging)
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
        self._ai = AiAssistantService(base_dir / "ai-assistant.json")
        self._glow = GlowMcpService()
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
        self._spellcheck = SpellCheckService()
        self._latest_result: Dict[str, Any] = {
            "confidence": 0.0,
            "fallbacks": ["cmd.palette.open"],
            "summary": "",
        }
        self._last_action = ""

    def _ai_enabled(self) -> bool:
        status = self._ai.key_status()
        if not status.ok:
            return False
        return bool((status.payload or {}).get("hasAnyKey", False))

    def _attach_ai_augmentation(self, result: RuntimeResult, *, tool: str, source: str, replace: bool = False) -> None:
        if not result.ok or not source.strip() or not self._ai_enabled():
            return
        if result.payload is None:
            result.payload = {}
        if "aiAugmentation" in result.payload:
            return

        ai = self._ai.tool_run(tool=tool, text=source, replace=replace)
        if not ai.ok:
            return
        ai_payload = ai.payload or {}
        result.payload["aiAugmentation"] = {
            "enabled": True,
            "tool": str(ai_payload.get("tool", tool)),
            "text": str(ai_payload.get("text", "")),
            "replaceSuggested": bool(ai_payload.get("replaceSuggested", replace)),
        }

    def _attach_ai_spellcheck_augmentation(self, result: RuntimeResult, *, source: str) -> None:
        if not result.ok or not source.strip() or not self._ai_enabled():
            return
        if result.payload is None:
            result.payload = {}
        if "aiAugmentation" in result.payload:
            return

        ai = self._ai.tool_run(tool="spellcheck", text=source, replace=False)
        if not ai.ok:
            return
        ai_payload = ai.payload or {}
        ai_text = str(ai_payload.get("text", "")).strip()
        suggestions = [] if not ai_text or ai_text == source else [ai_text]
        result.payload["aiAugmentation"] = {
            "enabled": True,
            "tool": "spellcheck",
            "text": ai_text,
            "suggestions": suggestions,
        }

    def _selection_action_source(self, context: AppContext) -> str:
        # Prefer explicit marker-captured selection, then clipboard, then full buffer.
        marked = self.runtime.selection_text_for_actions(context)
        if marked:
            return marked
        clip = context.clipboard_text.strip()
        if clip:
            return clip
        return context.buffer.strip()

    @staticmethod
    def _resolve_tag_path(context: AppContext, kwargs: Dict[str, Any]) -> str:
        raw = str(kwargs.get("path", "")).strip()
        if not raw:
            raw = context.clipboard_text.strip() or context.buffer.strip()
        if "\n" in raw:
            raw = raw.splitlines()[0].strip()
        return raw.strip().strip('"').strip("'")

    def _resolve_tag_path_from_selection(self, context: AppContext, kwargs: Dict[str, Any]) -> str:
        raw = str(kwargs.get("path", "")).strip()
        if not raw:
            raw = self._selection_action_source(context)
        if "\n" in raw:
            raw = raw.splitlines()[0].strip()
        return raw.strip().strip('"').strip("'")

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

        if command_id == "cmd.tags.session.toggleCurrent":
            payload = result.payload or {}
            path = str(payload.get("path", kwargs.get("path", ""))).strip()
            if path:
                return {
                    "commandId": "cmd.tags.session.toggleCurrent",
                    "kwargs": {"path": path},
                }

        if command_id == "cmd.clip.protectSlot":
            slot = kwargs.get("slot")
            if slot is not None:
                return {
                    "commandId": "cmd.clip.unprotectSlot",
                    "kwargs": {"slot": int(slot)},
                }
        if command_id == "cmd.clip.unprotectSlot":
            slot = kwargs.get("slot")
            if slot is not None:
                return {
                    "commandId": "cmd.clip.protectSlot",
                    "kwargs": {"slot": int(slot)},
                }

        if command_id == "cmd.notes.mode.set":
            mode = str(kwargs.get("mode", "")).strip().lower()
            if mode in ("simple", "advanced"):
                inverse = "advanced" if mode == "simple" else "simple"
                return {
                    "commandId": "cmd.notes.mode.set",
                    "kwargs": {"mode": inverse},
                }

        if command_id == "cmd.cuts.create":
            payload = result.payload or {}
            shortcut_id = str(payload.get("shortcutId", "")).strip()
            if shortcut_id:
                return {
                    "commandId": "cmd.cuts.delete",
                    "kwargs": {"shortcutId": shortcut_id},
                }

        if command_id == "cmd.cuts.assignCategory":
            payload = result.payload or {}
            shortcut_id = str(payload.get("shortcutId", kwargs.get("shortcutId", ""))).strip()
            previous = str(payload.get("previousCategory", "")).strip()
            if shortcut_id and previous:
                return {
                    "commandId": "cmd.cuts.assignCategory",
                    "kwargs": {"shortcutId": shortcut_id, "category": previous},
                }

        if command_id == "cmd.notes.category.move":
            payload = result.payload or {}
            category = str(payload.get("category", kwargs.get("category", ""))).strip()
            previous_parent = str(payload.get("previousParent", "")).strip()
            if category:
                return {
                    "commandId": "cmd.notes.category.move",
                    "kwargs": {"category": category, "parent": previous_parent},
                }

        if command_id in (
            "cmd.author.pipeline.polish",
            "cmd.author.template.apply",
            "cmd.author.html.fixApply",
        ):
            payload = result.payload or {}
            undo_token = str(payload.get("undoToken", "")).strip()
            if undo_token:
                return {
                    "commandId": "cmd.author.pipeline.undo",
                    "kwargs": {"undoToken": undo_token},
                }

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
        mnemonic_hints = [
            {
                "commandId": "cmd.selection.markStart",
                "hint": "Use Grave+Shift+S to set selection start anchor.",
            },
            {
                "commandId": "cmd.integration.itemChooser.open",
                "hint": "Use Grave+O to open Screen Item Chooser.",
            },
            {
                "commandId": "cmd.integration.itemChooser.openOcr",
                "hint": "Use Grave+Shift+O to open Item Chooser with OCR preselected.",
            },
            {
                "commandId": "cmd.selection.markEnd",
                "hint": "Use Grave+Shift+E to capture selection end and range.",
            },
            {
                "commandId": "cmd.clip.copyToSlot",
                "hint": "Use Grave+1 to copy selection into the active clip lane.",
            },
            {
                "commandId": "cmd.clip.pasteFromSlot",
                "hint": "Use Grave+2 to paste from the active clip lane.",
            },
            {
                "commandId": "cmd.notes.quickCapture",
                "hint": "Use Grave+Q to capture quick notes from current context.",
            },
            {
                "commandId": "cmd.journal.undoLast",
                "hint": "Use Grave+Shift+J to undo the latest reversible action.",
            },
            {
                "commandId": "cmd.author.pipeline.polish",
                "hint": "Use Grave+Shift+A to polish draft text in one pass.",
            },
            {
                "commandId": "cmd.author.template.apply",
                "hint": "Use Grave+Shift+N for release-notes template scaffolding.",
            },
            {
                "commandId": "cmd.author.pipeline.undo",
                "hint": "Use Grave+Shift+Z to undo the latest author pipeline output.",
            },
        ]
        return RuntimeResult(
            ok=True,
            message=f"Available hotkeys for {context.app_id} ready.",
            payload={
                "hotkeys": rows,
                "count": len(rows),
                "appId": context.app_id,
                "mnemonicHints": mnemonic_hints,
            },
        )

    @staticmethod
    def _mission_id_for_command(command_id: str) -> str:
        mapping = {
            "cmd.author.template.apply": "author-template",
            "cmd.author.pipeline.polish": "author-polish",
            "cmd.author.html.fixPreview": "author-html-preview",
            "cmd.author.html.fixApply": "author-html-apply",
            "cmd.author.pipeline.undo": "author-undo",
        }
        if command_id.startswith("cmd.selection."):
            return "select-range"
        if command_id.startswith("cmd.clip."):
            return "clips-core"
        if command_id.startswith("cmd.notes."):
            return "notes-core"
        if command_id.startswith("cmd.diary."):
            return "diary-core"
        if command_id.startswith("cmd.cuts."):
            return "cuts-core"
        return mapping.get(command_id, "")

    def _attach_mission_telemetry(self, command_id: str, result: RuntimeResult) -> None:
        mission_id = self._mission_id_for_command(command_id)
        if not mission_id:
            return
        before = self._missions.missions_status(self.profile_id)
        before_done = set((before.payload or {}).get("completed", [])) if before.ok else set()
        completed = self._missions.missions_complete(self.profile_id, mission_id)
        if not completed.ok:
            return
        done = set((completed.payload or {}).get("completed", []))
        is_first_completion = mission_id in done and mission_id not in before_done
        if result.payload is None:
            result.payload = {}
        result.payload["missionTelemetry"] = {
            "profile": self.profile_id,
            "missionId": mission_id,
            "firstCompletion": is_first_completion,
            "completed": sorted(done),
            "next": str((completed.payload or {}).get("next", "")),
        }
        if is_first_completion and self._is_core_magical_command(command_id):
            next_mission = str((completed.payload or {}).get("next", "")).strip()
            prompt_text = (
                f"First mission completed: {mission_id}."
                if not next_mission
                else f"First mission completed: {mission_id}. Next mission: {next_mission}."
            )
            result.payload["guidedMissionPrompt"] = {
                "title": "Guided mission update",
                "text": prompt_text,
                "nextMission": next_mission,
                "profile": self.profile_id,
            }

    @staticmethod
    def _is_core_magical_command(command_id: str) -> bool:
        return (
            command_id.startswith("cmd.selection.")
            or command_id.startswith("cmd.clip.")
            or command_id.startswith("cmd.cuts.")
            or command_id.startswith("cmd.notes.")
            or command_id.startswith("cmd.diary.")
            or command_id.startswith("cmd.author.")
            or command_id in ("cmd.journal.undoLast",)
        )

    def _attach_core_narration(self, command_id: str, result: RuntimeResult) -> None:
        if not self._is_core_magical_command(command_id):
            return
        if result.payload is None:
            result.payload = {}

        confidence = result.payload.get("confidence")
        if not isinstance(confidence, (int, float)):
            confidence = 0.93 if result.ok else 0.41
            result.payload["confidence"] = float(confidence)

        action_map = {
            "cmd.selection.markStart": "Move caret and run selection end capture.",
            "cmd.selection.markEnd": "Run selection summarize or rewrite on captured range.",
            "cmd.clip.copyToSlot": "Use clip paste to insert, or describe slot for preview.",
            "cmd.clip.pasteFromSlot": "If needed, undo latest action using quick undo.",
            "cmd.notes.quickCapture": "Route capture to notes, cuts, or tasks.",
            "cmd.diary.create": "List this month to verify appointment placement.",
            "cmd.author.pipeline.polish": "Review polished output and apply undo if needed.",
            "cmd.author.template.apply": "Fill placeholders, then run polish flow.",
            "cmd.author.html.fixPreview": "Apply fix preview when change list looks correct.",
            "cmd.author.html.fixApply": "Use undo token to restore original HTML when needed.",
            "cmd.author.pipeline.undo": "Continue editing from restored source content.",
            "cmd.journal.undoLast": "Confirm output state, then continue workflow.",
        }
        next_action = action_map.get(command_id, "Continue with the next guided action.")
        if not result.ok:
            next_action = "Try a fallback command from the palette and retry with context."

        if "nextAction" not in result.payload:
            result.payload["nextAction"] = next_action
        result.payload["narration"] = {
            "confidence": float(confidence),
            "nextAction": str(result.payload.get("nextAction", next_action)),
            "tone": "guidance",
        }
        if not result.next_steps:
            result.next_steps = [str(result.payload.get("nextAction", next_action))]

    def _core_mutating_command_ids(self) -> list[str]:
        prefixes = ("cmd.selection.", "cmd.clip.", "cmd.cuts.", "cmd.notes.", "cmd.diary.", "cmd.author.")
        rows: list[str] = []
        for command_id, meta in self.config.command_catalog.items():
            if not str(command_id).startswith(prefixes):
                continue
            safety = str(meta.get("safetyClass", "safe"))
            if safety not in ("mutating", "destructive"):
                continue
            rows.append(str(command_id))
        rows.sort()
        return rows

    @staticmethod
    def _rollback_support_matrix() -> Dict[str, Dict[str, str]]:
        return {
            "cmd.author.pipeline.polish": {
                "status": "conditional",
                "reason": "Uses undoToken produced by author pipeline payload.",
                "rollbackCommandId": "cmd.author.pipeline.undo",
            },
            "cmd.author.template.apply": {
                "status": "conditional",
                "reason": "Uses undoToken produced by template apply payload.",
                "rollbackCommandId": "cmd.author.pipeline.undo",
            },
            "cmd.author.html.fixApply": {
                "status": "conditional",
                "reason": "Uses undoToken produced by HTML fix apply payload.",
                "rollbackCommandId": "cmd.author.pipeline.undo",
            },
            "cmd.clip.protectSlot": {
                "status": "full",
                "reason": "Inverse operation is deterministic.",
                "rollbackCommandId": "cmd.clip.unprotectSlot",
            },
            "cmd.clip.unprotectSlot": {
                "status": "full",
                "reason": "Inverse operation is deterministic.",
                "rollbackCommandId": "cmd.clip.protectSlot",
            },
            "cmd.notes.mode.set": {
                "status": "full",
                "reason": "Mode inversion is deterministic.",
                "rollbackCommandId": "cmd.notes.mode.set",
            },
            "cmd.cuts.create": {
                "status": "full",
                "reason": "Created shortcut ID is captured in payload.",
                "rollbackCommandId": "cmd.cuts.delete",
            },
            "cmd.cuts.assignCategory": {
                "status": "full",
                "reason": "Previous category captured before mutation.",
                "rollbackCommandId": "cmd.cuts.assignCategory",
            },
            "cmd.notes.category.move": {
                "status": "full",
                "reason": "Previous parent captured before mutation.",
                "rollbackCommandId": "cmd.notes.category.move",
            },
        }

    def _rollback_coverage_report(self, out_path: Optional[Path] = None) -> RuntimeResult:
        commands = self._core_mutating_command_ids()
        matrix = self._rollback_support_matrix()
        items: list[Dict[str, Any]] = []
        for command_id in commands:
            row = matrix.get(command_id)
            if row is None:
                items.append(
                    {
                        "commandId": command_id,
                        "status": "none",
                        "reason": "No rollback mapping declared.",
                        "rollbackCommandId": "",
                    }
                )
                continue
            items.append(
                {
                    "commandId": command_id,
                    "status": row.get("status", "none"),
                    "reason": row.get("reason", ""),
                    "rollbackCommandId": row.get("rollbackCommandId", ""),
                }
            )

        total = len(items)
        full = len([x for x in items if x.get("status") == "full"])
        capable = len([x for x in items if x.get("status") in ("full", "conditional")])
        strict_percent = round((float(full) / float(total)) * 100.0, 2) if total else 0.0
        capable_percent = round((float(capable) / float(total)) * 100.0, 2) if total else 0.0

        payload: Dict[str, Any] = {
            "scope": "core-mutating",
            "total": total,
            "fullRollbackCount": full,
            "rollbackCapableCount": capable,
            "strictCoveragePercent": strict_percent,
            "rollbackCapablePercent": capable_percent,
            "items": items,
        }

        if out_path is not None:
            lines = [
                "# Rollback Coverage Report",
                "",
                f"- Scope: core-mutating",
                f"- Total commands: {total}",
                f"- Strict rollback coverage: {strict_percent}%",
                f"- Rollback-capable coverage: {capable_percent}%",
                "",
                "| Command | Status | Rollback Command | Reason |",
                "| --- | --- | --- | --- |",
            ]
            for row in items:
                lines.append(
                    f"| {row['commandId']} | {row['status']} | {row['rollbackCommandId'] or '-'} | {row['reason']} |"
                )
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            payload["outPath"] = str(out_path)

        return RuntimeResult(ok=True, message="Rollback coverage report ready.", payload=payload)

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

        chosen_row = next((r for r in accepted if str(r.get("commandId", "")) == resolved.matched_command_id), accepted[0] if accepted else None)
        binding_kwargs: Dict[str, Any] = {}
        if chosen_row is not None:
            bound = self.config.keymap_bindings[int(chosen_row.get("index", 0))]
            raw_args = bound.get("args", {})
            if isinstance(raw_args, dict):
                binding_kwargs = dict(raw_args)
        dispatch_kwargs = dict(binding_kwargs)
        dispatch_kwargs.update(kwargs)
        out = self.dispatch_command(context, resolved.matched_command_id, **dispatch_kwargs)
        if out.result.payload is None:
            out.result.payload = {}
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
        elif command_id == "cmd.integration.glow.health":
            result = self._glow.health()
        elif command_id == "cmd.integration.glow.audit":
            result = self._glow.audit(
                Path(str(kwargs.get("path", ""))),
                fmt=str(kwargs.get("format", "")),
            )
        elif command_id == "cmd.integration.glow.fix":
            result = self._glow.fix(
                Path(str(kwargs.get("path", ""))),
                fmt=str(kwargs.get("format", "")),
            )
        elif command_id == "cmd.integration.glow.convert":
            result = self._glow.convert(
                Path(str(kwargs.get("path", ""))),
                from_format=str(kwargs.get("fromFormat", "")),
                to_format=str(kwargs.get("toFormat", "markdown")),
            )
        elif command_id == "cmd.integration.glow.report":
            result = self._glow.report(
                Path(str(kwargs.get("path", ""))),
                fmt=str(kwargs.get("format", "")),
                report_type=str(kwargs.get("reportType", "json")),
            )
        elif command_id == "cmd.integration.itemChooser.open":
            result = RuntimeResult(
                ok=True,
                message="Opening Screen Item Chooser.",
                payload={
                    "integrationAction": {
                        "provider": "screenItemChooser",
                        "action": "open",
                        "ocr": False,
                    }
                },
            )
        elif command_id == "cmd.integration.itemChooser.openOcr":
            result = RuntimeResult(
                ok=True,
                message="Opening Screen Item Chooser with OCR.",
                payload={
                    "integrationAction": {
                        "provider": "screenItemChooser",
                        "action": "open",
                        "ocr": True,
                    }
                },
            )
        elif command_id == "cmd.selection.summarize":
            source = self._selection_action_source(context)
            result = self._adaptive.summarize(source)
            self._attach_ai_augmentation(result, tool="summarize", source=source)
            if result.ok:
                self._latest_result = {
                    "confidence": float((result.payload or {}).get("confidence", 0.0)),
                    "fallbacks": list((result.payload or {}).get("fallbacks", ["cmd.palette.open"])),
                    "summary": str((result.payload or {}).get("content", "")),
                }
        elif command_id == "cmd.selection.extractActions":
            source = self._selection_action_source(context)
            result = self._adaptive.extract_actions(source)
            self._attach_ai_augmentation(result, tool="extract-actions", source=source)
            if result.ok:
                items = list((result.payload or {}).get("items", []))
                self._latest_result = {
                    "confidence": float((result.payload or {}).get("confidence", 0.0)),
                    "fallbacks": list((result.payload or {}).get("fallbacks", ["cmd.palette.open"])),
                    "summary": "; ".join(str(x) for x in items[:3]),
                }
        elif command_id == "cmd.selection.rewriteBeginner":
            source = self._selection_action_source(context)
            result = self._adaptive.rewrite_beginner(source)
            self._attach_ai_augmentation(result, tool="a11y-rewrite", source=source)
            if result.ok:
                self._latest_result = {
                    "confidence": float((result.payload or {}).get("confidence", 0.0)),
                    "fallbacks": list((result.payload or {}).get("fallbacks", ["cmd.palette.open"])),
                    "summary": str((result.payload or {}).get("content", ""))[:120],
                }
        elif command_id == "cmd.spell.checkCurrentWord":
            result = self._spellcheck.check_current_word(context.buffer, context.caret)
            if result.ok:
                checked_word = str((result.payload or {}).get("word", ""))
                self._attach_ai_spellcheck_augmentation(result, source=checked_word)
        elif command_id == "cmd.capture.quickInbox":
            text = context.clipboard_text.strip() or context.buffer.strip()
            result = self._capture.capture(text, source_app=context.app_id, window_id=context.window_id)
            self._attach_ai_augmentation(result, tool="summarize", source=text)
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
        elif command_id == "cmd.journal.undoLast":
            listed = self._journal.list_entries(app_id=context.app_id)
            if not listed.ok:
                result = listed
            else:
                items = list((listed.payload or {}).get("items", []))
                target = next(
                    (
                        row
                        for row in reversed(items)
                        if bool(row.get("reversible", False))
                        and str(row.get("rollbackStatus", "none")) == "none"
                    ),
                    None,
                )
                if target is None:
                    result = RuntimeResult(
                        ok=False,
                        message="No reversible action is available for quick undo.",
                        next_steps=["Run journal list to inspect entries with rollback handlers."],
                    )
                else:
                    entry_id = str(target.get("entryId", ""))
                    prep = self._journal.rollback(entry_id)
                    if not prep.ok:
                        result = prep
                    else:
                        rollback_action = ((prep.payload or {}).get("rollbackAction") or {})
                        rollback_command = str(rollback_action.get("commandId", ""))
                        rollback_kwargs = rollback_action.get("kwargs", {})
                        if not rollback_command:
                            result = RuntimeResult(ok=False, message="Rollback handler metadata is incomplete.")
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
                                    "Quick undo completed."
                                    if rollback_outcome.result.ok
                                    else f"Quick undo failed: {rollback_outcome.result.message}"
                                ),
                                payload={
                                    "entryId": entry_id,
                                    "rolledBackCommandId": str(target.get("commandId", "")),
                                    "rollbackCommandId": rollback_command,
                                    "rollbackResult": rollback_outcome.result.payload or {},
                                },
                            )
        elif command_id == "cmd.journal.trends":
            result = self._journal.trend_report(window_days=int(kwargs.get("windowDays", 30)))
        elif command_id == "cmd.journal.rollbackCoverage":
            out_arg = str(kwargs.get("outPath", "")).strip()
            out_path = Path(out_arg) if out_arg else None
            result = self._rollback_coverage_report(out_path=out_path)
        elif command_id == "cmd.ai.key.set":
            result = self._ai.key_set(
                provider=str(kwargs.get("provider", "")),
                key=str(kwargs.get("key", "")),
            )
        elif command_id == "cmd.ai.key.delete":
            result = self._ai.key_delete(provider=str(kwargs.get("provider", "")))
        elif command_id == "cmd.ai.key.status":
            result = self._ai.key_status(provider=str(kwargs.get("provider", "")))
        elif command_id == "cmd.ai.key.storeStatus":
            result = self._ai.key_store_status()
        elif command_id == "cmd.ai.billingStatus":
            result = self._ai.billing_status(provider=str(kwargs.get("provider", "")))
        elif command_id == "cmd.ai.session.new":
            result = self._ai.session_new(title=str(kwargs.get("title", "")))
        elif command_id == "cmd.ai.session.clear":
            result = self._ai.session_clear()
        elif command_id == "cmd.ai.session.save":
            result = self._ai.session_save(session_id=str(kwargs.get("sessionId", "")))
        elif command_id == "cmd.ai.session.load":
            result = self._ai.session_load(session_id=str(kwargs.get("sessionId", "")))
        elif command_id == "cmd.ai.session.list":
            result = self._ai.session_list()
        elif command_id == "cmd.ai.session.delete":
            result = self._ai.session_delete(session_id=str(kwargs.get("sessionId", "")))
        elif command_id == "cmd.ai.tool.run":
            result = self._ai.tool_run(
                tool=str(kwargs.get("tool", "")),
                text=str(kwargs.get("text", "")),
                replace=bool(kwargs.get("replace", False)),
            )
        elif command_id == "cmd.ai.prompt.create":
            result = self._ai.prompt_create(
                name=str(kwargs.get("name", "")),
                text=str(kwargs.get("text", "")),
            )
        elif command_id == "cmd.ai.prompt.delete":
            result = self._ai.prompt_delete(name=str(kwargs.get("name", "")))
        elif command_id == "cmd.ai.prompt.list":
            result = self._ai.prompt_list(query=str(kwargs.get("query", "")))
        elif command_id == "cmd.ai.prompt.insert":
            result = self._ai.prompt_insert(name=str(kwargs.get("name", "")))
        elif command_id == "cmd.ai.doc.upload":
            result = self._ai.document_upload(
                path=Path(str(kwargs.get("path", ""))),
                title=str(kwargs.get("title", "")),
            )
        elif command_id == "cmd.ai.doc.ask":
            result = self._ai.document_ask(
                document_id=str(kwargs.get("documentId", "")),
                question=str(kwargs.get("question", "")),
            )
        elif command_id == "cmd.ai.doc.followUp":
            result = self._ai.document_ask(
                document_id=str(kwargs.get("documentId", "")),
                question=str(kwargs.get("question", "")),
            )
        elif command_id == "cmd.ai.image.generate":
            result = self._ai.image_generate(
                prompt=str(kwargs.get("prompt", "")),
                out_path=Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "generated-image.txt"))),
            )
        elif command_id == "cmd.ai.transcribe":
            result = self._ai.transcribe(
                in_path=Path(str(kwargs.get("inPath", ""))),
                speaker_separation=bool(kwargs.get("speakerSeparation", False)),
                translate_to=str(kwargs.get("translateTo", "")),
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
        elif command_id == "cmd.db.list":
            result = self._records.list_databases()
        elif command_id == "cmd.db.select":
            result = self._records.select_database(str(kwargs.get("name", "")))
        elif command_id == "cmd.db.template.apply":
            result = self._records.apply_template(
                str(kwargs.get("template", "")),
                database_name=str(kwargs.get("database", "")),
            )
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
        elif command_id == "cmd.db.entry.grid":
            result = self._records.entry_grid(
                fields=[str(x) for x in list(kwargs.get("fields", []))] or None,
                sort_by=str(kwargs.get("sortBy", "")),
                descending=bool(kwargs.get("descending", False)),
                limit=int(kwargs.get("limit", 50)),
                offset=int(kwargs.get("offset", 0)),
            )
        elif command_id == "cmd.db.entry.detail":
            result = self._records.entry_detail(str(kwargs.get("entryId", "")))
        elif command_id == "cmd.db.search":
            result = self._records.search_entries(
                str(kwargs.get("field", "")),
                str(kwargs.get("query", "")),
            )
        elif command_id == "cmd.db.search.advanced":
            result = self._records.search_advanced(
                text_query=str(kwargs.get("query", "")),
                filters=dict(kwargs.get("filters", {})),
                limit=int(kwargs.get("limit", 50)),
            )
        elif command_id == "cmd.db.sort":
            result = self._records.sort_entries(
                str(kwargs.get("field", "")),
                descending=bool(kwargs.get("descending", False)),
            )
        elif command_id == "cmd.db.dashboard":
            result = self._records.dashboard()
        elif command_id == "cmd.db.export.csv":
            result = self._records.export_csv(Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "records.csv"))))
        elif command_id == "cmd.db.export.text":
            result = self._records.export_text(Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "records.txt"))))
        elif command_id == "cmd.db.export.json":
            result = self._records.export_json(Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "records.json"))))
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
        elif command_id == "cmd.jamal.sync.plan":
            result = self._records.jamal_sync_plan(
                [dict(x) for x in list(kwargs.get("incomingEntries", []))],
                strategy=str(kwargs.get("strategy", "prefer-incoming")),
            )
        elif command_id == "cmd.jamal.sync.applyPlan":
            result = self._records.jamal_sync_apply_plan(
                str(kwargs.get("planId", "")),
                confirm=bool(kwargs.get("confirm", False)),
            )
        elif command_id == "cmd.jamal.sync.rollback":
            result = self._records.jamal_sync_rollback(database_name=str(kwargs.get("database", "")))
        elif command_id == "cmd.file.browse":
            result = self._file_ops.browse(
                str(kwargs.get("path", "")),
                include_hidden=bool(kwargs.get("includeHidden", False)),
            )
        elif command_id == "cmd.file.copy":
            result = self._file_ops.copy(
                str(kwargs.get("source", "")),
                str(kwargs.get("destination", "")),
                confirm=bool(kwargs.get("confirm", False)),
            )
        elif command_id == "cmd.file.move":
            result = self._file_ops.move(
                str(kwargs.get("source", "")),
                str(kwargs.get("destination", "")),
                confirm=bool(kwargs.get("confirm", False)),
            )
        elif command_id == "cmd.file.rename":
            result = self._file_ops.rename(
                str(kwargs.get("path", "")),
                str(kwargs.get("newName", "")),
                confirm=bool(kwargs.get("confirm", False)),
            )
        elif command_id == "cmd.file.delete":
            result = self._file_ops.delete(
                str(kwargs.get("path", "")),
                confirm=bool(kwargs.get("confirm", False)),
            )
        elif command_id == "cmd.file.zip.create":
            result = self._file_ops.zip_create(
                [str(x) for x in list(kwargs.get("sources", []))],
                str(kwargs.get("outPath", Path.cwd() / "dist" / "archive.zip")),
            )
        elif command_id == "cmd.file.path.copy":
            result = self._file_ops.copy_full_path(str(kwargs.get("path", "")))
        elif command_id == "cmd.file.tag.batch":
            result = self._file_ops.tag_batch([str(x) for x in list(kwargs.get("paths", []))])
        elif command_id == "cmd.notes.quickCapture":
            note_text = str(kwargs.get("text", ""))
            result = self._notes.quick_note(note_text, context.app_id)
            self._attach_ai_augmentation(result, tool="rewrite", source=note_text)
        elif command_id == "cmd.notes.mode.set":
            result = self._notes.set_mode(str(kwargs.get("mode", "simple")))
        elif command_id == "cmd.notes.category.create":
            result = self._notes.category_create(
                str(kwargs.get("category", "")),
                parent=str(kwargs.get("parent", "")),
            )
        elif command_id == "cmd.notes.category.move":
            category_id = str(kwargs.get("category", "")).strip().lower()
            previous_parent = ""
            before_tree = self._notes.category_tree()
            if before_tree.ok:
                tree = dict((before_tree.payload or {}).get("tree", {}))
                for parent, children in tree.items():
                    if category_id and category_id in [str(x) for x in list(children)]:
                        previous_parent = "" if str(parent) == "root" else str(parent)
                        break
            result = self._notes.category_move(
                str(kwargs.get("category", "")),
                new_parent=str(kwargs.get("parent", "")),
            )
            if result.ok:
                if result.payload is None:
                    result.payload = {}
                result.payload["previousParent"] = previous_parent
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
            help_text = str(kwargs.get("text", ""))
            result = self._notes.help_set(
                help_text,
                app_id=str(kwargs.get("appId", "")),
                domain=str(kwargs.get("domain", "")),
                page=str(kwargs.get("page", "")),
            )
            self._attach_ai_augmentation(result, tool="rewrite", source=help_text)
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
        elif command_id == "cmd.notes.category.tree":
            result = self._notes.category_tree()
        elif command_id == "cmd.notes.related.graph":
            result = self._notes.related_graph(str(kwargs.get("noteId", "")))
        elif command_id == "cmd.notes.attachment.action":
            result = self._notes.attachment_action(
                str(kwargs.get("noteId", "")),
                str(kwargs.get("path", "")),
                str(kwargs.get("action", "")),
            )
        elif command_id == "cmd.notes.backup.export":
            result = self._notes.backup_export(Path(str(kwargs.get("outPath", Path.cwd() / "dist" / "notes-backup.json"))))
        elif command_id == "cmd.notes.backup.restore":
            result = self._notes.backup_restore(Path(str(kwargs.get("inPath", ""))))
        elif command_id == "cmd.author.markdown.insert":
            result = self._author.markdown_insert(
                str(kwargs.get("kind", "")),
                str(kwargs.get("text", "")),
            )
        elif command_id == "cmd.author.pipeline.polish":
            source = str(kwargs.get("text", "")).strip() or self._selection_action_source(context)
            result = self._author.markdown_polish_pipeline(source)
        elif command_id == "cmd.author.pipeline.undo":
            result = self._author.pipeline_undo(str(kwargs.get("undoToken", "")))
        elif command_id == "cmd.author.template.apply":
            result = self._author.markdown_template_apply(
                str(kwargs.get("template", "release-notes")),
                str(kwargs.get("topic", "")),
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
        elif command_id == "cmd.author.html.fixPreview":
            result = self._author.html_fix_preview(str(kwargs.get("html", "")))
        elif command_id == "cmd.author.html.fixApply":
            result = self._author.html_fix_apply(str(kwargs.get("html", "")))
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
        elif command_id == "cmd.retrieve.anchor.set":
            result = self._retrieval.set_domain_anchor(
                str(kwargs.get("domain", "")),
                page=str(kwargs.get("page", "")),
                index=int(kwargs.get("index", 0)),
                phrase=str(kwargs.get("phrase", "")),
            )
        elif command_id == "cmd.retrieve.trail.open":
            result = self._retrieval.open_result_with_trail(
                int(kwargs.get("index", 0)),
                current_domain=str(kwargs.get("domain", "")),
                current_page=str(kwargs.get("page", "")),
            )
        elif command_id == "cmd.retrieve.trail.return":
            result = self._retrieval.return_previous_location()
        elif command_id == "cmd.retrieve.visited.report":
            result = self._retrieval.visited_report()
        elif command_id == "cmd.context.capabilityEnvelope":
            surface = classify_surface(context.app_id, context.control_id, context.control_id)
            adapter = self.runtime._adapter_for(context.app_id)
            steps = fallback_steps_for(surface.mode, str(kwargs.get("commandId", "cmd.context.capabilityEnvelope")))
            result = RuntimeResult(
                ok=True,
                message="Capability envelope ready.",
                payload={
                    "appId": context.app_id,
                    "surfaceMode": surface.mode,
                    "supportsSelection": bool(getattr(adapter, "supports_selection", False)),
                    "fallbackSteps": steps,
                },
            )
        elif command_id == "cmd.context.returnSourceDriftSafe":
            base = self.runtime.restore_source_anchor(context)
            if base.ok and bool((base.payload or {}).get("driftDetected", False)):
                surface = classify_surface(context.app_id, context.control_id, context.control_id)
                extra = fallback_steps_for(surface.mode, "cmd.context.returnSource")
                payload = dict(base.payload or {})
                payload["fallbackSteps"] = extra
                base.payload = payload
                if not base.next_steps:
                    base.next_steps = extra
            result = base
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
        elif command_id == "cmd.selection.markerStatus":
            result = self.runtime.describe_selection_markers(context)
        elif command_id == "cmd.selection.jumpStart":
            result = self.runtime.jump_selection_start(context)
        elif command_id == "cmd.selection.cancel":
            result = self.runtime.cancel_selection(context)
        elif command_id == "cmd.context.returnSource":
            result = self.runtime.restore_source_anchor(context)
        elif command_id == "cmd.clip.selectSlot":
            result = self.runtime.select_active_slot(int(kwargs.get("slot", self.runtime.active_slot())))
        elif command_id == "cmd.clip.copyToSlot":
            slot = int(kwargs.get("slot", self.runtime.active_slot()))
            result = self.runtime.copy_to_slot(context, slot=slot, text=kwargs.get("text"))
        elif command_id == "cmd.clip.pasteFromSlot":
            slot = int(kwargs.get("slot", self.runtime.active_slot()))
            result = self.runtime.paste_from_slot(slot=slot)
        elif command_id == "cmd.clip.protectSlot":
            slot = int(kwargs.get("slot", self.runtime.active_slot()))
            result = self.runtime.protect_slot(slot=slot)
        elif command_id == "cmd.clip.unprotectSlot":
            slot = int(kwargs.get("slot", self.runtime.active_slot()))
            result = self.runtime.unprotect_slot(slot=slot)
        elif command_id == "cmd.clip.deleteSlot":
            slot = int(kwargs.get("slot", self.runtime.active_slot()))
            result = self.runtime.delete_slot(slot=slot)
        elif command_id == "cmd.clip.editSlot":
            slot = int(kwargs.get("slot", self.runtime.active_slot()))
            content = str(kwargs.get("content", ""))
            result = self.runtime.edit_slot(slot=slot, content=content)
        elif command_id == "cmd.clip.describeSlot":
            slot = int(kwargs.get("slot", self.runtime.active_slot()))
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
        elif command_id == "cmd.merge.setDivider":
            divider = str(kwargs.get("divider", "line")).lower()
            if divider == "space":
                result = self.runtime.set_merge_divider_space()
            elif divider in ("paragraph", "para"):
                result = self.runtime.set_merge_divider_paragraph()
            else:
                result = self.runtime.set_merge_divider_line()
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
            rows = self._studio.list_slots(
                sort_by=str(kwargs.get("sortBy", "slot")),
                query=str(kwargs.get("query", "")),
                favorites_only=bool(kwargs.get("favoritesOnly", False)),
                smart_view=str(kwargs.get("smartView", "")),
            )
            result = RuntimeResult(
                ok=True,
                message="PocketClips browser opened.",
                payload={"slots": [r.__dict__ for r in rows]},
            )
        elif command_id == "cmd.clip.browser.search":
            rows = self._studio.list_slots(
                sort_by=str(kwargs.get("sortBy", "slot")),
                query=str(kwargs.get("query", "")),
                favorites_only=bool(kwargs.get("favoritesOnly", False)),
                smart_view=str(kwargs.get("smartView", "")),
            )
            result = RuntimeResult(
                ok=True,
                message="PocketClips search results ready.",
                payload={"slots": [r.__dict__ for r in rows]},
            )
        elif command_id == "cmd.clip.browser.filter":
            rows = self._studio.list_slots(
                source_app=str(kwargs.get("sourceApp", "")),
                only_protected=kwargs.get("onlyProtected"),
                sort_by=str(kwargs.get("sortBy", "slot")),
                query=str(kwargs.get("query", "")),
                favorites_only=bool(kwargs.get("favoritesOnly", False)),
                smart_view=str(kwargs.get("smartView", "")),
            )
            result = RuntimeResult(ok=True, message="PocketClips filter applied.", payload={"slots": [r.__dict__ for r in rows]})
        elif command_id == "cmd.clip.browser.sort":
            rows = self._studio.list_slots(sort_by=str(kwargs.get("sortBy", "slot")))
            result = RuntimeResult(ok=True, message="PocketClips sort applied.", payload={"slots": [r.__dict__ for r in rows]})
        elif command_id == "cmd.clip.browser.batchAction":
            result = self._studio.batch_action(
                slots=list(kwargs.get("slots", [])),
                action=str(kwargs.get("action", "")),
                out_path=kwargs.get("outPath"),
                separator=str(kwargs.get("separator", "\n")),
            )
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
            result = self._tagging.tag(self._resolve_tag_path(context, kwargs))
        elif command_id == "cmd.tags.session.toggleCurrent":
            result = self._tagging.toggle(self._resolve_tag_path(context, kwargs))
        elif command_id == "cmd.tags.session.tagFromSelection":
            result = self._tagging.tag(self._resolve_tag_path_from_selection(context, kwargs))
        elif command_id == "cmd.tags.session.untag":
            result = self._tagging.untag(self._resolve_tag_path(context, kwargs))
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
            sid = str(kwargs.get("shortcutId", "")).strip()
            previous_category = ""
            before_list = self._cuts.list_shortcuts()
            if before_list.ok:
                for row in list((before_list.payload or {}).get("items", [])):
                    if str(row.get("shortcutId", "")) == sid:
                        previous_category = str(row.get("category", "")).strip()
                        break
            result = self._cuts.assign_category(
                str(kwargs.get("shortcutId", "")),
                str(kwargs.get("category", "general")),
            )
            if result.ok:
                if result.payload is None:
                    result.payload = {}
                result.payload["previousCategory"] = previous_category
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
            result = self._library.retain_slot_alias_with_strategy(
                clip_id=str(kwargs.get("clipId", "")),
                alias=str(kwargs.get("slotAlias", "")),
                strategy=str(kwargs.get("aliasStrategy", "reject")),
            )
        elif command_id == "cmd.clip.library.assignCategory":
            result = self._library.assign_category(
                clip_id=str(kwargs.get("clipId", "")),
                category=str(kwargs.get("category", "")),
            )
        elif command_id == "cmd.clip.library.removeCategory":
            result = self._library.remove_category(
                clip_id=str(kwargs.get("clipId", "")),
                category=str(kwargs.get("category", "")),
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
        elif command_id == "cmd.clip.library.timeline":
            result = self._library.timeline_view(
                limit=int(kwargs.get("limit", 50)),
                source_app=str(kwargs.get("sourceApp", "")),
                category=str(kwargs.get("category", "")),
            )
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

        self._attach_core_narration(command_id, result)

        if result.ok:
            self._attach_mission_telemetry(command_id, result)

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

