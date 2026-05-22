import subprocess
import sys
import unittest
from pathlib import Path


class V1ClosureGateTests(unittest.TestCase):
    def test_verify_v1_closure_script(self):
        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / "scripts" / "verify_v1_closure.py"
        proc = subprocess.run([sys.executable, str(script)], cwd=repo_root, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
