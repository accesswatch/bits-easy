from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from .engine import RuntimeResult


@dataclass
class SymbolEntry:
    code: str
    symbol: str
    description: str


class SymbolAssistant:
    def __init__(self):
        self._catalog: Dict[str, SymbolEntry] = {
            "169": SymbolEntry(code="169", symbol="©", description="copyright"),
            "174": SymbolEntry(code="174", symbol="®", description="registered"),
            "176": SymbolEntry(code="176", symbol="°", description="degree"),
            "177": SymbolEntry(code="177", symbol="±", description="plus minus"),
            "8364": SymbolEntry(code="8364", symbol="€", description="euro"),
            "8482": SymbolEntry(code="8482", symbol="™", description="trademark"),
        }
        self._recent_code: str = ""

    def insert_by_code(self, code: str) -> RuntimeResult:
        key = "".join(ch for ch in str(code).strip() if ch.isdigit())
        if not key:
            return RuntimeResult(ok=False, message="Numeric symbol code is required.")

        entry = self._catalog.get(key)
        if entry is None:
            return RuntimeResult(ok=False, message="Symbol code not found in catalog.")

        self._recent_code = key
        return RuntimeResult(
            ok=True,
            message="Symbol resolved by code.",
            payload={
                "code": entry.code,
                "symbol": entry.symbol,
                "description": entry.description,
            },
        )

    def search(self, query: str) -> RuntimeResult:
        q = str(query).strip().lower()
        if not q:
            return RuntimeResult(ok=False, message="Search query is required.")

        rows: List[dict] = []
        for entry in self._catalog.values():
            if q in entry.description.lower() or q in entry.code:
                rows.append(
                    {
                        "code": entry.code,
                        "symbol": entry.symbol,
                        "description": entry.description,
                    }
                )
        rows.sort(key=lambda r: (r["description"], r["code"]))

        return RuntimeResult(
            ok=True,
            message="Symbol search results ready.",
            payload={"items": rows, "count": len(rows)},
        )

    def recent(self) -> RuntimeResult:
        if not self._recent_code:
            return RuntimeResult(ok=False, message="No recent symbol code.")

        entry = self._catalog[self._recent_code]
        return RuntimeResult(
            ok=True,
            message="Recent symbol code ready.",
            payload={
                "code": entry.code,
                "symbol": entry.symbol,
                "description": entry.description,
            },
        )
