# Spellforge Tester Handoff (NVDA 2026.1, 64-bit)

## Scope

This checklist is for test handoff of the Spellforge add-on to QA or pilot users.

## Hard Requirements

1. Windows 10 or Windows 11, 64-bit.
2. NVDA 2026.1, 64-bit.
3. Spellforge add-on package file (`.nvda-addon`).

These are required for compatibility baseline and release sign-off.

## Core Testing Install Steps

1. Install NVDA 2026.1, 64-bit.
2. Open NVDA, then Tools > Manage add-ons.
3. Install the provided Spellforge `.nvda-addon` package.
4. Restart NVDA.
5. Press Control+Alt+Slash to confirm hotkeys are active.

No extra Python packages are required for core add-on behavior.

## Optional Dependencies (Feature-Specific)

Install these only when testing Google Calendar or Google Contacts commands:

1. `google-api-python-client`
2. `google-auth`
3. `google-auth-oauthlib`
4. `google-auth-httplib2`

Install command:

```powershell
pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
```

## Optional Tooling (Dev/Tester Hybrid)

Use only if a tester also builds or validates from source.

1. Python 3.13 x64.
2. PowerShell 7+.
3. OpenSSL (only if signing build artifacts).
4. SCons (only if using the SCons build path).

## Recommended Validation Commands

Run from repository root:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/validate-hotkey-config.ps1
python -m unittest
```

## Sign-Off Matrix

Minimum acceptance matrix for release candidates:

1. NVDA 2026.1 x64 on Windows 10 x64.
2. NVDA 2026.1 x64 on Windows 11 x64.

## Release Candidate Evidence Snapshot (2026-05-22)

1. Hotkey config validation: PASS.
2. Full automated unit suite: PASS.
3. Cross-app parity smoke suite: PASS (Edge, Chrome, Firefox, Outlook, Word, Notepad, VS Code) via `tests/test_release_parity_matrix.py`.

### Scenario-level parity status (automated harness)

| Domain | Status | Evidence |
| --- | --- | --- |
| Selection markers/context/fallback envelope | PASS | `test_release_parity_matrix.py` |
| PocketClips browse/search/compare | PASS | `test_release_parity_matrix.py`, `test_pocketclips_studio.py` |
| Clip library ingest/timeline/restore paths | PASS | `test_release_parity_matrix.py`, `test_clip_library.py` |
| Structured records + Jamal plan path | PASS | `test_release_parity_matrix.py`, `test_structured_records.py` |
| Notes + Retrieval + Journal trend surfaces | PASS | `test_release_parity_matrix.py`, `test_v4_feature_completion.py` |

## Manual Device Pass Sign-Off (Operator Checklist)

Use this exact checklist during final device pass and attach outcomes to release PR.

| Surface | Operator | Date | Result | Notes |
| --- | --- | --- | --- | --- |
| Edge |  |  |  |  |
| Chrome |  |  |  |  |
| Firefox |  |  |  |  |
| Outlook |  |  |  |  |
| Word |  |  |  |  |
| Notepad |  |  |  |  |
| VS Code |  |  |  |  |

## Manual Parity Scenarios (Required)

Run these in Edge, Chrome, Firefox, Outlook, Word, Notepad, and VS Code where applicable.

1. Selection markers: start, end, context, jump, cancel, marker status output.
2. Unsupported-surface behavior: verify guided fallback steps and no silent failures.
3. PocketClips browser: open, search, filter, sort, pin/unpin, reorder, split, merge, compare.
4. Clip library: ingest, folder create/rename/delete, move/link clip, alias conflict strategy, restore to slot, retention policy.
5. Database tools: template apply, entry grid paging, advanced search filters, dashboard summary, CSV/TXT/JSON export, Jamal import/export/sync dry-run.

## Manual Sign-Off Evidence

Capture and attach to release:

1. App + scenario + PASS/FAIL for every required scenario.
2. Any fallback message text that was unclear or missing action guidance.
3. Repro steps for each fail, including command id, profile, and app surface.

## Notes

1. This project baseline is 64-bit only.
2. NVDA versions older than 2026.1 are out of scope for this handoff profile.