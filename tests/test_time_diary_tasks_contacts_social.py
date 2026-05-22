import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime.contacts_social import ContactsSocialService
from spellforge_runtime.google_calendar_sync import GoogleCalendarSync
from spellforge_runtime.google_contacts_sync import GoogleContactsSync
from spellforge_runtime.tasks_calendar import TaskIcsBridge
from spellforge_runtime.time_diary import TimeDiaryService


class TimeDiaryTasksContactsTests(unittest.TestCase):
    def test_time_diary_and_date_math(self):
        svc = TimeDiaryService()
        self.assertTrue(svc.speak_time().ok)
        self.assertTrue(svc.insert_date().ok)

        start = svc.stopwatch_start()
        self.assertTrue(start.ok)
        elapsed = svc.stopwatch_elapsed()
        self.assertTrue(elapsed.ok)

        dow = svc.day_of_week("2026-05-21")
        self.assertTrue(dow.ok)
        plus = svc.date_add_days("2026-05-21", 10)
        self.assertEqual(plus.payload["resultDate"], "2026-05-31")

    def test_diary_and_tasks_with_ics_and_google_calendar_dry_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            diary = TimeDiaryService(Path(tmpdir) / "diary.json")
            apt = diary.appointment_create("Standup", "2026-05-21T14:00:00+00:00")
            self.assertTrue(apt.ok)
            month = diary.appointment_list_month(2026, 5)
            self.assertGreaterEqual(month.payload["count"], 1)

            calendar_sync = GoogleCalendarSync(Path(tmpdir) / "creds.json", Path(tmpdir) / "token.json")
            tasks = TaskIcsBridge(Path(tmpdir) / "tasks.json", calendar_sync=calendar_sync)
            due = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
            created = tasks.create_task("Prepare notes", due, category="work", priority="high")
            self.assertTrue(created.ok)

            listed = tasks.list_tasks(status="open", category="work", priority="high")
            self.assertEqual(listed.payload["count"], 1)

            ics_path = Path(tmpdir) / "tasks.ics"
            exported = tasks.export_ics(ics_path)
            self.assertTrue(exported.ok)
            self.assertTrue(ics_path.exists())

            synced = tasks.sync_to_google_calendar(dry_run=True)
            self.assertTrue(synced.ok)
            self.assertEqual(synced.payload["mode"], "dry-run")

    def test_contacts_and_social_and_google_contacts_dry_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            contacts_sync = GoogleContactsSync(Path(tmpdir) / "creds.json", Path(tmpdir) / "token.json")
            svc = ContactsSocialService(Path(tmpdir) / "contacts.json", google_sync=contacts_sync)

            created = svc.create_contact("Jane Doe", "jane@example.com", "555-0101")
            self.assertTrue(created.ok)
            cid = created.payload["contactId"]

            found = svc.search_contacts("jane")
            self.assertEqual(found.payload["count"], 1)

            inserted = svc.insert_field(cid, "email")
            self.assertEqual(inserted.payload["insertText"], "jane@example.com")

            copied = svc.copy_field(cid, "phone")
            self.assertEqual(copied.payload["clipboardText"], "555-0101")

            gsync = svc.sync_google_contacts(dry_run=True)
            self.assertTrue(gsync.ok)
            self.assertEqual(gsync.payload["mode"], "dry-run")

            self.assertTrue(svc.mail_extract_sender("Jane", "jane@example.com").ok)
            self.assertTrue(svc.whatsapp_voice_control("send").ok)
            self.assertTrue(svc.x_timeline(["a", "b"], 1).ok)
            self.assertTrue(svc.nickname_upsert("Jane Doe", "JD").ok)
            replaced = svc.nickname_replace("Jane Doe pinged you")
            self.assertIn("JD", replaced.payload["text"])


if __name__ == "__main__":
    unittest.main()
