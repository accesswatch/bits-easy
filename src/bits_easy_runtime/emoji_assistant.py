from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, cast
from urllib.request import Request, urlopen
from xml.etree import ElementTree

from .engine import RuntimeResult


FetchTextFn = Callable[[str, float], str]


def _default_fetch_text(url: str, timeout: float) -> str:
    req = Request(url, headers={"User-Agent": "BITS-EASY/1.0"})
    with urlopen(req, timeout=float(timeout)) as resp:
        return resp.read().decode("utf-8")


def _normalize_cp(value: str) -> str:
    # CLDR annotations strip FE0F/FE0E, so normalize keys before lookups.
    return str(value or "").replace("\uFE0F", "").replace("\uFE0E", "")


def _slugify(value: str) -> str:
    raw = re.sub(r"[^a-z0-9]+", "-", str(value or "").strip().lower())
    return raw.strip("-") or "misc"


def _safe_alias_from_name(name: str) -> str:
    slug = _slugify(name)
    return slug or "emoji"


def _parse_version(value: str) -> float:
    try:
        return float(str(value or "0").strip())
    except Exception:
        return 0.0


_EMOJI_LINE_RE = re.compile(
    r"^\s*[0-9A-F ]+\s*;\s*fully-qualified\s*#\s*(\S+)\s+E([0-9]+(?:\.[0-9]+)?)\s+(.+?)\s*$"
)


_GROUP_TO_CATEGORY = {
    "Smileys & Emotion": "people",
    "People & Body": "people",
    "Component": "people",
    "Animals & Nature": "nature",
    "Food & Drink": "food",
    "Travel & Places": "places",
    "Activities": "activities",
    "Objects": "objects",
    "Symbols": "symbols",
    "Flags": "flags",
}


class EmojiAssistant:
    def __init__(
        self,
        *,
        cache_path: Path | None = None,
        locale: str = "",
        max_emoji_version: str = "",
        emoji_test_url: str = "https://unicode.org/Public/emoji/latest/emoji-test.txt",
        cldr_annotations_base_url: str = "https://raw.githubusercontent.com/unicode-org/cldr/main/common/annotations",
        fetch_timeout_seconds: float = 2.5,
        fetch_text: FetchTextFn = _default_fetch_text,
    ) -> None:
        self._cache_path = Path(cache_path) if cache_path is not None else (Path.home() / "AppData" / "Roaming" / "BITS-EASY" / "emoji-catalog-cache.json")
        requested_locale = str(locale or "").strip() or str(os.getenv("BITS_EASY_EMOJI_LOCALE", "")).strip() or "en"
        self._locale = requested_locale.lower()
        configured_max_version = str(max_emoji_version or "").strip() or str(os.getenv("BITS_EASY_EMOJI_MAX_VERSION", "")).strip() or "15.1"
        self._max_emoji_version = _parse_version(configured_max_version)
        self._emoji_test_url = str(emoji_test_url).strip()
        self._cldr_base = str(cldr_annotations_base_url).rstrip("/")
        self._fetch_timeout_seconds = float(fetch_timeout_seconds)
        self._fetch_text: FetchTextFn = fetch_text
        self._catalog_ready = False
        self._items: List[Dict[str, str]] = [
            {"emoji": "😀", "alias": "grinning", "category": "people"},
            {"emoji": "🙂", "alias": "smile", "category": "people"},
            {"emoji": "🎉", "alias": "party", "category": "events"},
            {"emoji": "✅", "alias": "check", "category": "symbols"},
            {"emoji": "⚠️", "alias": "warning", "category": "symbols"},
            {"emoji": "🚀", "alias": "rocket", "category": "objects"},
            {"emoji": "📌", "alias": "pin", "category": "objects"},
            {"emoji": "📅", "alias": "calendar", "category": "objects"},
            {"emoji": "💡", "alias": "idea", "category": "objects"},
            {"emoji": "❤️", "alias": "heart", "category": "symbols"},
        ]

    def _read_cache(self) -> Dict[str, List[Dict[str, str]]]:
        try:
            payload: Any = json.loads(self._cache_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        if not isinstance(payload, dict):
            return {}
        payload_map = cast(Dict[str, Any], payload)
        locales = payload_map.get("locales", {})
        if not isinstance(locales, dict):
            return {}
        locale_map = cast(Dict[str, Any], locales)
        rows = locale_map.get(self._locale, [])
        if not isinstance(rows, list):
            return {}
        row_items = cast(List[Any], rows)
        valid_rows: List[Dict[str, str]] = []
        for row in row_items:
            if not isinstance(row, dict):
                continue
            row_map = cast(Dict[str, Any], row)
            valid_rows.append({str(k): str(v) for k, v in row_map.items()})
        return {"items": valid_rows}

    def _write_cache(self, items: List[Dict[str, str]]) -> None:
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        payload: Dict[str, object] = {"updatedAt": int(time.time()), "locales": {self._locale: items}}
        try:
            if self._cache_path.exists():
                prior: Any = json.loads(self._cache_path.read_text(encoding="utf-8"))
                if isinstance(prior, dict):
                    prior_map = cast(Dict[str, Any], prior)
                    prior_locales = prior_map.get("locales", {})
                    if isinstance(prior_locales, dict):
                        merged: Dict[str, Any] = dict(cast(Dict[str, Any], prior_locales))
                        merged[self._locale] = items
                        payload["locales"] = merged
        except Exception:
            pass
        self._cache_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")

    def _parse_emoji_test(self, raw: str) -> List[Dict[str, str]]:
        group = "Objects"
        subgroup = "general"
        rows: List[Dict[str, str]] = []

        for line in str(raw or "").splitlines():
            text = line.strip()
            if not text:
                continue
            if text.startswith("# group:"):
                group = text.split(":", 1)[1].strip() or group
                continue
            if text.startswith("# subgroup:"):
                subgroup = text.split(":", 1)[1].strip() or subgroup
                continue

            match = _EMOJI_LINE_RE.match(text)
            if not match:
                continue

            emoji_char = match.group(1)
            version = _parse_version(match.group(2))
            unicode_name = match.group(3).strip()
            if version > self._max_emoji_version:
                continue

            category = _GROUP_TO_CATEGORY.get(group, "misc")
            rows.append(
                {
                    "emoji": emoji_char,
                    "alias": _safe_alias_from_name(unicode_name),
                    "category": category,
                    "group": _slugify(group),
                    "groupLabel": group,
                    "subgroup": _slugify(subgroup),
                    "name": unicode_name,
                }
            )
        return rows

    def _parse_cldr_annotations(self, raw: str) -> Dict[str, Dict[str, str]]:
        out: Dict[str, Dict[str, str]] = {}
        root = ElementTree.fromstring(raw)
        for node in root.findall(".//annotation"):
            cp = _normalize_cp(node.attrib.get("cp", ""))
            if not cp:
                continue
            text = (node.text or "").strip()
            if not text:
                continue
            target = out.setdefault(cp, {"label": "", "keywords": ""})
            if node.attrib.get("type", "") == "tts":
                target["label"] = text
            else:
                target["keywords"] = text.replace(" | ", " ")
        return out

    def _load_cldr_for_locale(self, locale: str) -> Dict[str, Dict[str, str]]:
        normalized = _slugify(locale).replace("-", "_")
        url = f"{self._cldr_base}/{normalized}.xml"
        raw = self._fetch_text(url, self._fetch_timeout_seconds)
        return self._parse_cldr_annotations(raw)

    def _build_dynamic_items(self) -> List[Dict[str, str]]:
        emoji_test_raw = self._fetch_text(self._emoji_test_url, self._fetch_timeout_seconds)
        base_rows = self._parse_emoji_test(emoji_test_raw)
        if not base_rows:
            return []

        en_annotations = self._load_cldr_for_locale("en")
        locale_annotations = en_annotations if self._locale == "en" else self._load_cldr_for_locale(self._locale)

        dynamic_rows: List[Dict[str, str]] = []
        for row in base_rows:
            cp = _normalize_cp(str(row.get("emoji", "")))
            loc = locale_annotations.get(cp, {})
            en = en_annotations.get(cp, {})
            label = str(loc.get("label", "") or en.get("label", "") or row.get("name", "")).strip()
            keywords = str(loc.get("keywords", "") or en.get("keywords", "")).strip()
            merged = dict(row)
            merged["label"] = label
            merged["keywords"] = keywords
            dynamic_rows.append(merged)
        return dynamic_rows

    def _ensure_catalog(self) -> None:
        if self._catalog_ready:
            return

        try:
            dynamic = self._build_dynamic_items()
            if dynamic:
                self._items = dynamic
                self._write_cache(dynamic)
                self._catalog_ready = True
                return
        except Exception:
            pass

        cached = self._read_cache().get("items", [])
        if cached:
            self._items = cached
        self._catalog_ready = True

    def list_items(self, *, category: str = "", query: str = "", limit: int = 25) -> RuntimeResult:
        self._ensure_catalog()
        cat = str(category or "").strip().lower()
        q = str(query or "").strip().lower()
        max_items = max(1, min(100, int(limit)))

        rows: List[Dict[str, str]] = []
        for item in self._items:
            item_category = str(item.get("category", "")).lower()
            item_group = str(item.get("group", "")).lower()
            if cat and cat not in (item_category, item_group):
                continue
            probe = (
                f"{item.get('alias','')} {item.get('emoji','')} {item.get('category','')} "
                f"{item.get('group','')} {item.get('groupLabel','')} {item.get('label','')} {item.get('keywords','')}"
            ).lower()
            if q and q not in probe:
                continue
            rows.append(dict(item))

        rows = rows[:max_items]
        return RuntimeResult(
            ok=True,
            message="Emoji list ready.",
            payload={"items": rows, "count": len(rows), "category": cat, "query": q},
        )

    def insert(self, *, alias: str = "", fallback_text: bool = False) -> RuntimeResult:
        self._ensure_catalog()
        needle = str(alias or "").strip().lower()
        if not needle:
            return RuntimeResult(ok=False, message="Emoji alias is required.")

        match = next((row for row in self._items if str(row.get("alias", "")).strip().lower() == needle), None)
        if match is None:
            return RuntimeResult(ok=False, message="Emoji alias not found.")

        rendered = f":{needle}:" if bool(fallback_text) else str(match.get("emoji", ""))
        return RuntimeResult(
            ok=True,
            message="Emoji insertion ready.",
            payload={
                "alias": needle,
                "emoji": str(match.get("emoji", "")),
                "insertText": rendered,
                "insertViaClipboard": True,
            },
        )
