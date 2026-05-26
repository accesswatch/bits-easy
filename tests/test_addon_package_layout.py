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

    def _manifest_dict(self):
        with zipfile.ZipFile(self._artifact) as zf:
            manifest_text = zf.read("manifest.ini").decode("utf-8")

        out = {}
        for raw_line in manifest_text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            out[key.strip()] = value.strip().strip('"')
        return out

    @staticmethod
    def _parse_version(version: str):
        parts = [p.strip() for p in version.split(".") if p.strip()]
        if len(parts) == 2:
            parts.append("0")
        return tuple(int(p) for p in parts)

    def test_required_files_at_zip_root(self):
        names = set(self._names())
        required = {
            "manifest.ini",
            "installTasks.py",
            "globalPlugins/bits_easy.py",
            # bits_easy_settings.py must live at zip root, NOT under globalPlugins/.
            # NVDA scans globalPlugins/*.py for a GlobalPlugin class and fails on helpers.
            "bits_easy_settings.py",
            "bits_easy_runtime/__init__.py",
            "bits_easy_runtime/diagnostics.py",
            "config/hotkeys/commands/tier1-commands.v1.json",
            "config/hotkeys/global-keymap.v1.json",
            "doc/en/readme.md",
        }
        missing = sorted(required - names)
        self.assertFalse(missing, f"Missing required entries at zip root: {missing}")

    def test_settings_helper_not_in_globalplugins(self):
        names = set(self._names())
        self.assertNotIn(
            "globalPlugins/bits_easy_settings.py",
            names,
            "bits_easy_settings.py must not live under globalPlugins/ — NVDA will fail to import it as a plugin.",
        )

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
        self.assertIn("name = bits-easy", text)

    def test_manifest_doc_filename_exists_in_package(self):
        names = set(self._names())
        manifest = self._manifest_dict()
        doc_name = manifest.get("docFileName", "")

        self.assertTrue(doc_name, "manifest.ini must declare docFileName")
        self.assertIn(
            f"doc/en/{doc_name}",
            names,
            f"manifest docFileName points to missing packaged file: {doc_name}",
        )

    def test_manifest_has_release_metadata_fields(self):
        manifest = self._manifest_dict()
        required = {
            "name",
            "summary",
            "version",
            "author",
            "url",
            "minimumNVDAVersion",
            "lastTestedNVDAVersion",
            "docFileName",
            "updateChannel",
            "changelog",
        }
        missing = sorted(k for k in required if not manifest.get(k))
        self.assertFalse(missing, f"Manifest is missing required release metadata fields: {missing}")

    def test_manifest_version_ordering_is_valid(self):
        manifest = self._manifest_dict()
        min_v = self._parse_version(manifest["minimumNVDAVersion"])
        tested_v = self._parse_version(manifest["lastTestedNVDAVersion"])
        self.assertLessEqual(
            min_v,
            tested_v,
            "minimumNVDAVersion must be less than or equal to lastTestedNVDAVersion",
        )


if __name__ == "__main__":
    unittest.main()

