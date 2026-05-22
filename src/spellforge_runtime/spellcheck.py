"""Spell-check service stub.

The dispatcher imports ``SpellCheckService`` and routes the
``cmd.spell.checkCurrentWord`` command through it. The full spell-check
backend is part of an upcoming sprint (see SPRINT-BACKLOG-EXECUTION.md), but
the module must be importable today so the runtime — and therefore the NVDA
add-on — can load.

This stub returns a structured "not yet implemented" result so callers see a
useful message instead of an exception.
"""

from __future__ import annotations

from .diagnostics import get_logger
from .engine import RuntimeResult

_logger = get_logger("spellforge.spellcheck")


def _current_word(buffer: str, caret: int) -> str:
    if not buffer:
        return ""
    if caret < 0:
        caret = 0
    if caret > len(buffer):
        caret = len(buffer)

    start = caret
    while start > 0 and not buffer[start - 1].isspace():
        start -= 1
    end = caret
    while end < len(buffer) and not buffer[end].isspace():
        end += 1
    return buffer[start:end]


class SpellCheckService:
    """Minimal spell-check shim used by ``RuntimeDispatcher``.

    The real engine will plug into NVDA's spell-check infrastructure. Until
    then, ``check_current_word`` reports the word under the caret and a
    "not yet available" message so the surrounding command stays addressable.
    """

    def __init__(self) -> None:
        _logger.debug("Spellforge: SpellCheckService stub initialized")

    def check_current_word(self, buffer: str, caret: int) -> RuntimeResult:
        word = _current_word(buffer or "", int(caret or 0))
        return RuntimeResult(
            ok=False,
            message="Spell check is not yet available in this build.",
            payload={"word": word, "caret": int(caret or 0)},
            next_steps=[
                "Use your application's built-in spell checker for now.",
                "Track progress via the Spellforge SPRINT-BACKLOG-EXECUTION.md.",
            ],
        )


__all__ = ["SpellCheckService"]
