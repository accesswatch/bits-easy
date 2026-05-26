from __future__ import annotations

import json
import mimetypes
import os
import uuid
from pathlib import Path
from typing import Any, Dict, Tuple
from urllib import error, request

from .engine import RuntimeResult


class GlowMcpService:
    def __init__(self, endpoint: str = ""):
        raw = endpoint.strip() or os.getenv("GLOW_MCP_URL", "http://127.0.0.1:8000")
        self._endpoint = raw.rstrip("/")

    @property
    def endpoint(self) -> str:
        return self._endpoint

    @staticmethod
    def _multipart_body(fields: Dict[str, str], file_field: Tuple[str, Path]) -> Tuple[bytes, str]:
        file_name, file_path = file_field
        boundary = f"----BITS-EASYGlow{uuid.uuid4().hex}"
        chunks: list[bytes] = []

        for name, value in fields.items():
            chunks.append(f"--{boundary}\r\n".encode("utf-8"))
            chunks.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
            chunks.append(str(value).encode("utf-8"))
            chunks.append(b"\r\n")

        file_bytes = file_path.read_bytes()
        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        chunks.append(f"--{boundary}\r\n".encode("utf-8"))
        chunks.append(
            (
                f'Content-Disposition: form-data; name="{file_name}"; '
                f'filename="{file_path.name}"\r\n'
            ).encode("utf-8")
        )
        chunks.append(f"Content-Type: {content_type}\r\n\r\n".encode("utf-8"))
        chunks.append(file_bytes)
        chunks.append(b"\r\n")
        chunks.append(f"--{boundary}--\r\n".encode("utf-8"))

        return b"".join(chunks), boundary

    def _post_file(self, route: str, fields: Dict[str, str], file_path: Path) -> RuntimeResult:
        if not file_path.exists() or not file_path.is_file():
            return RuntimeResult(ok=False, message=f"GLOW file not found: {file_path}")

        body, boundary = self._multipart_body(fields, ("file", file_path))
        req = request.Request(
            url=f"{self._endpoint}{route}",
            data=body,
            method="POST",
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        try:
            with request.urlopen(req, timeout=45) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                payload = json.loads(raw) if raw.strip() else {}
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            return RuntimeResult(ok=False, message=f"GLOW request failed ({exc.code}): {detail}")
        except error.URLError as exc:
            return RuntimeResult(ok=False, message=f"GLOW server unreachable at {self._endpoint}: {exc.reason}")
        except Exception as exc:
            return RuntimeResult(ok=False, message=f"GLOW request failed: {exc}")

        if isinstance(payload, dict) and payload.get("error"):
            return RuntimeResult(ok=False, message=f"GLOW error: {payload.get('error')}")

        return RuntimeResult(ok=True, message="GLOW request completed.", payload=payload if isinstance(payload, dict) else {"raw": payload})

    def health(self) -> RuntimeResult:
        req = request.Request(url=f"{self._endpoint}/health", method="GET")
        try:
            with request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
                payload = json.loads(raw) if raw.strip() else {}
        except Exception as exc:
            return RuntimeResult(ok=False, message=f"GLOW server unreachable at {self._endpoint}: {exc}")
        return RuntimeResult(ok=True, message="GLOW health check complete.", payload=payload if isinstance(payload, dict) else {"raw": payload})

    @staticmethod
    def _infer_format(path: Path) -> str:
        suffix = path.suffix.lower().lstrip(".")
        if suffix in ("md", "markdown"):
            return "markdown"
        if suffix in ("html", "htm"):
            return "html"
        if suffix == "docx":
            return "docx"
        return suffix or "docx"

    def audit(self, file_path: Path, fmt: str = "") -> RuntimeResult:
        form = fmt.strip() or self._infer_format(file_path)
        return self._post_file("/audit", {"format": form}, file_path)

    def fix(self, file_path: Path, fmt: str = "") -> RuntimeResult:
        form = fmt.strip() or self._infer_format(file_path)
        return self._post_file("/fix", {"format": form}, file_path)

    def report(self, file_path: Path, fmt: str = "", report_type: str = "json") -> RuntimeResult:
        form = fmt.strip() or self._infer_format(file_path)
        return self._post_file("/report", {"format": form, "report_type": report_type}, file_path)

    def convert(self, file_path: Path, from_format: str = "", to_format: str = "markdown") -> RuntimeResult:
        from_fmt = from_format.strip() or self._infer_format(file_path)
        to_fmt = to_format.strip() or "markdown"
        return self._post_file("/convert", {"from_format": from_fmt, "to_format": to_fmt}, file_path)

