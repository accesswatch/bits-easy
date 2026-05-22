# Spellforge NVDA Add-on

## Purpose

Spellforge adds selection-first hotkeys, clip slot workflows, and merge utilities to NVDA.

## Included Features

1. Selection start and end marker commands.
2. Selection context readback.
3. Clip slot copy and paste workflow with persistent storage.
4. Runtime command dispatcher driven by repository hotkey JSON.

## Default Add-on Gestures

1. NVDA+[ sets selection start.
2. NVDA+] sets selection end.
3. NVDA+' reads selection context.
4. NVDA+1 copies into slot 1.
5. NVDA+2 pastes from slot 1.

## Development Notes

1. Runtime source lives in src/spellforge_runtime.
2. Global plugin entrypoint is addon/globalPlugins/spellforge.py.
3. Hotkey profiles and policies live under config/hotkeys.
