# NVDA Upstream Implementation Readiness

## Date

May 21, 2026

## Purpose

This document translates current NV Access GitHub and documentation sources into implementation-ready constraints for Magical 1.0 hotkeys and virtualized browse behavior.

## Upstream Snapshot

1. Latest upstream change log on `master` is `2026.3`.
2. `2026.1` is an add-on API breaking release.
3. `2026.1.1` is a security patch release in that series.
4. Platform support shifted to 64-bit Windows only.

Primary sources:
1. https://github.com/nvaccess/nvda
2. https://raw.githubusercontent.com/nvaccess/nvda/master/user_docs/en/changes.md
3. https://download.nvaccess.org/releases/2026.1.1/documentation/en/userGuide.html
4. https://download.nvaccess.org/releases/2026.1.1/documentation/en/keyCommands.html

## Non-Negotiable Platform Constraints

1. Minimum runtime target for NVDA-aligned behavior is Windows 10 64-bit.
2. Recommended runtime target is Windows 11 and Windows 10 22H2.
3. 32-bit Windows is out of scope.
4. Windows 10 on ARM is out of scope.
5. Add-on compatibility must be treated as broken at 2026.1 boundaries unless manifests are updated and add-ons are re-tested.

Sources:
1. https://raw.githubusercontent.com/nvaccess/nvda/master/user_docs/en/changes.md
2. https://download.nvaccess.org/releases/2026.1.1/documentation/en/userGuide.html

## Build Environment Baseline (NVDA-Aligned)

For any future repo that builds NVDA code or NVDA add-ons directly, use this baseline:

1. Python: `cpython-3.13.12-windows-x86_64-none`
2. Package and project manager: `uv`
3. Visual Studio: 2022 or 2026 with C++ desktop workload and ARM64/ARM64EC build tools
4. Build entry point: `scons source`
5. Run from source entry point: `runnvda.bat`

Sources:
1. https://raw.githubusercontent.com/nvaccess/nvda/master/.python-versions
2. https://raw.githubusercontent.com/nvaccess/nvda/master/.vsconfig
3. https://raw.githubusercontent.com/nvaccess/nvda/master/projectDocs/dev/createDevEnvironment.md
4. https://raw.githubusercontent.com/nvaccess/nvda/master/projectDocs/dev/buildingNVDA.md

## Mandatory Test and Quality Gates

Upstream-required checks for NVDA-facing code or add-ons:

1. `rununittests.bat`
2. `runlint.bat`
3. `runcheckpot.bat`
4. `runlicensecheck.bat`
5. `runsystemtests.bat --include NVDA` when relevant to behavior changes

Source:
1. https://raw.githubusercontent.com/nvaccess/nvda/master/projectDocs/testing/automated.md
2. https://raw.githubusercontent.com/nvaccess/nvda/master/projectDocs/dev/contributing.md

## Security Process Requirements

1. Never file vulnerabilities as public GitHub issues.
2. Use GitHub Security Advisories or email `info@nvaccess.org`.
3. Include reproducibility details, impact, and workaround information.
4. Track severity using upstream P1, P2, P3 model.

Source:
1. https://raw.githubusercontent.com/nvaccess/nvda/master/security.md

## Impact on This Repository

This repository is currently a spec/config/validation workspace, not an NVDA runtime codebase. Implementation readiness therefore means:

1. Keep hotkey and virtualized browse contracts compatible with NVDA command and browse mental models.
2. Keep safety and fallback behavior explicit for all direct hotkeys.
3. Keep deterministic restore-to-source behavior aligned with NVDA browse and focus transitions.
4. Reserve future adapter and add-on work for 64-bit Windows targets only.

## Recommended Immediate Actions

1. Treat `2026.1` and later as compatibility baseline for all design assumptions.
2. Add explicit backlog tasks for add-on manifest compatibility and API break adaptation before adapter implementation starts.
3. Add a release checklist item that verifies no requirement assumes 32-bit Windows or Windows 8.1 support.
4. Require evidence links to upstream source files in all future architecture or behavior changes.

## GitHub Reference Index

Core repository and docs:
1. https://github.com/nvaccess/nvda
2. https://raw.githubusercontent.com/nvaccess/nvda/master/projectDocs/dev/createDevEnvironment.md
3. https://raw.githubusercontent.com/nvaccess/nvda/master/projectDocs/dev/buildingNVDA.md
4. https://raw.githubusercontent.com/nvaccess/nvda/master/projectDocs/dev/contributing.md
5. https://raw.githubusercontent.com/nvaccess/nvda/master/projectDocs/dev/addons.md
6. https://raw.githubusercontent.com/nvaccess/nvda/master/projectDocs/testing/automated.md
7. https://raw.githubusercontent.com/nvaccess/nvda/master/security.md
8. https://raw.githubusercontent.com/nvaccess/nvda/master/user_docs/en/changes.md

Release documentation:
1. https://download.nvaccess.org/releases/2026.1.1/documentation/en/userGuide.html
2. https://download.nvaccess.org/releases/2026.1.1/documentation/en/keyCommands.html
3. https://download.nvaccess.org/releases/2026.1.1/documentation/en/changes.html

