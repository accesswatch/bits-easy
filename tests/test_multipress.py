import unittest

from bits_easy_runtime.multipress import MultiPressResolver


class MultiPressResolverTests(unittest.TestCase):
    def test_double_press_wins_over_single(self):
        resolver = MultiPressResolver(
            [
                {"keyChord": "CapsLock+X", "commandId": "cmd.one", "trigger": {"kind": "single-press"}},
                {"keyChord": "CapsLock+X", "commandId": "cmd.two", "trigger": {"kind": "double-press"}},
            ]
        )
        resolved = resolver.resolve("CapsLock+X", 2)
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.matched_command_id, "cmd.two")

    def test_emergency_stop_precedence(self):
        resolver = MultiPressResolver(
            [
                {"keyChord": "CapsLock+Esc", "commandId": "cmd.any", "trigger": {"kind": "double-press"}},
                {"keyChord": "CapsLock+Esc", "commandId": "cmd.system.emergencyStop", "trigger": {"kind": "single-press"}},
            ]
        )
        resolved = resolver.resolve("CapsLock+Esc", 3)
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.matched_command_id, "cmd.system.emergencyStop")

    def test_press_and_hold_resolution(self):
        resolver = MultiPressResolver(
            [
                {"keyChord": "CapsLock+Space", "commandId": "cmd.single", "trigger": {"kind": "single-press"}},
                {
                    "keyChord": "CapsLock+Space",
                    "commandId": "cmd.hold",
                    "trigger": {"kind": "press-and-hold", "holdThresholdMs": 500},
                },
            ]
        )
        resolved = resolver.resolve("CapsLock+Space", 1, hold_duration_ms=700)
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.matched_command_id, "cmd.hold")
        self.assertEqual(resolved.trigger_kind, "press-and-hold")

    def test_multi_press_disabled_forces_single(self):
        resolver = MultiPressResolver(
            [
                {"keyChord": "CapsLock+X", "commandId": "cmd.single", "trigger": {"kind": "single-press"}},
                {"keyChord": "CapsLock+X", "commandId": "cmd.double", "trigger": {"kind": "double-press"}},
            ]
        )
        resolved = resolver.resolve("CapsLock+X", 2, multi_press_enabled=False)
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.matched_command_id, "cmd.single")


if __name__ == "__main__":
    unittest.main()

