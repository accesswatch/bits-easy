from __future__ import annotations

from dataclasses import dataclass
from difflib import get_close_matches
from typing import List, Optional

from .engine import RuntimeResult


_BASE_WORDS = {
    "a",
    "about",
    "after",
    "again",
    "all",
    "also",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "because",
    "been",
    "before",
    "being",
    "between",
    "both",
    "but",
    "by",
    "can",
    "check",
    "checked",
    "checking",
    "checker",
    "command",
    "commands",
    "context",
    "copy",
    "could",
    "current",
    "default",
    "did",
    "do",
    "does",
    "done",
    "edit",
    "enabled",
    "error",
    "errors",
    "feature",
    "file",
    "for",
    "from",
    "get",
    "good",
    "great",
    "had",
    "has",
    "have",
    "help",
    "hotkey",
    "hotkeys",
    "if",
    "in",
    "into",
    "is",
    "it",
    "its",
    "just",
    "key",
    "like",
    "list",
    "message",
    "mode",
    "name",
    "new",
    "next",
    "no",
    "not",
    "now",
    "of",
    "on",
    "one",
    "open",
    "or",
    "other",
    "output",
    "please",
    "press",
    "profile",
    "result",
    "results",
    "save",
    "search",
    "selection",
    "set",
    "settings",
    "show",
    "simple",
    "slot",
    "source",
    "spell",
    "spelling",
    "start",
    "status",
    "stop",
    "suggest",
    "suggestion",
    "suggestions",
    "system",
    "test",
    "tests",
    "text",
    "that",
    "the",
    "their",
    "then",
    "there",
    "these",
    "they",
    "this",
    "time",
    "to",
    "toggle",
    "tool",
    "try",
    "two",
    "type",
    "update",
    "use",
    "used",
    "user",
    "was",
    "we",
    "were",
    "what",
    "when",
    "where",
    "which",
    "with",
    "word",
    "words",
    "workflow",
    "you",
    "your",
}

_TECH_ALLOWLIST = {
    "bits_easy",
    "nvda",
    "tinispell",
    "capslock",
}


@dataclass
class WordSpan:
    word: str
    start: int
    end: int


class SpellCheckService:
    def __init__(self) -> None:
        self._lexicon = _BASE_WORDS | _TECH_ALLOWLIST

    @staticmethod
    def _is_word_char(ch: str) -> bool:
        return ch.isalpha() or ch in ("'", "-")

    def _word_at_caret(self, buffer: str, caret: int) -> Optional[WordSpan]:
        if not buffer:
            return None

        idx = max(0, min(caret, len(buffer)))
        pivot = idx

        if pivot < len(buffer) and self._is_word_char(buffer[pivot]):
            pass
        elif pivot > 0 and self._is_word_char(buffer[pivot - 1]):
            pivot -= 1
        else:
            return None

        start = pivot
        while start > 0 and self._is_word_char(buffer[start - 1]):
            start -= 1

        end = pivot + 1
        while end < len(buffer) and self._is_word_char(buffer[end]):
            end += 1

        token = buffer[start:end].strip("'-")
        if not token:
            return None
        return WordSpan(word=token, start=start, end=end)

    def _normalize_parts(self, word: str) -> List[str]:
        return [p for p in word.lower().replace("'", "-").split("-") if p]

    def _is_correct(self, word: str) -> bool:
        if len(word) <= 1:
            return True
        if word.isupper() and len(word) > 1:
            return True

        parts = self._normalize_parts(word)
        return bool(parts) and all(part in self._lexicon for part in parts)

    def _suggest(self, word: str, limit: int = 5) -> List[str]:
        parts = self._normalize_parts(word)
        if not parts:
            return []
        base = parts[0]
        return get_close_matches(base, sorted(self._lexicon), n=limit, cutoff=0.75)

    def check_current_word(self, buffer: str, caret: int) -> RuntimeResult:
        span = self._word_at_caret(buffer, caret)
        if span is None:
            return RuntimeResult(
                ok=False,
                message="No word found at the caret.",
                next_steps=["Move the caret to a word and try again."],
            )

        correct = self._is_correct(span.word)
        suggestions = [] if correct else self._suggest(span.word)

        if correct:
            message = f"Spelling looks good: {span.word}."
        elif suggestions:
            message = f"Possible misspelling: {span.word}. Suggestions: {', '.join(suggestions)}."
        else:
            message = f"Possible misspelling: {span.word}. No strong suggestions."

        return RuntimeResult(
            ok=True,
            message=message,
            payload={
                "word": span.word,
                "start": span.start,
                "end": span.end,
                "isCorrect": correct,
                "suggestions": suggestions,
            },
        )

