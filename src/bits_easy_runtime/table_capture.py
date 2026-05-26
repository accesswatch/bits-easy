from __future__ import annotations

from typing import List

from .engine import RuntimeResult


class TableCaptureExtractor:
    def __init__(self):
        self._buffer: List[str] = []

    def capture(self, rows: List[List[str]], *, separator: str = " | ") -> RuntimeResult:
        if not rows:
            return RuntimeResult(ok=False, message="Table rows are required.")
        normalized = []
        for row in rows:
            normalized.append(separator.join(str(cell) for cell in row))
        chunk = "\n".join(normalized)
        self._buffer.append(chunk)
        return RuntimeResult(
            ok=True,
            message="Table capture appended.",
            payload={
                "rows": len(rows),
                "separator": separator,
                "chunk": chunk,
                "bufferCount": len(self._buffer),
            },
        )

    def export_buffer(self, *, block_separator: str = "\n\n") -> RuntimeResult:
        output = block_separator.join(self._buffer)
        return RuntimeResult(
            ok=True,
            message="Table capture buffer exported.",
            payload={"content": output, "captures": len(self._buffer)},
        )

    def clear_buffer(self) -> RuntimeResult:
        removed = len(self._buffer)
        self._buffer.clear()
        return RuntimeResult(ok=True, message="Table capture buffer cleared.", payload={"cleared": removed})
