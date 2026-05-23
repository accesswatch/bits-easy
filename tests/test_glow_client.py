import json
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime.glow_client import GlowMcpService


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class GlowClientTests(unittest.TestCase):
    def test_health_success(self) -> None:
        client = GlowMcpService("http://127.0.0.1:8000")
        with patch("spellforge_runtime.glow_client.request.urlopen", return_value=_FakeResponse({"status": "ok"})):
            out = client.health()
        self.assertTrue(out.ok)
        self.assertEqual((out.payload or {}).get("status"), "ok")

    def test_audit_missing_file(self) -> None:
        client = GlowMcpService("http://127.0.0.1:8000")
        out = client.audit(Path("Z:/does-not-exist.docx"), fmt="docx")
        self.assertFalse(out.ok)
        self.assertIn("file not found", out.message.lower())

    def test_convert_posts_and_returns_payload(self) -> None:
        client = GlowMcpService("http://127.0.0.1:8000")
        with tempfile.TemporaryDirectory() as tmpdir:
            src = Path(tmpdir) / "sample.docx"
            src.write_bytes(b"doc")
            with patch(
                "spellforge_runtime.glow_client.request.urlopen",
                return_value=_FakeResponse({"output_file": "x.md", "converted_text": "# hi"}),
            ):
                out = client.convert(src, from_format="docx", to_format="markdown")

        self.assertTrue(out.ok)
        self.assertEqual((out.payload or {}).get("output_file"), "x.md")


if __name__ == "__main__":
    unittest.main()
