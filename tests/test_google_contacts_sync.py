import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime.google_contacts_sync import GoogleContact, GoogleContactsSync


class GoogleContactsSyncTests(unittest.TestCase):
    def test_sync_dry_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sync = GoogleContactsSync(
                credentials_path=Path(tmpdir) / "credentials.json",
                token_path=Path(tmpdir) / "token.json",
            )
            contacts = [GoogleContact(given_name="Jane", family_name="Doe", email="jane@example.com", phone="555-0101")]
            out = sync.sync_contacts(contacts, dry_run=True)
            self.assertTrue(out.ok)
            self.assertEqual(out.payload["mode"], "dry-run")


if __name__ == "__main__":
    unittest.main()

