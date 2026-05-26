import sys
import json
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from bits_easy_runtime import SettingsStore, BitsEasySettings


class SettingsStoreTests(unittest.TestCase):
    def test_load_defaults_when_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SettingsStore(Path(tmpdir) / "missing.json")
            settings = store.load()
            self.assertEqual(settings.profile_id, "balanced")
            self.assertTrue(settings.announce_surface_mode)
            self.assertTrue(settings.enable_contextual_fallbacks)
            self.assertTrue(settings.enable_command_palette)
            self.assertTrue(settings.enable_global_hotkeys)
            self.assertTrue(settings.emulate_capslock_prefix_for_os_hotkeys)
            self.assertTrue(settings.enable_multi_press_gestures)

    def test_roundtrip_save_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "settings.json"
            store = SettingsStore(path)
            store.save(
                BitsEasySettings(
                    profile_id="expert",
                    announce_surface_mode=False,
                    enable_contextual_fallbacks=True,
                    enable_command_palette=False,
                    slot_default=3,
                    preview_threshold_chars=128,
                    active_mode="focusMode",
                    custom_modes={
                        "focusMode": {
                            "baseProfile": "expert",
                            "overrides": {
                                "enable_command_palette": False,
                                "enable_multi_press_gestures": True,
                            },
                            "hotkeyBindings": [
                                {
                                    "commandId": "cmd.help.availableHotkeys",
                                    "keyChord": "GRAVE+H",
                                    "scope": "global",
                                    "enabled": True,
                                }
                            ],
                        }
                    },
                )
            )
            loaded = store.load()
            self.assertEqual(loaded.profile_id, "expert")
            self.assertFalse(loaded.announce_surface_mode)
            self.assertFalse(loaded.enable_command_palette)
            self.assertEqual(loaded.slot_default, 3)
            self.assertEqual(loaded.preview_threshold_chars, 128)
            self.assertEqual(loaded.active_mode, "focusMode")
            self.assertIn("focusMode", loaded.custom_modes)

    def test_legacy_settings_missing_palette_flag_defaults_enabled(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "settings.json"
            path.write_text(
                json.dumps(
                    {
                        "profile_id": "balanced",
                        "announce_surface_mode": True,
                        "enable_contextual_fallbacks": True,
                        "slot_default": 1,
                        "preview_threshold_chars": 240,
                    }
                ),
                encoding="utf-8",
            )
            store = SettingsStore(path)
            settings = store.load()
            self.assertTrue(settings.enable_command_palette)
            self.assertTrue(settings.enable_global_hotkeys)
            self.assertTrue(settings.emulate_capslock_prefix_for_os_hotkeys)
            self.assertTrue(settings.enable_multi_press_gestures)
            self.assertEqual(settings.active_mode, "")
            self.assertEqual(settings.custom_modes, {})


if __name__ == "__main__":
    unittest.main()

