import json
import tempfile
import unittest
from pathlib import Path

from bits_easy_runtime.health import IntegrationHealthTracker
from bits_easy_runtime.portability import export_portability_bundle, import_portability_bundle


class PortabilityHealthTests(unittest.TestCase):
    def test_health_tracker_report(self):
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "health.jsonl"
            tracker = IntegrationHealthTracker(log)
            tracker.record("word", "cmd.a", True)
            tracker.record("word", "cmd.b", False, "adapter-miss")
            report = tracker.report()
            self.assertEqual(report.total_commands, 2)
            self.assertEqual(report.failure_count, 1)
            self.assertGreaterEqual(report.success_rate, 0.0)

    def test_portability_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "config" / "hotkeys" / "profiles").mkdir(parents=True)
            (repo / "config" / "hotkeys" / "commands").mkdir(parents=True)

            for name in ("beginner", "balanced", "expert"):
                (repo / "config" / "hotkeys" / "profiles" / f"{name}.json").write_text(
                    json.dumps({"id": name}), encoding="utf-8"
                )

            (repo / "config" / "hotkeys" / "global-keymap.v1.json").write_text(
                json.dumps({"bindings": []}), encoding="utf-8"
            )
            (repo / "config" / "hotkeys" / "commands" / "tier1-commands.v1.json").write_text(
                json.dumps([]), encoding="utf-8"
            )

            bundle = repo / "bundle.json"
            export_portability_bundle(repo, bundle)
            self.assertTrue(bundle.exists())

            restored = import_portability_bundle(repo, bundle, overwrite_existing=True)
            self.assertGreaterEqual(restored["profiles"], 1)

            # Existing files should be preserved when overwrite is disabled.
            (repo / "config" / "hotkeys" / "profiles" / "beginner.json").write_text(
                json.dumps({"id": "beginner", "local": True}), encoding="utf-8"
            )
            restored_conflict = import_portability_bundle(repo, bundle, overwrite_existing=False)
            self.assertGreaterEqual(restored_conflict["conflicts"], 1)

    def test_portability_integrity_rejects_tamper(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "config" / "hotkeys" / "profiles").mkdir(parents=True)
            (repo / "config" / "hotkeys" / "commands").mkdir(parents=True)
            for name in ("beginner", "balanced", "expert"):
                (repo / "config" / "hotkeys" / "profiles" / f"{name}.json").write_text(json.dumps({"id": name}), encoding="utf-8")
            (repo / "config" / "hotkeys" / "global-keymap.v1.json").write_text(json.dumps({"bindings": []}), encoding="utf-8")
            (repo / "config" / "hotkeys" / "commands" / "tier1-commands.v1.json").write_text(json.dumps([]), encoding="utf-8")

            bundle = repo / "bundle.json"
            export_portability_bundle(repo, bundle)
            payload = json.loads(bundle.read_text(encoding="utf-8"))
            payload["profiles"]["beginner"]["tampered"] = True
            bundle.write_text(json.dumps(payload, indent=2), encoding="utf-8")

            with self.assertRaises(ValueError):
                import_portability_bundle(repo, bundle)


if __name__ == "__main__":
    unittest.main()

