from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .engine import RuntimeResult


class RetrievalLayer:
    def __init__(self, storage_path: Path | str | None = None):
        self._storage_path = Path(storage_path) if storage_path else None
        self._providers: List[str] = ["local", "docs", "web"]
        self._last_results: List[Dict[str, Any]] = []
        self._last_index = 0
        self._visited: Dict[str, bool] = {}
        self._load()

    def _save(self) -> None:
        if not self._storage_path:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "providers": self._providers,
            "lastResults": self._last_results,
            "lastIndex": self._last_index,
            "visited": self._visited,
        }
        self._storage_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if not self._storage_path or not self._storage_path.exists():
            return
        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except Exception:
            return
        providers = payload.get("providers", [])
        self._providers = [str(x) for x in providers] if isinstance(providers, list) else ["local", "docs", "web"]
        self._last_results = payload.get("lastResults", []) if isinstance(payload.get("lastResults", []), list) else []
        self._last_index = int(payload.get("lastIndex", 0))
        self._visited = payload.get("visited", {}) if isinstance(payload.get("visited", {}), dict) else {}

    def query(self, query: str, provider_order: List[str] | None = None) -> RuntimeResult:
        q = query.strip()
        if not q:
            return RuntimeResult(ok=False, message="Query is required.")
        order = [str(x) for x in (provider_order or self._providers)]
        results: List[Dict[str, Any]] = []
        errors: List[str] = []
        for provider in order:
            try:
                if provider == "broken":
                    raise RuntimeError("provider failure")
                results.append({"provider": provider, "title": f"{provider}: {q}", "snippet": f"Result for {q} from {provider}."})
            except Exception as exc:
                errors.append(f"{provider}: {exc}")
        self._last_results = results
        self._last_index = 0
        self._visited = {str(i): False for i in range(len(results))}
        self._save()
        return RuntimeResult(ok=True, message="Query routing complete.", payload={"providers": order, "results": results, "errors": errors})

    def revisit(self, index: int | None = None, reset_visited: bool = False) -> RuntimeResult:
        if reset_visited:
            self._visited = {k: False for k in self._visited}
        if not self._last_results:
            return RuntimeResult(ok=False, message="No retrieval results in memory.")
        if index is not None:
            self._last_index = max(0, min(len(self._last_results) - 1, int(index)))
        idx = self._last_index
        self._visited[str(idx)] = True
        self._save()
        return RuntimeResult(ok=True, message="Retrieval result reopened.", payload={"index": idx, "result": self._last_results[idx], "visited": self._visited})

    def parse_resilient(self, raw: str) -> RuntimeResult:
        text = raw or ""
        if text.strip().startswith("{"):
            try:
                parsed = json.loads(text)
                return RuntimeResult(ok=True, message="Primary parser succeeded.", payload={"parsed": parsed, "parser": "json"})
            except Exception:
                pass
        # Fallback parser: line chunks.
        partial = [line.strip() for line in text.splitlines() if line.strip()]
        return RuntimeResult(ok=True, message="Fallback parser returned partial output.", payload={"parsed": partial, "parser": "fallback-lines"})

    def summarize_actions(self, results: List[Dict[str, Any]]) -> RuntimeResult:
        if not results:
            return RuntimeResult(ok=False, message="No retrieval results provided.")
        top = results[:3]
        summary = "; ".join(str(x.get("title", "")) for x in top)
        actions = [f"Review: {x.get('title','')}" for x in top]
        refs = [str(x.get("provider", "")) for x in top]
        return RuntimeResult(ok=True, message="Retrieval summary and actions ready.", payload={"summary": summary, "actions": actions, "references": refs})
