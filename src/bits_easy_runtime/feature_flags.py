from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen

from .engine import RuntimeResult


class FeatureFlagManager:
    def __init__(
        self,
        *,
        state_path: Path,
        cache_path: Path,
        fallback_manifest_path: Path,
        default_manifest_url: str = "",
    ):
        self._state_path = Path(state_path)
        self._cache_path = Path(cache_path)
        self._fallback_manifest_path = Path(fallback_manifest_path)
        self._default_manifest_url = str(default_manifest_url or "").strip()
        self._state = self._load_state()
        self._manifest = self._load_manifest_bootstrap()

    @staticmethod
    def _rank_for_authority(authority: str) -> int:
        return {"stable": 1, "beta": 2, "internal": 3}.get(str(authority or "stable").strip().lower(), 1)

    @staticmethod
    def _sha256(value: str) -> str:
        return hashlib.sha256(str(value or "").encode("utf-8")).hexdigest()

    def _read_json(self, path: Path) -> Optional[Dict[str, Any]]:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return None
        if not isinstance(raw, dict):
            return None
        return raw

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")

    def _load_state(self) -> Dict[str, Any]:
        payload = self._read_json(self._state_path) or {}
        authority = str(payload.get("authority", "stable")).strip().lower() or "stable"
        overrides = payload.get("overrides", {})
        if not isinstance(overrides, dict):
            overrides = {}
        manifest_url = str(payload.get("manifestUrl", self._default_manifest_url)).strip()
        return {
            "authority": authority,
            "overrides": {str(k): bool(v) for k, v in overrides.items()},
            "manifestUrl": manifest_url,
            "lastGrant": str(payload.get("lastGrant", "")),
        }

    def _save_state(self) -> None:
        self._write_json(self._state_path, self._state)

    def _fallback_manifest(self) -> Dict[str, Any]:
        payload = self._read_json(self._fallback_manifest_path)
        if payload:
            payload["source"] = payload.get("source", "fallback")
            return payload
        return {
            "version": "1",
            "source": "fallback-default",
            "authorityStages": {
                "stable": ["stable"],
                "beta": ["stable", "beta"],
                "internal": ["stable", "beta", "experimental"],
            },
            "flags": [],
            "grants": [],
        }

    def _load_manifest_bootstrap(self) -> Dict[str, Any]:
        cached = self._read_json(self._cache_path)
        if cached:
            cached["source"] = cached.get("source", "cached")
            return cached
        return self._fallback_manifest()

    def _iter_flags(self) -> List[Dict[str, Any]]:
        flags = self._manifest.get("flags", [])
        if not isinstance(flags, list):
            return []
        return [f for f in flags if isinstance(f, dict)]

    def _flag_for_command(self, command_id: str) -> Optional[Dict[str, Any]]:
        cid = str(command_id or "").strip()
        if not cid:
            return None
        for flag in self._iter_flags():
            ids = flag.get("commandIds", [])
            prefixes = flag.get("commandPrefixes", [])
            if isinstance(ids, list) and cid in [str(x) for x in ids]:
                return flag
            if isinstance(prefixes, list):
                for pref in prefixes:
                    p = str(pref).strip()
                    if p and cid.startswith(p):
                        return flag
        return None

    def _allowed_stages_for_authority(self, authority: str) -> List[str]:
        rows = self._manifest.get("authorityStages", {})
        if not isinstance(rows, dict):
            return ["stable"]
        allowed = rows.get(authority, rows.get("stable", ["stable"]))
        if not isinstance(allowed, list):
            return ["stable"]
        return [str(x).strip().lower() for x in allowed if str(x).strip()]

    def _effective_enabled(self, flag: Dict[str, Any]) -> bool:
        flag_id = str(flag.get("id", "")).strip()
        defaults = bool(flag.get("enabledByDefault", False))
        override = self._state.get("overrides", {}).get(flag_id)
        return defaults if override is None else bool(override)

    def evaluate_command(self, command_id: str) -> Dict[str, Any]:
        flag = self._flag_for_command(command_id)
        if flag is None:
            return {
                "allowed": True,
                "reason": "no-feature-flag",
                "authority": str(self._state.get("authority", "stable")),
            }

        authority = str(self._state.get("authority", "stable")).strip().lower() or "stable"
        stage = str(flag.get("stage", "stable")).strip().lower() or "stable"
        flag_id = str(flag.get("id", "")).strip()
        enabled = self._effective_enabled(flag)
        allowed_stages = self._allowed_stages_for_authority(authority)
        stage_allowed = stage in allowed_stages
        allowed = enabled and stage_allowed

        reason = "enabled"
        if not enabled:
            reason = "flag-disabled"
        elif not stage_allowed:
            reason = "authority-denied"

        return {
            "allowed": bool(allowed),
            "reason": reason,
            "authority": authority,
            "stage": stage,
            "flagId": flag_id,
            "flagName": str(flag.get("name", flag_id)),
            "enabled": bool(enabled),
        }

    def filter_bindings(self, bindings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for binding in bindings:
            command_id = str(binding.get("commandId", ""))
            gate = self.evaluate_command(command_id)
            if gate.get("allowed", True):
                rows.append(binding)
        return rows

    def list_flags(self) -> RuntimeResult:
        items = []
        for flag in self._iter_flags():
            flag_id = str(flag.get("id", "")).strip()
            items.append(
                {
                    "id": flag_id,
                    "name": str(flag.get("name", flag_id)),
                    "description": str(flag.get("description", "")),
                    "stage": str(flag.get("stage", "stable")),
                    "enabled": bool(self._effective_enabled(flag)),
                    "enabledByDefault": bool(flag.get("enabledByDefault", False)),
                }
            )
        return RuntimeResult(
            ok=True,
            message="Feature flags listed.",
            payload={
                "authority": str(self._state.get("authority", "stable")),
                "manifestSource": str(self._manifest.get("source", "")),
                "manifestUrl": str(self._state.get("manifestUrl", "")),
                "flags": items,
                "count": len(items),
            },
        )

    def set_override(self, flag_id: str, enabled: bool) -> RuntimeResult:
        target = str(flag_id or "").strip()
        if not target:
            return RuntimeResult(ok=False, message="Flag id is required.")
        exists = any(str(flag.get("id", "")).strip() == target for flag in self._iter_flags())
        if not exists:
            return RuntimeResult(ok=False, message="Unknown feature flag id.")
        self._state["overrides"][target] = bool(enabled)
        self._save_state()
        return RuntimeResult(
            ok=True,
            message="Feature flag override updated.",
            payload={"flagId": target, "enabled": bool(enabled)},
        )

    def clear_override(self, flag_id: str) -> RuntimeResult:
        target = str(flag_id or "").strip()
        if not target:
            return RuntimeResult(ok=False, message="Flag id is required.")
        self._state["overrides"].pop(target, None)
        self._save_state()
        return RuntimeResult(
            ok=True,
            message="Feature flag override cleared.",
            payload={"flagId": target},
        )

    def set_authority(self, authority: str) -> RuntimeResult:
        requested = str(authority or "").strip().lower()
        if requested not in ("stable", "beta", "internal"):
            return RuntimeResult(ok=False, message="Authority must be stable, beta, or internal.")
        self._state["authority"] = requested
        self._save_state()
        return RuntimeResult(ok=True, message="Authority updated.", payload={"authority": requested})

    def grant_beta_access(self, access_code: str) -> RuntimeResult:
        code = str(access_code or "").strip()
        if not code:
            return RuntimeResult(ok=False, message="Access code is required.")

        digest = self._sha256(code)
        grants = self._manifest.get("grants", [])
        if not isinstance(grants, list):
            grants = []
        grant = next((g for g in grants if isinstance(g, dict) and str(g.get("sha256", "")).strip().lower() == digest), None)
        if grant is None:
            return RuntimeResult(ok=False, message="Access code is invalid.")

        grant_authority = str(grant.get("authority", "beta")).strip().lower() or "beta"
        current_authority = str(self._state.get("authority", "stable")).strip().lower() or "stable"
        if self._rank_for_authority(grant_authority) > self._rank_for_authority(current_authority):
            self._state["authority"] = grant_authority

        enable_flags = grant.get("enableFlags", [])
        if isinstance(enable_flags, list):
            for flag_id in enable_flags:
                self._state["overrides"][str(flag_id)] = True

        self._state["lastGrant"] = str(grant.get("name", ""))
        self._save_state()
        return RuntimeResult(
            ok=True,
            message="Beta access granted.",
            payload={
                "authority": self._state.get("authority", "stable"),
                "grant": str(grant.get("name", "")),
                "enabledFlags": [str(x) for x in enable_flags] if isinstance(enable_flags, list) else [],
            },
        )

    def refresh_manifest(self, *, manifest_url: str = "", timeout_seconds: float = 2.5) -> RuntimeResult:
        requested_url = str(manifest_url or "").strip()
        active_url = requested_url or str(self._state.get("manifestUrl", "")).strip() or self._default_manifest_url
        env_url = str(os.getenv("BITS_EASY_FEATURE_FLAGS_URL", "")).strip()
        if env_url:
            active_url = env_url

        if not active_url:
            self._manifest = self._fallback_manifest()
            return RuntimeResult(
                ok=True,
                message="Feature flag manifest refreshed from fallback (no URL configured).",
                payload={"source": "fallback", "url": ""},
            )

        try:
            req = Request(active_url, headers={"User-Agent": "BITS-EASY/1.0"})
            with urlopen(req, timeout=float(timeout_seconds)) as resp:
                raw = resp.read().decode("utf-8")
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                raise ValueError("Manifest payload is not a JSON object.")
            payload["source"] = "remote"
            self._manifest = payload
            self._write_json(self._cache_path, payload)
            self._state["manifestUrl"] = active_url
            self._save_state()
            return RuntimeResult(
                ok=True,
                message="Feature flag manifest refreshed from remote source.",
                payload={"source": "remote", "url": active_url},
            )
        except Exception:
            cached = self._read_json(self._cache_path)
            if cached:
                cached["source"] = "cache"
                self._manifest = cached
                return RuntimeResult(
                    ok=True,
                    message="Remote manifest unavailable; using cached feature flag manifest.",
                    payload={"source": "cache", "url": active_url},
                )
            self._manifest = self._fallback_manifest()
            return RuntimeResult(
                ok=True,
                message="Remote manifest unavailable; using bundled fallback manifest.",
                payload={"source": "fallback", "url": active_url},
            )
