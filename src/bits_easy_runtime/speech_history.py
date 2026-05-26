from __future__ import annotations

from typing import List

from .engine import RuntimeResult


class SpeechHistory:
    def __init__(self):
        self._items: List[str] = []
        self._cursor: int = -1

    def append(self, text: str) -> RuntimeResult:
        value = text.strip()
        if not value:
            return RuntimeResult(ok=False, message="Speech history item cannot be empty.")
        self._items.append(value)
        self._cursor = len(self._items) - 1
        return RuntimeResult(ok=True, message="Speech history captured.", payload={"count": len(self._items), "index": self._cursor})

    def browse(self, direction: str) -> RuntimeResult:
        if not self._items:
            return RuntimeResult(ok=False, message="Speech history is empty.")

        d = direction.strip().lower()
        if d in ("left", "previous", "back"):
            self._cursor = max(0, self._cursor - 1)
        elif d in ("right", "next", "forward"):
            self._cursor = min(len(self._items) - 1, self._cursor + 1)
        else:
            return RuntimeResult(ok=False, message="Unknown browse direction.")

        return RuntimeResult(
            ok=True,
            message="Speech history browse moved.",
            payload={"index": self._cursor, "text": self._items[self._cursor], "count": len(self._items)},
        )

    def copy_item(self, index: int) -> RuntimeResult:
        idx = int(index)
        if idx < 0 or idx >= len(self._items):
            return RuntimeResult(ok=False, message="Speech history index out of range.")
        return RuntimeResult(ok=True, message="Speech history item copied.", payload={"text": self._items[idx], "index": idx})

    def copy_range(self, start: int, end: int, separator: str = "\n") -> RuntimeResult:
        if not self._items:
            return RuntimeResult(ok=False, message="Speech history is empty.")
        lo = max(0, min(int(start), int(end)))
        hi = min(len(self._items) - 1, max(int(start), int(end)))
        if lo > hi:
            return RuntimeResult(ok=False, message="Invalid history range.")
        text = separator.join(self._items[lo : hi + 1])
        return RuntimeResult(ok=True, message="Speech history range copied.", payload={"start": lo, "end": hi, "text": text})

    def open_virtual_view(self) -> RuntimeResult:
        return RuntimeResult(
            ok=True,
            message="Speech history virtual view ready.",
            payload={"items": [{"index": i, "text": t} for i, t in enumerate(self._items)], "count": len(self._items)},
        )
