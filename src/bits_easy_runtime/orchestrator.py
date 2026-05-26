from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .diagnostics import get_logger
from .dispatcher import DispatchOutcome, RuntimeDispatcher
from .engine import AppContext

_logger = get_logger("bits_easy.orchestrator")


class CommandOrchestrator:
    def __init__(
        self,
        dispatcher: RuntimeDispatcher,
        journal_path: Path | str,
        intent_store_path: Path | str | None = None,
    ):
        self.dispatcher = dispatcher
        self.journal_path = Path(journal_path)
        self.intent_store_path = (
            Path(intent_store_path)
            if intent_store_path is not None
            else self.journal_path.with_name("intent-memory.json")
        )
        self.recent_commands: List[str] = []
        self.intent_memory: Dict[str, str] = {}
        self.command_rankings: Dict[str, Dict[str, float]] = {}
        self._load_intent_store()

    def _write_journal(self, row: Dict[str, Any]) -> None:
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        with self.journal_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=True) + "\n")

    def _load_intent_store(self) -> None:
        if not self.intent_store_path.exists():
            return

        try:
            payload = json.loads(self.intent_store_path.read_text(encoding="utf-8"))
        except Exception:
            _logger.exception("BITS-EASY: loading intent store at %s failed", self.intent_store_path)
            return

        intents = payload.get("intentMemory", {})
        rankings = payload.get("commandRankings", {})

        if isinstance(intents, dict):
            self.intent_memory = {str(k): str(v) for k, v in intents.items()}
        if isinstance(rankings, dict):
            loaded: Dict[str, Dict[str, float]] = {}
            for app_id, values in rankings.items():
                if not isinstance(values, dict):
                    continue
                loaded[str(app_id)] = {str(cmd): float(score) for cmd, score in values.items()}
            self.command_rankings = loaded

    def _save_intent_store(self) -> None:
        self.intent_store_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "intentMemory": self.intent_memory,
            "commandRankings": self.command_rankings,
        }
        self.intent_store_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    def _base_candidates_for_intent(self, intent: str) -> List[str]:
        lowered = intent.lower()
        if "selection" in lowered:
            return ["cmd.selection.markStart", "cmd.selection.markEnd", "cmd.selection.readContext"]
        if "clip" in lowered or "copy" in lowered:
            return [
                "cmd.capture.quickInbox",
                "cmd.clip.copyToSlot",
                "cmd.clip.pasteFromSlot",
                "cmd.clip.describeSlot",
            ]
        if "journal" in lowered or "recover" in lowered or "rollback" in lowered:
            return ["cmd.journal.list", "cmd.journal.rollback", "cmd.capture.quickInbox.list"]
        return ["cmd.help.availableHotkeys", "cmd.capture.quickInbox", "cmd.selection.markStart"]

    def _intent_bonus(self, intent: str, command_id: str) -> float:
        lowered = intent.lower()
        bonus = 0.0
        if "selection" in lowered and command_id.startswith("cmd.selection."):
            bonus += 3.0
        if ("clip" in lowered or "copy" in lowered) and (
            command_id.startswith("cmd.clip.") or command_id.startswith("cmd.capture.")
        ):
            bonus += 3.0
        if ("recover" in lowered or "rollback" in lowered or "journal" in lowered) and command_id.startswith("cmd.journal."):
            bonus += 3.0
        return bonus

    def _bump_ranking(self, app_id: str, command_id: str) -> None:
        app_scores = self.command_rankings.setdefault(app_id, {})
        app_scores[command_id] = app_scores.get(command_id, 0.0) + 1.0

    def suggestion_details_for_app(self, app_id: str) -> List[Dict[str, Any]]:
        intent = self.intent_memory.get(app_id, "")
        candidates = self._base_candidates_for_intent(intent)
        app_scores = self.command_rankings.get(app_id, {})

        details = []
        for command_id in candidates:
            learned = float(app_scores.get(command_id, 0.0))
            intent_bonus = self._intent_bonus(intent, command_id)
            total = learned + intent_bonus
            reasons = []
            if learned > 0:
                reasons.append(f"learnedUsage:{learned:.1f}")
            if intent_bonus > 0:
                reasons.append(f"intentBoost:{intent_bonus:.1f}")
            if not reasons:
                reasons.append("baseline")

            details.append(
                {
                    "commandId": command_id,
                    "score": total,
                    "reasons": reasons,
                }
            )

        details.sort(key=lambda row: row["score"], reverse=True)
        return details

    def execute(self, context: AppContext, command_id: str, *, intent: Optional[str] = None, **kwargs: Any) -> DispatchOutcome:
        outcome = self.dispatcher.dispatch_command(context, command_id, **kwargs)
        self.recent_commands.append(command_id)
        self.recent_commands = self.recent_commands[-20:]

        self._bump_ranking(context.app_id, command_id)

        if intent:
            self.intent_memory[context.app_id] = intent

        self._save_intent_store()

        row = {
            "appId": context.app_id,
            "commandId": command_id,
            "ok": outcome.result.ok,
            "message": outcome.result.message,
            "policy": outcome.result.payload.get("executionPolicy") if outcome.result.payload else None,
            "intent": intent,
        }
        self._write_journal(row)
        return outcome

    def suggestions_for_app(self, app_id: str) -> List[str]:
        return [row["commandId"] for row in self.suggestion_details_for_app(app_id)]

    def reset_app_memory(self, app_id: str) -> bool:
        removed = False
        if app_id in self.intent_memory:
            del self.intent_memory[app_id]
            removed = True
        if app_id in self.command_rankings:
            del self.command_rankings[app_id]
            removed = True
        if removed:
            self._save_intent_store()
        return removed

