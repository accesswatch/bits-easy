from __future__ import annotations

from pathlib import Path
import os


def onInstall():
    storage_dir = Path(os.getenv("APPDATA", "")) / "Spellforge"
    storage_dir.mkdir(parents=True, exist_ok=True)


def onUninstall():
    # Keep user data by default.
    return
