import json
import sys
import tempfile
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime import AppAdapter, AppContext, RuntimeDispatcher, BitsEasyRuntime, load_runtime_config
from bits_easy_runtime.feature_flags import FeatureFlagManager


class FeatureFlagTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_root = Path(__file__).resolve().parents[1]
        self.config = load_runtime_config(self.repo_root)
        self.runtime = BitsEasyRuntime(adapters={"edge": AppAdapter("edge", supports_selection=True)})
        self.ctx = AppContext(
            app_id="edge",
            window_id="win-edge",
            control_id="main-editor",
            buffer="alpha bravo",
            caret=0,
            clipboard_text="",
        )

    def test_beta_flagged_command_blocked_until_granted(self):
        with tempfile.TemporaryDirectory() as td:
            dispatcher = RuntimeDispatcher(
                runtime=self.runtime,
                config=self.config,
                profile_id="balanced",
                data_root=Path(td),
            )

            blocked = dispatcher.dispatch_command(self.ctx, "cmd.emoji.list")
            self.assertFalse(blocked.result.ok)
            self.assertEqual((blocked.result.payload or {}).get("featureGate", {}).get("reason"), "flag-disabled")

            grant = dispatcher.dispatch_command(
                self.ctx,
                "cmd.feature.flags.grantBeta",
                accessCode="BITS-EASY-BETA-2026",
            )
            self.assertTrue(grant.result.ok)

            enabled = dispatcher.dispatch_command(self.ctx, "cmd.emoji.list")
            self.assertTrue(enabled.result.ok)
            self.assertGreaterEqual((enabled.result.payload or {}).get("count", 0), 1)

    def test_disabled_feature_keybindings_are_filtered(self):
        with tempfile.TemporaryDirectory() as td:
            dispatcher = RuntimeDispatcher(
                runtime=self.runtime,
                config=self.config,
                profile_id="balanced",
                data_root=Path(td),
            )

            bindings = [
                {"commandId": "cmd.emoji.list", "keyChord": "Grave+Shift+M", "enabled": True},
                {"commandId": "cmd.palette.open", "keyChord": "NVDA+Shift+P", "enabled": True},
            ]

            filtered_before = dispatcher.enabled_keymap_bindings(bindings)
            self.assertEqual(len(filtered_before), 1)
            self.assertEqual(filtered_before[0]["commandId"], "cmd.palette.open")

            grant = dispatcher.dispatch_command(
                self.ctx,
                "cmd.feature.flags.grantBeta",
                accessCode="BITS-EASY-BETA-2026",
            )
            self.assertTrue(grant.result.ok)

            filtered_after = dispatcher.enabled_keymap_bindings(bindings)
            self.assertEqual(len(filtered_after), 2)

    def test_remote_manifest_falls_back_to_bundled_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            fallback_manifest = td_path / "fallback.json"
            fallback_manifest.write_text(
                json.dumps(
                    {
                        "version": "1",
                        "authorityStages": {
                            "stable": ["stable"],
                            "beta": ["stable", "beta"],
                            "internal": ["stable", "beta", "experimental"],
                        },
                        "flags": [],
                        "grants": [],
                    }
                ),
                encoding="utf-8",
            )

            manager = FeatureFlagManager(
                state_path=td_path / "state.json",
                cache_path=td_path / "cache.json",
                fallback_manifest_path=fallback_manifest,
                default_manifest_url="https://127.0.0.1:9/manifest.json",
            )
            refreshed = manager.refresh_manifest(timeout_seconds=0.1)
            self.assertTrue(refreshed.ok)
            self.assertIn((refreshed.payload or {}).get("source"), ("fallback", "cache"))

    def test_refresh_manifest_reports_changes_from_previous_snapshot(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            fallback_manifest = td_path / "fallback.json"
            fallback_manifest.write_text(
                json.dumps(
                    {
                        "version": "1",
                        "authorityStages": {
                            "stable": ["stable"],
                            "beta": ["stable", "beta"],
                            "internal": ["stable", "beta", "experimental"],
                        },
                        "flags": [
                            {
                                "id": "flag.alpha",
                                "stage": "beta",
                                "enabledByDefault": False,
                                "commandIds": ["cmd.alpha"],
                            }
                        ],
                        "grants": [],
                    }
                ),
                encoding="utf-8",
            )

            manager = FeatureFlagManager(
                state_path=td_path / "state.json",
                cache_path=td_path / "cache.json",
                fallback_manifest_path=fallback_manifest,
                default_manifest_url="https://127.0.0.1:9/manifest.json",
            )
            first = manager.refresh_manifest(timeout_seconds=0.1)
            self.assertTrue(first.ok)
            self.assertFalse((first.payload or {}).get("updatesAvailable"))

            cache_manifest = {
                "version": "1",
                "authorityStages": {
                    "stable": ["stable"],
                    "beta": ["stable", "beta"],
                    "internal": ["stable", "beta", "experimental"],
                },
                "flags": [
                    {
                        "id": "flag.alpha",
                        "stage": "beta",
                        "enabledByDefault": True,
                        "commandIds": ["cmd.alpha"],
                    },
                    {
                        "id": "flag.beta",
                        "stage": "beta",
                        "enabledByDefault": False,
                        "commandIds": ["cmd.beta"],
                    },
                ],
                "grants": [],
            }
            (td_path / "cache.json").write_text(json.dumps(cache_manifest), encoding="utf-8")
            refreshed = manager.refresh_manifest(timeout_seconds=0.1)
            self.assertTrue(refreshed.ok)

            changes = (refreshed.payload or {}).get("changes", {})
            self.assertTrue((refreshed.payload or {}).get("updatesAvailable"))
            self.assertEqual(len(changes.get("newFlags", [])), 1)
            self.assertEqual(changes.get("newFlags", [])[0].get("id"), "flag.beta")
            self.assertEqual(len(changes.get("changedFlags", [])), 1)
            self.assertEqual(changes.get("changedFlags", [])[0].get("id"), "flag.alpha")

    def test_set_overrides_updates_multiple_flags(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            fallback_manifest = td_path / "fallback.json"
            fallback_manifest.write_text(
                json.dumps(
                    {
                        "version": "1",
                        "authorityStages": {
                            "stable": ["stable"],
                            "beta": ["stable", "beta"],
                            "internal": ["stable", "beta", "experimental"],
                        },
                        "flags": [
                            {"id": "flag.alpha", "stage": "beta", "enabledByDefault": False},
                            {"id": "flag.beta", "stage": "beta", "enabledByDefault": False},
                        ],
                        "grants": [],
                    }
                ),
                encoding="utf-8",
            )

            manager = FeatureFlagManager(
                state_path=td_path / "state.json",
                cache_path=td_path / "cache.json",
                fallback_manifest_path=fallback_manifest,
            )
            updated = manager.set_overrides({"flag.alpha": True, "flag.beta": True})
            self.assertTrue(updated.ok)
            listed = manager.list_flags()
            rows = {row.get("id"): row for row in (listed.payload or {}).get("flags", [])}
            self.assertTrue(rows.get("flag.alpha", {}).get("enabled"))
            self.assertTrue(rows.get("flag.beta", {}).get("enabled"))


if __name__ == "__main__":
    unittest.main()
