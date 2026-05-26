from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
from typing import List

from .engine import RuntimeResult
from .tagging import TaggingSession


class FileOpsService:
    def __init__(self, tagging: TaggingSession):
        self._tagging = tagging

    def browse(self, path: str, *, include_hidden: bool = False) -> RuntimeResult:
        target = Path(path)
        if not target.exists():
            return RuntimeResult(ok=False, message="Path was not found.")
        if target.is_file():
            stat = target.stat()
            return RuntimeResult(
                ok=True,
                message="File details ready.",
                payload={
                    "type": "file",
                    "path": str(target),
                    "name": target.name,
                    "size": stat.st_size,
                },
            )
        items = []
        for child in sorted(target.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
            if not include_hidden and child.name.startswith("."):
                continue
            items.append(
                {
                    "name": child.name,
                    "path": str(child),
                    "type": "file" if child.is_file() else "directory",
                }
            )
        return RuntimeResult(ok=True, message="Directory listing ready.", payload={"type": "directory", "path": str(target), "items": items, "count": len(items)})

    @staticmethod
    def _risk_tier(path: Path) -> str:
        lowered = str(path).lower()
        if "windows" in lowered or "system32" in lowered:
            return "high"
        if path.suffix.lower() in (".exe", ".dll", ".sys"):
            return "high"
        return "low"

    def copy(self, source: str, destination: str, *, confirm: bool) -> RuntimeResult:
        src = Path(source)
        dst = Path(destination)
        if not src.exists():
            return RuntimeResult(ok=False, message="Source path was not found.")
        risk = self._risk_tier(src)
        if risk == "high" and not confirm:
            return RuntimeResult(ok=False, message="High-risk copy requires confirmation.", payload={"riskTier": risk})
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            if dst.exists():
                return RuntimeResult(ok=False, message="Destination already exists for directory copy.")
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        return RuntimeResult(ok=True, message="Copy completed.", payload={"source": str(src), "destination": str(dst), "riskTier": risk})

    def move(self, source: str, destination: str, *, confirm: bool) -> RuntimeResult:
        src = Path(source)
        dst = Path(destination)
        if not src.exists():
            return RuntimeResult(ok=False, message="Source path was not found.")
        risk = self._risk_tier(src)
        if risk == "high" and not confirm:
            return RuntimeResult(ok=False, message="High-risk move requires confirmation.", payload={"riskTier": risk})
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return RuntimeResult(ok=True, message="Move completed.", payload={"source": str(src), "destination": str(dst), "riskTier": risk})

    def rename(self, path: str, new_name: str, *, confirm: bool) -> RuntimeResult:
        src = Path(path)
        if not src.exists():
            return RuntimeResult(ok=False, message="Path was not found.")
        name = new_name.strip()
        if not name:
            return RuntimeResult(ok=False, message="New name is required.")
        risk = self._risk_tier(src)
        if risk == "high" and not confirm:
            return RuntimeResult(ok=False, message="High-risk rename requires confirmation.", payload={"riskTier": risk})
        dst = src.with_name(name)
        src.rename(dst)
        return RuntimeResult(ok=True, message="Rename completed.", payload={"path": str(dst), "riskTier": risk})

    def delete(self, path: str, *, confirm: bool) -> RuntimeResult:
        target = Path(path)
        if not target.exists():
            return RuntimeResult(ok=False, message="Path was not found.")
        risk = self._risk_tier(target)
        if not confirm:
            return RuntimeResult(ok=False, message="Delete requires confirmation.", payload={"riskTier": risk})
        if target.is_dir():
            shutil.rmtree(target)
        else:
            target.unlink()
        return RuntimeResult(ok=True, message="Delete completed.", payload={"path": str(path), "riskTier": risk})

    def zip_create(self, sources: List[str], out_path: str) -> RuntimeResult:
        if not sources:
            return RuntimeResult(ok=False, message="At least one source path is required.")
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for raw in sources:
                src = Path(raw)
                if not src.exists():
                    continue
                if src.is_file():
                    archive.write(src, arcname=src.name)
                else:
                    for child in src.rglob("*"):
                        if child.is_file():
                            archive.write(child, arcname=str(child.relative_to(src.parent)))
        return RuntimeResult(ok=True, message="Zip archive created.", payload={"path": str(out), "sourceCount": len(sources)})

    def copy_full_path(self, path: str) -> RuntimeResult:
        target = Path(path)
        if not target.exists():
            return RuntimeResult(ok=False, message="Path was not found.")
        return RuntimeResult(ok=True, message="Full path ready.", payload={"path": str(target.resolve()), "insertText": str(target.resolve())})

    def tag_batch(self, paths: List[str]) -> RuntimeResult:
        tagged = []
        for raw in paths:
            out = self._tagging.tag(raw)
            if out.ok:
                tagged.append(raw)
        return RuntimeResult(ok=True, message="Tagged file batch ready.", payload={"count": len(tagged), "items": tagged})
