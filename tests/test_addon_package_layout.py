import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class AddonPackageLayoutTests(unittest.TestCase):
    """Guard the .nvda-addon zip layout.

    NVDA scans the addon zip root for ``globalPlugins/``, ``doc/``,
    ``installTasks.py`` etc. If the build script accidentally nests them under
    ``addon/`` again, NVDA installs the addon but never loads the plugin —
    which is exactly how the previous silent-failure regression manifested.
    """

    @classmethod
    def setUpClass(cls):
        cls._tmpdir = tempfile.TemporaryDirectory()
        out_dir = Path(cls._tmpdir.name)
        proc = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "build_addon.py"),
                "--repo-root",
                str(REPO_ROOT),
                "--output-dir",
                str(out_dir),
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise AssertionError(
                "build_addon.py failed\nstdout:\n" + proc.stdout + "\nstderr:\n" + proc.stderr
            )
        artifacts = list(out_dir.rglob("*.nvda-addon"))
        if not artifacts:
            raise AssertionError(f"build produced no .nvda-addon under {out_dir}")
        cls._artifact = artifacts[0]

    @classmethod
    def tearDownClass(cls):
        cls._tmpdir.cleanup()

    def _names(self):
        with zipfile.ZipFile(self._artifact) as zf:
            return zf.namelist()

    def test_required_files_at_zip_root(self):
        names = set(self._names())
        required = {
            "manifest.ini",
            "installTasks.py",
            "globalPlugins/spellforge.py",
            "globalPlugins/spellforge_settings.py",
            "spellforge_runtime/__init__.py",
            "spellforge_runtime/diagnostics.py",
            "config/hotkeys/commands/tier1-commands.v1.json",
            "config/hotkeys/global-keymap.v1.json",
            "doc/en/readme.md",
        }
        missing = sorted(required - names)
        self.assertFalse(missing, f"Missing required entries at zip root: {missing}")

    def test_no_addon_prefix_anywhere(self):
        offenders = [n for n in self._names() if n.startswith("addon/") or n == "addon"]
        self.assertFalse(
            offenders,
            "Found entries under addon/ — NVDA will not see globalPlugins. "
            "Examples: " + ", ".join(offenders[:5]),
        )

    def test_manifest_has_addon_name(self):
        with zipfile.ZipFile(self._artifact) as zf:
            with zf.open("manifest.ini") as fh:
                text = fh.read().decode("utf-8")
        self.assertIn("name = spellforgeHotkeys", text)


if __name__ == "__main__":
    unittest.main()
