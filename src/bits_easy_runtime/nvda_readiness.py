from __future__ import annotations

from typing import Dict, List

from .engine import RuntimeResult


class NvdaReadinessService:
    def baseline(self) -> RuntimeResult:
        assumptions = {
            "osSupport": ["Windows 10 64-bit", "Windows 11 64-bit"],
            "unsupported": ["Windows 8.1", "32-bit Windows", "Windows 10 ARM"],
        }
        return RuntimeResult(ok=True, message="NVDA platform baseline assumptions ready.", payload=assumptions)

    def api_break_checklist(self) -> RuntimeResult:
        checklist = [
            "Manifest minimum and last-tested fields documented.",
            "API deprecations mapped to internal work items.",
            "Build gates: lint, unit, translation, license checks.",
            "Fallback guidance for incompatible add-ons.",
        ]
        return RuntimeResult(ok=True, message="NVDA API break readiness checklist ready.", payload={"items": checklist, "count": len(checklist)})

    def security_alignment(self) -> RuntimeResult:
        workflow = {
            "privateReporting": True,
            "paths": ["GitHub Advisory", "info@nvaccess.org"],
            "severity": ["P1", "P2", "P3"],
            "handoffTemplate": ["reproduction", "impact", "workaround"],
        }
        return RuntimeResult(ok=True, message="NVDA security and disclosure workflow ready.", payload=workflow)
