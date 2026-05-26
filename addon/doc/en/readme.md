# BITS-EASY NVDA Add-on

## Purpose

BITS-EASY (Efficient Accessibility Shortcuts for You) adds selection-first hotkeys, clip slot workflows, and merge utilities to NVDA.

## Compatibility Baseline

1. Windows 10 or 11, 64-bit.
2. NVDA 2026.1, 64-bit.

This add-on handoff profile is validated only on NVDA 2026.1 x64.

## Included Features

1. Selection start and end marker commands.
2. Selection context readback.
3. Clip slot copy and paste workflow with persistent storage.
4. Runtime command dispatcher driven by repository hotkey JSON.

## Default Add-on Gestures

1. Control+Alt+[ sets selection start.
2. Control+Alt+] sets selection end.
3. Control+Alt+' reads selection context.
4. Control+Alt+1 copies into slot 1.
5. Control+Alt+2 pastes from slot 1.
6. Control+Alt+Space opens the command palette (double-press for hotkey list, hold for quick actions).
7. NVDA+Shift+P also opens the command palette (secondary entry point).

## Development Notes

1. Runtime source lives in src/bits_easy_runtime.
2. Global plugin entrypoint is addon/globalPlugins/bits_easy.py.
3. Hotkey profiles and policies live under config/hotkeys.

## Optional Integration Dependencies

No additional libraries are required for core hotkeys and clip workflows.

For Google Calendar or Google Contacts features, install:

1. google-api-python-client
2. google-auth
3. google-auth-oauthlib
4. google-auth-httplib2


