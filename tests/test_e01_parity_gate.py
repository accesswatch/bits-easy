import subprocess
import sys
import unittest
from pathlib import Path


class E01ParityGateTests(unittest.TestCase):
    def test_verify_e01_parity_script(self):
        repo_root = Path(__file__).resolve().parents[1]
        script = repo_root / "scripts" / "verify_e01_parity.py"
        proc = subprocess.run([sys.executable, str(script)], cwd=repo_root, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, msg=proc.stdout + proc.stderr)


if __name__ == "__main__":
    unittest.main()
