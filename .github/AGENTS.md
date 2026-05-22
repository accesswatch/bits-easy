# AGENTS.md

## Purpose

This repository defines the hotkey and virtualized-browse foundation for Magical 1.0. AI coding agents should treat this repo as a configuration and validation workspace first, not an application runtime.

## Start Here

1. Read [VIRTUALIZED-BROWSE-AND-HOTKEY-SPEC.md](VIRTUALIZED-BROWSE-AND-HOTKEY-SPEC.md) for behavior contracts.
2. Read [ENGINEERING-STARTER-PACK-VIRTUALIZED-HOTKEYS.md](ENGINEERING-STARTER-PACK-VIRTUALIZED-HOTKEYS.md) for implementation artifacts and acceptance framing.
3. Use [SPRINT-BACKLOG-EXECUTION.md](SPRINT-BACKLOG-EXECUTION.md) for ticket dependencies and release priorities.
4. Use [NVDA-UPSTREAM-IMPLEMENTATION-READINESS.md](NVDA-UPSTREAM-IMPLEMENTATION-READINESS.md) for current NV Access GitHub baselines and migration constraints.

## Primary Validation Commands

Run these after any change to files under `config/hotkeys`, `schemas/hotkeys`, or `scripts/validate-hotkey-config.ps1`:

1. VS Code task: `Validate hotkey configs`
2. Script directly:
   `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/validate-hotkey-config.ps1`

Expected success output: `Hotkey config validation passed.`

## Repo Map

1. Command catalog: [config/hotkeys/commands/tier1-commands.v1.json](config/hotkeys/commands/tier1-commands.v1.json)
2. Global keymap: [config/hotkeys/global-keymap.v1.json](config/hotkeys/global-keymap.v1.json)
3. Profile overrides:
   [config/hotkeys/profiles/beginner.json](config/hotkeys/profiles/beginner.json),
   [config/hotkeys/profiles/balanced.json](config/hotkeys/profiles/balanced.json),
   [config/hotkeys/profiles/expert.json](config/hotkeys/profiles/expert.json)
4. Schemas:
   [schemas/hotkeys/command-metadata.schema.json](schemas/hotkeys/command-metadata.schema.json),
   [schemas/hotkeys/global-keymap.schema.json](schemas/hotkeys/global-keymap.schema.json),
   [schemas/hotkeys/profile-overrides.schema.json](schemas/hotkeys/profile-overrides.schema.json)
5. Validator script: [scripts/validate-hotkey-config.ps1](scripts/validate-hotkey-config.ps1)

## Non-Negotiable Conventions

1. Command IDs must match `^cmd\.[a-z0-9]+(\.[a-z0-9]+)+$`.
2. Do not add key bindings that reference unknown `commandId` values.
3. Keep `cmd.system.emergencyStop` globally available and enabled.
4. Do not bypass safety gates for adaptive or mutating commands without explicit spec changes.
5. Preserve profile IDs exactly: `beginner`, `balanced`, `expert`.
6. If changing behavior contracts, update spec docs in the same change.

## Change Workflow for Agents

1. Identify the source of truth first:
   command metadata, keymap, profile override, or schema.
2. Make the smallest possible edit.
3. Validate with the task or script.
4. If validation fails, fix root cause instead of weakening schemas.
5. Summarize user-visible impact in terms of:
   hotkey behavior, fallback behavior, and safety/confirmation behavior.

## Common Pitfalls

1. Updating `global-keymap.v1.json` without adding/updating the command in `tier1-commands.v1.json`.
2. Changing schema constraints without updating existing config files.
3. Introducing duplicate command IDs in command metadata.
4. Assuming this repo includes executable app adapters. It currently contains spec/config/validation assets.

## Related Product Context

For broader product direction and user journey details, use these references instead of duplicating content:

1. [PRD-NVDA-Magical-Experience.md](PRD-NVDA-Magical-Experience.md)
2. [MAGICAL-1.0-END-USER-STORY.md](MAGICAL-1.0-END-USER-STORY.md)
3. [NVDA-UPSTREAM-IMPLEMENTATION-READINESS.md](NVDA-UPSTREAM-IMPLEMENTATION-READINESS.md)
