import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime.google_calendar_sync import GoogleCalendarSync


class GoogleCalendarSyncTests(unittest.TestCase):
    def test_sync_dry_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sync = GoogleCalendarSync(
                credentials_path=Path(tmpdir) / "credentials.json",
                token_path=Path(tmpdir) / "token.json",
                calendar_id="primary",
            )
            event = GoogleCalendarSync.sample_event("Focus Block")
            out = sync.sync_events([event], dry_run=True)
            self.assertTrue(out.ok)
            self.assertEqual(out.payload["mode"], "dry-run")


if __name__ == "__main__":
    unittest.main()

