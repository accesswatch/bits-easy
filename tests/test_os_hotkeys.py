import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from spellforge_runtime import parse_key_chord_for_os


class OsHotkeyTests(unittest.TestCase):
    def test_grave_single_key_supported(self):
        spec = parse_key_chord_for_os("Grave", emulate_capslock_prefix=True)
        self.assertTrue(spec.supported)

    def test_grave_prefix_shortcut_supported(self):
        spec = parse_key_chord_for_os("Grave+F", emulate_capslock_prefix=True)
        self.assertTrue(spec.supported)

    def test_capslock_emulation_parses(self):
        spec = parse_key_chord_for_os("CapsLock+1", emulate_capslock_prefix=True)
        self.assertTrue(spec.supported)
        self.assertNotEqual(spec.modifiers, 0)

    def test_capslock_without_emulation_is_unsupported(self):
        spec = parse_key_chord_for_os("CapsLock+1", emulate_capslock_prefix=False)
        self.assertFalse(spec.supported)

    def test_control_alt_shortcut_supported(self):
        spec = parse_key_chord_for_os("Control+Alt+F", emulate_capslock_prefix=False)
        self.assertTrue(spec.supported)

    def test_f_key_shortcut_supported(self):
        spec = parse_key_chord_for_os("CapsLock+Shift+F12", emulate_capslock_prefix=True)
        self.assertTrue(spec.supported)


if __name__ == "__main__":
    unittest.main()
