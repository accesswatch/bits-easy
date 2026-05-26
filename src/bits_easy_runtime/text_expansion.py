from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from .diagnostics import get_logger
from .engine import RuntimeResult

_logger = get_logger("bits_easy.text_expansion")


@dataclass
class ExpansionEntry:
    abbreviation: str
    content: str
    title: str


class TextExpansionStore:
    def __init__(self, storage_path: Path | str):
        self.storage_path = Path(storage_path)
        self._entries: Dict[str, ExpansionEntry] = {}
        self._primary: Optional[str] = None
        self._load()

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            payload = json.loads(self.storage_path.read_text(encoding="utf-8"))
            self._primary = payload.get("primary")
            rows = payload.get("entries", {})
            for abbr, item in rows.items():
                self._entries[abbr] = ExpansionEntry(
                    abbreviation=abbr,
                    content=str(item.get("content", "")),
                    title=str(item.get("title", abbr)),
                )
        except Exception:
            _logger.exception("BITS-EASY: loading text expansions at %s failed", self.storage_path)
            self._entries = {}
            self._primary = None

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "primary": self._primary,
            "entries": {
                abbr: {"content": entry.content, "title": entry.title}
                for abbr, entry in self._entries.items()
            },
        }
        self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def upsert(self, abbreviation: str, content: str, *, title: Optional[str] = None, overwrite: bool = False) -> RuntimeResult:
        abbreviation = abbreviation.strip()
        if not abbreviation:
            return RuntimeResult(ok=False, message="Abbreviation cannot be empty.")

        existing = self._entries.get(abbreviation)
        if existing and existing.content != content and not overwrite:
            return RuntimeResult(
                ok=False,
                message="Abbreviation conflict detected.",
                payload={"abbreviation": abbreviation, "existing": existing.content, "incoming": content},
                next_steps=["Retry with overwrite enabled.", "Rename one of the abbreviations."],
            )

        self._entries[abbreviation] = ExpansionEntry(
            abbreviation=abbreviation,
            content=content,
            title=(title or abbreviation),
        )
        if self._primary is None:
            self._primary = abbreviation
        self._save()
        return RuntimeResult(ok=True, message="Text expansion saved.", payload={"abbreviation": abbreviation})

    def expand(self, abbreviation: str) -> RuntimeResult:
        entry = self._entries.get(abbreviation.strip())
        if not entry:
            return RuntimeResult(ok=False, message="Expansion not found.")
        return RuntimeResult(ok=True, message="Expansion ready.", payload={"content": entry.content, "abbreviation": entry.abbreviation})

    def list_entries(self) -> RuntimeResult:
        return RuntimeResult(
            ok=True,
            message="Expansion list ready.",
            payload={
                "primary": self._primary,
                "items": [
                    {"abbreviation": e.abbreviation, "title": e.title, "length": len(e.content)}
                    for e in sorted(self._entries.values(), key=lambda x: x.abbreviation)
                ],
            },
        )

    def rename(self, abbreviation: str, new_title: str) -> RuntimeResult:
        entry = self._entries.get(abbreviation.strip())
        if not entry:
            return RuntimeResult(ok=False, message="Expansion not found.")
        entry.title = new_title.strip() or entry.title
        self._save()
        return RuntimeResult(ok=True, message="Expansion renamed.", payload={"abbreviation": entry.abbreviation, "title": entry.title})

    def delete(self, abbreviation: str) -> RuntimeResult:
        abbr = abbreviation.strip()
        if abbr not in self._entries:
            return RuntimeResult(ok=False, message="Expansion not found.")
        del self._entries[abbr]
        if self._primary == abbr:
            self._primary = next(iter(sorted(self._entries.keys())), None)
        self._save()
        return RuntimeResult(ok=True, message="Expansion deleted.", payload={"abbreviation": abbr})

    def set_primary(self, abbreviation: str) -> RuntimeResult:
        abbr = abbreviation.strip()
        if abbr not in self._entries:
            return RuntimeResult(ok=False, message="Expansion not found.")
        self._primary = abbr
        self._save()
        return RuntimeResult(ok=True, message="Primary quick insert updated.", payload={"abbreviation": abbr})

    def quick_insert(self) -> RuntimeResult:
        if not self._primary:
            return RuntimeResult(ok=False, message="No primary quick insert is configured.")
        return self.expand(self._primary)

