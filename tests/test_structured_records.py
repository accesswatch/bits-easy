import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime.structured_records import StructuredRecordService


class StructuredRecordServiceTests(unittest.TestCase):
    def test_database_lifecycle_and_restore(self):
        svc = StructuredRecordService()
        self.assertTrue(svc.create_database("People").ok)
        self.assertTrue(svc.select_database("People").ok)
        self.assertFalse(svc.delete_database("People", confirm=False).ok)
        self.assertTrue(svc.delete_database("People", confirm=True).ok)
        self.assertTrue(svc.restore_database("People").ok)

    def test_field_validation_entry_and_export(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            svc = StructuredRecordService(Path(tmpdir) / "records.json")
            svc.create_database("crm")
            svc.define_field("email", field_type="text", required=True, validator="email")
            svc.define_field("score", field_type="number", required=False)

            bad = svc.add_entry({"email": "not-an-email", "score": "x"})
            self.assertFalse(bad.ok)

            good = svc.add_entry({"email": "a@b.com", "score": "42"})
            self.assertTrue(good.ok)
            eid = good.payload["entryId"]

            detail = svc.entry_detail(eid)
            self.assertTrue(detail.ok)

            found = svc.search_entries("email", "a@b")
            self.assertEqual(found.payload["count"], 1)

            sorted_rows = svc.sort_entries("email")
            self.assertGreaterEqual(sorted_rows.payload["count"], 1)

            csv_out = Path(tmpdir) / "out.csv"
            txt_out = Path(tmpdir) / "out.txt"
            self.assertTrue(svc.export_csv(csv_out).ok)
            self.assertTrue(svc.export_text(txt_out).ok)
            self.assertTrue(csv_out.exists())
            self.assertTrue(txt_out.exists())

    def test_jamal_bridge_import_export_launch_sync(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            svc = StructuredRecordService(Path(tmpdir) / "records.json")
            svc.create_database("inventory")
            svc.define_field("name", field_type="text", required=True)
            svc.add_entry({"name": "item-a"})

            export_path = Path(tmpdir) / "jamal.json"
            self.assertTrue(svc.jamal_export(export_path).ok)

            launched = svc.jamal_launch(export_path)
            self.assertTrue(launched.ok)
            self.assertTrue(svc.jamal_return().ok)

            imported = svc.jamal_import(export_path, database_name="imported")
            self.assertTrue(imported.ok)

            dry = svc.jamal_sync([{"entryId": "rec-00001", "values": {"name": "item-b"}}], apply=False)
            self.assertTrue(dry.ok)
            self.assertGreaterEqual(dry.payload["conflictCount"], 0)

            applied = svc.jamal_sync([{"entryId": "rec-00001", "values": {"name": "item-b"}}], apply=True)
            self.assertTrue(applied.ok)


if __name__ == "__main__":
    unittest.main()
