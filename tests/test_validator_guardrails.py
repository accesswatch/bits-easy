import json
from pathlib import Path
import subprocess
import unittest


class ValidatorGuardrailsTests(unittest.TestCase):
    def test_validator_blocks_unsafe_profile_override(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        expert_profile = repo_root / "config" / "hotkeys" / "profiles" / "expert.json"
        validate_script = repo_root / "scripts" / "validate-hotkey-config.ps1"

        original = expert_profile.read_text(encoding="utf-8")
        try:
            data = json.loads(original)
            for policy in data.get("commandPolicies", []):
                if policy.get("commandId") == "cmd.clip.deleteSlot":
                    policy["confirmation"] = "adaptive"
            expert_profile.write_text(json.dumps(data, indent=2), encoding="utf-8")

            proc = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(validate_script),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("destructive commands must use confirmation 'always' or 'inherit'", proc.stdout)
        finally:
            expert_profile.write_text(original, encoding="utf-8")

        verify = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(validate_script),
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(verify.returncode, 0)


if __name__ == "__main__":
    unittest.main()
