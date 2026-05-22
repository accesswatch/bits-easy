from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import tempfile
import zipfile


def _copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def _render_manifest(repo_root: Path, stage_root: Path) -> dict:
    vars_mod = runpy.run_path(str(repo_root / "buildVars.py"))
    info = vars_mod["addon_info"]
    tpl = (repo_root / "manifest.ini.tpl").read_text(encoding="utf-8")
    manifest = tpl.format(**info)
    (stage_root / "manifest.ini").write_text(manifest, encoding="utf-8")
    return info


def _zip_addon(stage_root: Path, out_file: Path) -> None:
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_file, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in stage_root.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(stage_root))


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 64)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _sign_if_possible(artifact: Path, key_pem_path: Path | None) -> Path | None:
    if key_pem_path is None or not key_pem_path.exists():
        return None

    sig_path = artifact.with_suffix(artifact.suffix + ".sig")
    subprocess.run(
        [
            "openssl",
            "dgst",
            "-sha256",
            "-sign",
            str(key_pem_path),
            "-out",
            str(sig_path),
            str(artifact),
        ],
        check=True,
    )
    return sig_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build distributable NVDA addon artifact.")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--output-dir", default="dist")
    parser.add_argument("--signing-key-pem", default="")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    output_dir = (repo_root / args.output_dir).resolve()

    with tempfile.TemporaryDirectory() as tmpdir:
        stage_root = Path(tmpdir) / "addon-stage"
        stage_root.mkdir(parents=True, exist_ok=True)

        _copy_tree(repo_root / "addon", stage_root / "addon")
        _copy_tree(repo_root / "config" / "hotkeys", stage_root / "config" / "hotkeys")
        _copy_tree(repo_root / "src" / "spellforge_runtime", stage_root / "spellforge_runtime")

        info = _render_manifest(repo_root, stage_root)
        artifact = output_dir / f"{info['addon_name']}-{info['addon_version']}.nvda-addon"
        _zip_addon(stage_root, artifact)

        digest = _sha256(artifact)
        sha_path = artifact.with_suffix(artifact.suffix + ".sha256")
        sha_path.write_text(f"{digest}  {artifact.name}\n", encoding="utf-8")

        sig = _sign_if_possible(artifact, Path(args.signing_key_pem) if args.signing_key_pem else None)

        print(f"Built {artifact}")
        print(f"SHA256 {sha_path}")
        if sig:
            print(f"Signature {sig}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
