import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "addon"))

from bits_easy_runtime import BitsEasySettings, apply_active_mode, effective_keymap_bindings
from bits_easy_settings import (
    build_mode_payload,
    mode_hotkeys_for_editor,
    remove_custom_mode,
    upsert_custom_mode,
    with_mode_hotkey_bindings,
)


class ControlPanelModeTests(unittest.TestCase):
    def test_mode_crud_helpers(self):
        settings = BitsEasySettings(profile_id="balanced")
        payload = build_mode_payload(settings)

        modes = {}
        modes = upsert_custom_mode(modes, "focus", payload)
        self.assertIn("focus", modes)

        modes = upsert_custom_mode(
            modes,
            "focus",
            {
                "baseProfile": "expert",
                "overrides": {"enable_command_palette": False},
            },
        )
        self.assertEqual(modes["focus"]["baseProfile"], "expert")

        modes, active_mode = remove_custom_mode(modes, "focus", "focus")
        self.assertNotIn("focus", modes)
        self.assertEqual(active_mode, "")

    def test_apply_active_mode_and_hotkey_layer(self):
        settings = BitsEasySettings(
            profile_id="beginner",
            enable_command_palette=True,
            enable_multi_press_gestures=True,
            active_mode="coding",
            custom_modes={
                "coding": {
                    "baseProfile": "expert",
                    "overrides": {
                        "enable_command_palette": False,
                        "enable_multi_press_gestures": False,
                        "enable_raw_easy_sequences": True,
                        "raw_easy_sequence_timeout_ms": 1200,
                        "enable_contextual_fallbacks": True,
                        "announce_surface_mode": False,
                        "enable_global_hotkeys": True,
                    },
                    "hotkeyBindings": [
                        {
                            "commandId": "cmd.help.availableHotkeys",
                            "keyChord": "GRAVE+QUESTION",
                            "scope": "global",
                            "enabled": True,
                        }
                    ],
                }
            },
        )

        mode_hotkeys = apply_active_mode(settings)
        self.assertEqual(settings.profile_id, "expert")
        self.assertFalse(settings.enable_command_palette)
        self.assertFalse(settings.enable_multi_press_gestures)
        self.assertEqual(settings.raw_easy_sequence_timeout_ms, 1200)
        self.assertIsInstance(mode_hotkeys, list)
        self.assertEqual(len(mode_hotkeys), 1)

        base_bindings = [
            {
                "commandId": "cmd.tags.session.toggle",
                "keyChord": "GRAVE+ALT+G",
                "scope": "global",
                "enabled": True,
            }
        ]
        effective = effective_keymap_bindings(base_bindings, mode_hotkeys)
        self.assertEqual(len(effective), 1)
        self.assertEqual(effective[0]["commandId"], "cmd.help.availableHotkeys")

    def test_build_mode_payload_can_include_hotkeys(self):
        settings = BitsEasySettings(profile_id="balanced")
        payload = build_mode_payload(
            settings,
            hotkey_bindings=[
                {
                    "commandId": "cmd.help.availableHotkeys",
                    "keyChord": "GRAVE+QUESTION",
                    "scope": "global",
                    "enabled": True,
                }
            ],
        )
        self.assertIn("hotkeyBindings", payload)
        self.assertEqual(len(payload["hotkeyBindings"]), 1)

    def test_mode_hotkeys_for_editor_prefers_mode_hotkeys(self):
        mode_payload = {
            "hotkeyBindings": [
                {
                    "commandId": "cmd.help.availableHotkeys",
                    "keyChord": "GRAVE+QUESTION",
                    "scope": "global",
                    "enabled": True,
                }
            ]
        }
        fallback_bindings = [
            {
                "commandId": "cmd.tags.session.toggle",
                "keyChord": "GRAVE+ALT+G",
                "scope": "global",
                "enabled": True,
            }
        ]

        editor_rows = mode_hotkeys_for_editor(mode_payload, fallback_bindings)
        self.assertEqual(len(editor_rows), 1)
        self.assertEqual(editor_rows[0]["commandId"], "cmd.help.availableHotkeys")

    def test_with_mode_hotkey_bindings_stores_in_mode_payload(self):
        modes = {
            "focus": {
                "baseProfile": "balanced",
                "overrides": {"enable_command_palette": True},
            }
        }
        new_bindings = [
            {
                "commandId": "cmd.help.availableHotkeys",
                "keyChord": "GRAVE+QUESTION",
                "scope": "global",
                "enabled": True,
            }
        ]

        updated = with_mode_hotkey_bindings(modes, "focus", new_bindings)
        self.assertIn("focus", updated)
        self.assertIn("hotkeyBindings", updated["focus"])
        self.assertEqual(updated["focus"]["hotkeyBindings"][0]["commandId"], "cmd.help.availableHotkeys")

        settings = BitsEasySettings(profile_id="beginner", active_mode="focus", custom_modes=updated)
        mode_hotkeys = apply_active_mode(settings)
        effective = effective_keymap_bindings([], mode_hotkeys)
        self.assertEqual(len(effective), 1)
        self.assertEqual(effective[0]["commandId"], "cmd.help.availableHotkeys")


if __name__ == "__main__":
    unittest.main()
