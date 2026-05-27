from __future__ import annotations

from pathlib import Path
import os

import addonHandler

addonHandler.initTranslation()

if "_" not in globals():
    def _(message: str) -> str:
        return message


def onInstall():
    appdata_root = Path(os.getenv("APPDATA", ""))
    storage_dir = appdata_root / "BITS-EASY"
    legacy_storage_dir = appdata_root / "BITS-EASY"
    if not storage_dir.exists() and legacy_storage_dir.exists():
        storage_dir = legacy_storage_dir
    storage_dir.mkdir(parents=True, exist_ok=True)


def onUninstall():
    # Keep user data by default.
    return

