import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime import SettingsStore, SpellforgeSettings


class SettingsStoreTests(unittest.TestCase):
    def test_load_defaults_when_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            store = SettingsStore(Path(tmpdir) / "missing.json")
            settings = store.load()
            self.assertEqual(settings.profile_id, "balanced")
            self.assertTrue(settings.enable_command_palette)

    def test_roundtrip_save_load(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "settings.json"
            store = SettingsStore(path)
            store.save(
                SpellforgeSettings(
                    profile_id="expert",
                    announce_surface_mode=False,
                    enable_contextual_fallbacks=True,
                    enable_command_palette=False,
                    slot_default=3,
                    preview_threshold_chars=128,
                )
            )
            loaded = store.load()
            self.assertEqual(loaded.profile_id, "expert")
            self.assertFalse(loaded.announce_surface_mode)
            self.assertFalse(loaded.enable_command_palette)
            self.assertEqual(loaded.slot_default, 3)
            self.assertEqual(loaded.preview_threshold_chars, 128)


if __name__ == "__main__":
    unittest.main()
