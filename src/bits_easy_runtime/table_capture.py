from __future__ import annotations

import json
from typing import List

from .engine import RuntimeResult


class TableCaptureExtractor:
    def __init__(self):
        self._buffer: List[str] = []
        self._captures: List[List[List[str]]] = []

    @staticmethod
    def _normalize_rows(rows: List[List[str]]) -> List[List[str]]:
        normalized: List[List[str]] = []
        for row in rows:
            normalized.append([str(cell) for cell in row])
        return normalized

    @staticmethod
    def _table_to_delimited(table: List[List[str]], delimiter: str) -> str:
        return "\n".join(delimiter.join(cell for cell in row) for row in table)

    @staticmethod
    def _table_to_markdown(table: List[List[str]]) -> str:
        if not table:
            return ""
        widths = [0] * max(len(r) for r in table)
        for row in table:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(cell))

        def _pad_row(row: List[str]) -> str:
            cells = []
            for i in range(len(widths)):
                val = row[i] if i < len(row) else ""
                cells.append(val.ljust(widths[i]))
            return "| " + " | ".join(cells) + " |"

        header = _pad_row(table[0])
        divider = "| " + " | ".join("-" * max(3, w) for w in widths) + " |"
        body = [
            _pad_row(row)
            for row in table[1:]
        ]
        return "\n".join([header, divider, *body])

    @staticmethod
    def _escape_html(value: str) -> str:
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    @classmethod
    def _table_to_html(cls, table: List[List[str]]) -> str:
        if not table:
            return "<table></table>"
        lines = ["<table>"]
        header = table[0]
        lines.append("  <thead>")
        lines.append("    <tr>" + "".join(f"<th>{cls._escape_html(c)}</th>" for c in header) + "</tr>")
        lines.append("  </thead>")
        lines.append("  <tbody>")
        for row in table[1:]:
            lines.append("    <tr>" + "".join(f"<td>{cls._escape_html(c)}</td>" for c in row) + "</tr>")
        lines.append("  </tbody>")
        lines.append("</table>")
        return "\n".join(lines)

    @staticmethod
    def _table_to_json_rows(table: List[List[str]]) -> str:
        if not table:
            return "[]"
        header = table[0]
        rows = []
        for row in table[1:]:
            item = {}
            for i, col in enumerate(header):
                item[str(col).strip() or f"col{i + 1}"] = row[i] if i < len(row) else ""
            rows.append(item)
        return json.dumps(rows, ensure_ascii=True)

    def capture(self, rows: List[List[str]], *, separator: str = " | ") -> RuntimeResult:
        if not rows:
            return RuntimeResult(ok=False, message="Table rows are required.")
        table = self._normalize_rows(rows)
        normalized = []
        for row in table:
            normalized.append(separator.join(cell for cell in row))
        chunk = "\n".join(normalized)
        self._buffer.append(chunk)
        self._captures.append(table)
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

    def export_buffer(self, *, block_separator: str = "\n\n", format: str = "plain") -> RuntimeResult:
        fmt = str(format or "plain").strip().lower()
        if not self._captures:
            return RuntimeResult(
                ok=True,
                message="Table capture buffer exported.",
                payload={"content": "", "captures": 0, "format": fmt},
            )

        rendered: List[str] = []
        for table in self._captures:
            if fmt == "tsv":
                rendered.append(self._table_to_delimited(table, "\t"))
            elif fmt == "csv":
                rendered.append(self._table_to_delimited(table, ","))
            elif fmt in ("markdown", "md"):
                rendered.append(self._table_to_markdown(table))
            elif fmt == "html":
                rendered.append(self._table_to_html(table))
            elif fmt in ("json", "json-rows"):
                rendered.append(self._table_to_json_rows(table))
            elif fmt in ("plain", "text"):
                rendered.append(self._buffer[len(rendered)])
            else:
                return RuntimeResult(
                    ok=False,
                    message="Unsupported table export format.",
                    payload={"supportedFormats": ["plain", "tsv", "csv", "markdown", "html", "json"]},
                )

        output = block_separator.join(rendered)
        return RuntimeResult(
            ok=True,
            message="Table capture buffer exported.",
            payload={"content": output, "captures": len(self._buffer), "format": fmt},
        )

    def clear_buffer(self) -> RuntimeResult:
        removed = len(self._buffer)
        self._buffer.clear()
        self._captures.clear()
        return RuntimeResult(ok=True, message="Table capture buffer cleared.", payload={"cleared": removed})
