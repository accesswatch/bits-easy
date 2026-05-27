# Release Hardening Checklist

## Purpose

This checklist standardizes release readiness for major feature waves so rollout quality remains consistent.

Release quality in BITS-EASY means more than tests passing. It means users get speed with trust: commands behave predictably, recovery paths are intact, and beta controls do not leak into stable experience.

## 1. Build and Validation Gate

1. Run hotkey schema and config validation.
2. Run full unit test suite.
3. Verify deterministic command catalog load and dispatcher startup.
4. Ensure git hooks are installed (`pwsh -File scripts/install-git-hooks.ps1`).
5. Confirm pre-commit rebuilds the addon package (`.githooks/pre-commit` runs `python scripts/build_addon.py --output-dir dist`).

### Current branch status (2026-05-22)

1. Hotkey validation: PASS (`scripts/validate-hotkey-config.ps1`).
2. Unit tests: PASS (`python -m unittest discover -s tests -p "test_*.py"`).
3. Cross-app parity smoke suite: PASS (`tests/test_release_parity_matrix.py`).
4. Pre-commit addon rebuild hook: REQUIRED for release branch commits.

## 2. Migration and Data Safety

1. Verify new persisted files/keys load safely from prior versions.
2. Verify missing or malformed persisted data falls back without crashes.
3. Verify rollback paths for destructive commands remain intact.

## 3. QA Evidence Pack

1. Include manual parity matrix output from `FULL-GUIDED-KEYSTROKE-TEST-PLAN.md`.
2. Include pass/fail summary by app surface.
3. Include unresolved risk notes and explicit defer list.

Evidence should demonstrate both correctness and experience quality, not only raw pass counts.

## 3A. Tester Handoff Baseline (Consolidated)

This checklist now contains the former tester handoff essentials.

1. Hard requirements:
1. Windows 10 or 11, 64-bit.
2. NVDA 2026.1, 64-bit.
3. Latest BITS-EASY `.nvda-addon` package.
2. Optional dependency scope:
1. Install Google APIs only if testing Google Calendar or Google Contacts flows.
3. Manual device pass surfaces:
1. Edge
2. Chrome
3. Firefox
4. Outlook
5. Word
6. Notepad
7. VS Code

## 4. Release Notes Content

Each release note should include:

1. New command families and behavior changes.
2. Backward compatibility notes and migration behavior.
3. Known limitations and planned follow-up.

### Release Notes Draft (non-media, non-podcasting, non-RSS, non-braille scope)

1. Added retrieval wayfinding commands (anchor set, trail open/return, visited report).
2. Added advanced notes commands (category tree, related graph, attachment actions, backup export/restore).
3. Added guided Jamal sync commands (plan, apply plan, rollback).
4. Added context hardening commands (capability envelope and drift-safe return-source).
5. Added file operations command family (browse, copy/move/rename/delete, zip create, full path copy, tag batch).
6. Added journal trend reporting and clip library timeline/discoverability payload.
7. Improved clip compare payload quality with similarity and line-diff preview.
8. Added secure secret-store abstraction for AI provider keys with Windows Credential Manager backend and safe fallback.
9. Added AI key diagnostics commands (`cmd.ai.key.status`, `cmd.ai.key.storeStatus`) including plain-language spoken backend summary in NVDA.
10. Added additive AI augmentation to existing text workflows (selection summarize/extract/rewrite, quick capture, notes quick capture/help, spellcheck) while preserving deterministic primary outputs.

### Migration Notes Draft

1. New persisted runtime files:
   - `ai-assistant.json`
   - `secret_store` runtime backend state is provider-key storage abstraction; provider keys are no longer persisted in plaintext JSON.
   - `retrieval-memory.json` additions (anchors/trail)
   - `notes-workspace.json` additions (backup/category graph metadata)
   - `structured-records.json` additions (sync plans)
2. Existing persisted files remain backward-compatible and load with safe defaults when keys are missing.
3. No schema-breaking rename was introduced for existing command IDs used by earlier v1/v2 flows.

## 5. Pull Request and Branch Hygiene

1. Keep unrelated generated artifacts out of release diff.
2. Ensure docs and command catalog are synchronized.
3. Ensure tests cover every new command path added in dispatcher.

### Branch Hygiene Gate (required before merge)

1. Keep build artifacts out of commit by default; include only intentional release artifacts.
2. Exclude generated local payload files (for example `dist/*.json`) unless explicitly required for release evidence.
3. Use `git --no-pager status --short` and ensure only intended docs/config/src/tests are staged.


