# Engineering Starter Pack: Virtualized Browse and Hotkeys

## Date

May 21, 2026

## Purpose

This starter pack provides implementation-ready artifacts for direct hotkey workflows and virtualized browse return mode.

## Includes

1. Tier 1 command ID catalog for v1 hotkeys.
2. JSON schemas for keymap, profile overrides, and command metadata.
3. CI test matrix checklist with release gates.
4. Suggested rollout sequence by sprint.

## Bootstrap Config Files

1. config/hotkeys/global-keymap.v1.json
2. config/hotkeys/commands/tier1-commands.v1.json
3. config/hotkeys/profiles/beginner.json
4. config/hotkeys/profiles/balanced.json
5. config/hotkeys/profiles/expert.json

## Bootstrap Schema Files

1. schemas/hotkeys/command-metadata.schema.json
2. schemas/hotkeys/global-keymap.schema.json
3. schemas/hotkeys/profile-overrides.schema.json

## Validation Automation

1. Local script: scripts/validate-hotkey-config.ps1
2. VS Code task: .vscode/tasks.json with label Validate hotkey configs
3. CI workflow: .github/workflows/validate-hotkeys.yml
4. Release hardening checklist: docs/RELEASE-HARDENING-CHECKLIST.md
5. Cross-app parity smoke suite: tests/test_release_parity_matrix.py

### How To Run Locally

1. Use the VS Code task named Validate hotkey configs.
2. Or run pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/validate-hotkey-config.ps1.

## Tier 1 Command ID Catalog

The following table defines v1 direct-hotkey commands.

| Command ID | Command Name | Safety Class | Default Hotkey | Requires Confirmation |
| --- | --- | --- | --- | --- |
| cmd.palette.open | Open palette | Safe | NVDA+Shift+P | No |
| cmd.capture.quickInbox | Quick capture to inbox | Safe | Grave+Q | No |
| cmd.selection.summarize | Summarize selection | Adaptive | Grave+S | Low confidence only |
| cmd.selection.extractActions | Extract action items | Adaptive | Grave+A | Low confidence only |
| cmd.selection.rewriteBeginner | Rewrite for beginners | Adaptive mutating | Grave+R | Yes before apply |
| cmd.result.virtualOpen | Open latest virtualized result | Safe | Grave+V | No |
| cmd.result.block.copy | Copy current virtual block | Safe | Grave+C | No |
| cmd.result.block.next | Next virtual block | Safe | Grave+RightArrow | No |
| cmd.result.block.previous | Previous virtual block | Safe | Grave+LeftArrow | No |
| cmd.context.returnSource | Return to source anchor | Safe | Grave+Backspace | No |
| cmd.help.availableHotkeys | What can I press | Safe | Grave+Slash | No |
| cmd.system.emergencyStop | Emergency stop | Safe critical | Grave+Escape | No |
| cmd.result.copyAll | Copy full result | Safe | Grave+Shift+C | No |
| cmd.result.pinInbox | Pin result to inbox | Safe | Grave+P | No |
| cmd.result.readConfidence | Read confidence summary | Safe | Grave+K | No |
| cmd.result.openFallbacks | Open fallback menu | Safe | Grave+F | No |
| cmd.result.toggleSpeechDensity | Toggle speech density | Safe | Grave+B | No |
| cmd.result.toggleBrailleDensity | Toggle braille density | Safe | Grave+N | No |
| cmd.result.search | Search in virtualized result | Safe | Grave+Control+F | No |
| cmd.profile.hotkeyDiagnostics | Open hotkey diagnostics | Safe | Grave+D | No |
| cmd.selection.markStart | Mark selection start | Safe | Grave+OpenBracket | No |
| cmd.selection.markEnd | Mark selection end | Safe | Grave+CloseBracket | No |
| cmd.selection.readContext | Read selection context | Safe | Grave+Quote | No |
| cmd.selection.jumpStart | Jump to selection start | Safe | Grave+J | No |
| cmd.selection.cancel | Cancel selection markers | Safe | Grave+X | No |
| cmd.clip.selectSlot | Select active clip slot | Safe | Grave+F1..F12 | No |
| cmd.clip.copyToSlot | Copy to active clip slot | Safe | Grave+Shift+F1..F12 | No |
| cmd.clip.pasteFromSlot | Paste from active clip slot | Mutating | Grave+Control+F1..F12 | Yes before apply |
| cmd.clip.protectSlot | Protect active clip slot | Mutating | Grave+Shift+P | No |
| cmd.clip.unprotectSlot | Unprotect active clip slot | Mutating | Grave+Shift+U | No |
| cmd.clip.deleteSlot | Delete active clip slot | Destructive | Grave+3 | Yes |
| cmd.clip.editSlot | Edit active clip slot | Mutating | Grave+Shift+E | Yes before apply |
| cmd.clip.describeSlot | Describe active clip slot | Safe | Grave+Windows+F1..F12 | No |
| cmd.merge.setModeAppend | Set merge mode append | Safe | Grave+M | No |
| cmd.merge.setModeReplace | Set merge mode replace | Safe | Grave+Shift+M | No |
| cmd.merge.setDividerLine | Set merge divider line | Safe | Grave+L | No |
| cmd.merge.setDividerSpace | Set merge divider space | Safe | Grave+U | No |
| cmd.merge.setDividerParagraph | Set merge divider paragraph | Safe | Grave+I | No |

## JSON Schema: Command Metadata

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://bits-easy.local/schemas/command-metadata.schema.json",
  "title": "CommandMetadata",
  "type": "object",
  "required": [
    "id",
    "name",
    "safetyClass",
    "executionMode",
    "supportsHotkey",
    "supportsPalette",
    "supportsVirtualized"
  ],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^cmd\\.[a-z0-9]+(\\.[a-z0-9]+)+$"
    },
    "name": {
      "type": "string",
      "minLength": 3
    },
    "safetyClass": {
      "type": "string",
      "enum": ["safe", "adaptive", "mutating", "destructive"]
    },
    "executionMode": {
      "type": "string",
      "enum": ["immediate", "preview-first", "confirm-first"]
    },
    "supportsHotkey": {
      "type": "boolean"
    },
    "supportsPalette": {
      "type": "boolean"
    },
    "supportsVirtualized": {
      "type": "boolean"
    },
    "defaultHotkey": {
      "type": ["string", "null"]
    },
    "requiresConfirmation": {
      "type": "boolean",
      "default": false
    },
    "fallbackCommandIds": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^cmd\\.[a-z0-9]+(\\.[a-z0-9]+)+$"
      },
      "default": []
    }
  },
  "additionalProperties": false
}
```

## JSON Schema: Global Keymap

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://bits-easy.local/schemas/global-keymap.schema.json",
  "title": "GlobalKeymap",
  "type": "object",
  "required": ["version", "bindings"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^v[0-9]+$"
    },
    "bindings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["commandId", "keyChord", "scope", "enabled"],
        "properties": {
          "commandId": {
            "type": "string",
            "pattern": "^cmd\\.[a-z0-9]+(\\.[a-z0-9]+)+$"
          },
          "keyChord": {
            "type": "string",
            "minLength": 3
          },
          "scope": {
            "type": "string",
            "enum": ["global", "virtualized", "app-override"]
          },
          "appId": {
            "type": ["string", "null"]
          },
          "enabled": {
            "type": "boolean"
          },
          "safetyGate": {
            "type": "string",
            "enum": ["none", "low-confidence-confirm", "always-confirm"],
            "default": "none"
          }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
```

## JSON Schema: Profile Overrides

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://bits-easy.local/schemas/profile-overrides.schema.json",
  "title": "ProfileOverrides",
  "type": "object",
  "required": ["profileId", "speechMode", "brailleMode", "confirmPolicy", "hotkeyHints"],
  "properties": {
    "profileId": {
      "type": "string",
      "enum": ["beginner", "balanced", "expert"]
    },
    "speechMode": {
      "type": "string",
      "enum": ["detailed", "concise", "minimal"]
    },
    "brailleMode": {
      "type": "string",
      "enum": ["expanded", "compact"]
    },
    "confirmPolicy": {
      "type": "string",
      "enum": ["strict", "adaptive", "minimal"]
    },
    "hotkeyHints": {
      "type": "boolean"
    },
    "appOverrides": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["appId", "remapBindings"],
        "properties": {
          "appId": {
            "type": "string"
          },
          "remapBindings": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["commandId", "keyChord"],
              "properties": {
                "commandId": {
                  "type": "string",
                  "pattern": "^cmd\\.[a-z0-9]+(\\.[a-z0-9]+)+$"
                },
                "keyChord": {
                  "type": "string"
                }
              },
              "additionalProperties": false
            }
          }
        },
        "additionalProperties": false
      },
      "default": []
    }
  },
  "additionalProperties": false
}
```

## Example Keymap

```json
{
  "version": "v1",
  "bindings": [
    {
      "commandId": "cmd.palette.open",
      "keyChord": "NVDA+Shift+P",
      "scope": "global",
      "appId": null,
      "enabled": true,
      "safetyGate": "none"
    },
    {
      "commandId": "cmd.selection.summarize",
      "keyChord": "Grave+S",
      "scope": "global",
      "appId": null,
      "enabled": true,
      "safetyGate": "low-confidence-confirm"
    },
    {
      "commandId": "cmd.result.block.next",
      "keyChord": "Grave+RightArrow",
      "scope": "virtualized",
      "appId": null,
      "enabled": true,
      "safetyGate": "none"
    }
  ]
}
```

## CI Test Matrix Checklist

### Matrix Dimensions

1. OS: Windows 11 current and previous stable.
2. Screen reader mode: speech only, braille only, speech plus braille.
3. Profile: beginner, balanced, expert.
4. App target: Edge, Chrome, Firefox, Outlook, Word, Notepad, VS Code.
5. Path: direct hotkey and palette equivalent.

### Gate A: Command Parity

1. Each Tier 1 command has both palette and direct-hotkey execution path.
2. Result semantics match across both paths.
3. Failures produce deterministic fallback suggestions.

### Gate B: Collision Safety

1. Key collisions are detected before enable and at runtime.
2. Diagnostics include app id, key chord, conflicting commands.
3. User can remap to a valid chord without restart.

### Gate C: Virtualized Navigation

1. H, A, C, L, T, N, Home, End, and in-result search operate deterministically.
2. Block copy and full copy produce expected content.
3. Confidence, fallback, and status outputs are available at any point.

### Gate D: Focus Return

1. Exit virtualized mode returns to exact source in at least 95 percent of runs.
2. Drift path reports clear explanation and guided recovery.
3. Return operation never leaves user in unknown focus state.

### Gate E: Accessibility Parity

1. Speech and braille convey equivalent critical information.
2. No speech-only confirmation or fallback details.
3. Keyboard-only operation succeeds for all test cases.

### Gate F: Safety Controls

1. Mutating actions via hotkey always enforce preview and confirmation policy.
2. Low-confidence adaptive actions require confirmation.
3. Emergency stop interrupts active automation safely.

## Suggested Sprint Sequence

1. Sprint 1: Command IDs, metadata schema, Tier 1 global bindings, collision scanner baseline.
2. Sprint 2: Virtualized renderer core, structural navigation, block actions.
3. Sprint 3: Source anchor restore and drift recovery, parity tests, profile overrides.
4. Sprint 4: Diagnostics surface, telemetry events, CI gate hardening.

## Done Criteria for v1

1. Tier 1 commands shipped with stable IDs and default bindings.
2. JSON schemas validated in CI for configuration files.
3. CI matrix gates A through F are green for baseline apps.
4. Documentation references updated in PRD and sprint backlog.


