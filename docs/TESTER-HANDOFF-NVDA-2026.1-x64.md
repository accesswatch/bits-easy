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

## Notes

1. This project baseline is 64-bit only.
2. NVDA versions older than 2026.1 are out of scope for this handoff profile.