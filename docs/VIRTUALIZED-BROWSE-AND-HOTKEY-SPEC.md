# Virtualized Browse and Direct Hotkey Spec

## Date

May 21, 2026

## Purpose

This specification defines how Magical 1.0 returns complex content in a virtualized browse surface and how users run high-frequency actions through direct hotkeys without opening the command palette.

## Scope

1. Virtualized return surface behavior.
2. Deterministic focus return and context anchoring.
3. Direct hotkey command plane.
4. Keymap strategy by profile.
5. Collision handling and fallback behavior.
6. Accessibility parity and release acceptance tests.

## Design Principles

1. Palette first discovery, hotkey first speed.
2. Deterministic key behavior across apps.
3. No silent failure. Always offer next action.
4. Speech and braille parity for every critical state.
5. Fast exit back to exact user context.

## Terms

1. Source surface: the app and control where the action started.
2. Virtualized browse surface: a temporary, keyboard-first reading surface for returned content.
3. Source anchor: metadata required to return focus and selection to source.
4. Flight path: a direct hotkey path that executes a command without opening the palette.

## Virtualized Browse Surface

### Entry Rules

The following list defines when virtualized browse mode should open.

1. Output length exceeds user threshold.
2. Output contains more than one structural section.
3. Source surface cannot reliably host rich returned content.
4. User explicitly requests virtualized view.

### Exit Rules

The following list defines how virtualized browse mode exits.

1. Escape closes virtualized browse and returns to source anchor.
2. Enter on apply action writes output to destination when applicable.
3. Control+Enter opens action menu for apply, copy, export, compare.
4. On failure to restore anchor, system opens guided return menu.

### Information Model

The following table defines the required data model for each virtualized result.

| Field | Required | Description |
| --- | --- | --- |
| resultId | Yes | Unique result identifier |
| sourceAnchor | Yes | App id, window id, control id, selection snapshot |
| blocks | Yes | Structured blocks such as heading, paragraph, list, table, action item |
| citations | Optional | Source links or origin metadata |
| confidence | Yes | Confidence score and policy level |
| fallbacks | Yes | Available fallback actions |
| createdAt | Yes | Timestamp for diagnostics and replay |

### Structural Navigation Contract

The following list defines required navigation behavior.

1. H and Shift+H move next and previous heading.
2. A and Shift+A move next and previous action item.
3. C and Shift+C move next and previous citation block.
4. L and Shift+L move next and previous list block.
5. T and Shift+T move next and previous table block.
6. N and Shift+N move next and previous paragraph block.
7. Home and End move first and last block.
8. Control+F opens in-result search.

### Action Contract in Virtualized Mode

The following list defines required action keys.

1. Y copies current block.
2. Control+Y copies full result.
3. P pins result to quick capture inbox.
4. R reads confidence and rationale summary.
5. F opens fallback actions for current block.
6. B toggles brief and detailed speech mode.
7. V toggles braille compact and expanded output.

### Focus Return Contract

The following list defines required focus behavior.

1. Save source anchor before rendering virtualized surface.
2. Restore window focus, control focus, and selection state on exit.
3. If exact selection restore fails, restore nearest valid anchor and announce drift.
4. Always provide retry return and manual return options.

## Direct Hotkey Command Plane

### Multi-Press Gesture Model

The following model defines how single, double, and triple key press patterns are resolved.

1. Single press runs the default command immediately unless a multi-press binding for the same key chord is active with suppression enabled.
2. Double press executes a second command bound to the same key chord within the multi-press window.
3. Triple press executes a third command bound to the same key chord within the multi-press window.
4. Press-and-hold can execute a dedicated command when hold threshold is reached.

Timing defaults:

1. `multiPressWindowMs`: 350 milliseconds.
2. `holdThresholdMs`: 500 milliseconds.
3. Configurable range must be validated by schema.

Deterministic resolution order:

1. Emergency stop binding always wins if configured on the active chord.
2. Explicit triple-press match.
3. Explicit double-press match.
4. Single-press command.

Fallback and feedback requirements:

1. On ambiguous pattern timing, execute the safest matching command and announce resolution.
2. If a multi-press command is blocked in current context, offer immediate fallback options.
3. Speech and braille must announce whether single, double, or triple action was triggered.

### Command Tiers

The following list defines which commands qualify for direct hotkeys.

1. Tier 1 commands: top 35 frequency and low ambiguity actions.
2. Tier 2 commands: profile-enabled advanced actions.
3. Tier 3 commands: palette only because of high ambiguity or safety risk.

### Global Reserved Hotkeys

The following table defines baseline reserved hotkeys.

| Command | Default Hotkey | Behavior |
| --- | --- | --- |
| Open palette | NVDA+Shift+P | Opens StarKey palette |
| Quick capture to inbox | CapsLock+Q | Captures current selection or guided fallback |
| Summarize selection | CapsLock+S | Runs summarize action with confidence output |
| Extract action items | CapsLock+A | Extracts tasks from current context |
| Rewrite for beginners | CapsLock+R | Opens preview first for rewrite action |
| Open virtualized result | CapsLock+V | Opens most recent result in virtualized mode |
| Copy current virtual block | CapsLock+C | Copies focused block in virtualized mode |
| Next virtual block | CapsLock+RightArrow | Moves to next structural block |
| Previous virtual block | CapsLock+LeftArrow | Moves to previous structural block |
| Return to source | CapsLock+Backspace | Restores source anchor |
| What can I press | CapsLock+Slash | Announces available hotkeys by context |
| Emergency stop | CapsLock+Escape | Cancels current automation and returns control |
| Mark selection start | CapsLock+OpenBracket | Sets selection start marker for range workflows |
| Mark selection end | CapsLock+CloseBracket | Sets selection end marker and normalizes range |
| Read selection context | CapsLock+Quote | Announces normalized range context and confidence |
| Jump to selection start | CapsLock+J | Restores caret to start marker with fallback |
| Cancel selection markers | CapsLock+X | Exits marker mode with no side effects |
| Copy to clip slot | CapsLock+1 | Copies selection or clipboard into chosen slot |
| Paste from clip slot | CapsLock+2 | Pastes selected slot content with safety confirmation |
| Delete clip slot | CapsLock+3 | Deletes selected clip slot with confirmation |
| Describe clip slot | CapsLock+4 | Reads slot metadata and content summary |
| Merge mode append | CapsLock+M | Sets merge behavior to append |
| Merge mode replace | CapsLock+Shift+M | Sets merge behavior to replace |
| Merge divider line | CapsLock+L | Sets merge divider to line break separator |
| Merge divider space | CapsLock+U | Sets merge divider to single space separator |
| Merge divider paragraph | CapsLock+I | Sets merge divider to paragraph separator |

### Profile Keymap Variants

The following table defines profile-level key behavior.

| Profile | Behavior |
| --- | --- |
| Beginner | Announces command name and result summary after execution. Clipboard paste, delete, and edit use always-confirm and always-preview policies |
| Balanced | Announces concise status and confidence only. Clipboard paste and edit use adaptive confirmation and when-long preview |
| Expert | Minimal status output and fastest repeat execution. Clipboard paste uses no confirmation with no preview while destructive delete remains always-confirm |

### App-Aware Remapping

The following list defines remap behavior.

1. Allow per-app overrides for conflicting shortcuts.
2. Preserve global emergency stop in all profiles.
3. Block remaps that conflict with OS-reserved key combinations.
4. Require user confirmation before enabling risky remaps.

### Collision and Degradation Policy

The following list defines collision handling.

1. Detect collisions during profile load and on remap save.
2. If collision occurs at runtime, announce conflict and offer alternatives.
3. Fallback options: retry with alternate key, open palette with command prefilled, open mapping diagnostics.
4. Log collision events in diagnostics with app and key metadata.

### Multi-Press Safety Rules

1. Multi-press bindings must never shadow `cmd.system.emergencyStop`.
2. Destructive commands are disallowed on triple press without confirmation.
3. Profile-level setting must allow users to disable multi-press globally.
4. Discoverability prompt must include multi-press variants for current context.

## Accessibility Requirements

1. Every hotkey-triggered operation must emit equivalent speech and braille outcomes.
2. Virtualized surface must support full keyboard navigation with no pointer dependency.
3. Confidence and fallback options must always be available through direct hotkey and palette paths.
4. Error messages must include actionable next step in one sentence.

## Telemetry and Diagnostics

The following table defines required observability fields.

| Event | Required Fields |
| --- | --- |
| hotkeyExecuted | commandId, appId, profileId, success, latencyMs |
| hotkeyCollision | key, appId, losingCommandId, fallbackChosen |
| virtualizedOpened | resultId, sourceAppId, blockCount, openLatencyMs |
| virtualizedReturned | resultId, returnSuccess, driftDetected |
| virtualizedAction | resultId, blockType, actionId, success |

## Security and Safety Controls

1. Destructive actions cannot execute directly from hotkey without confirmation.
2. Any low-confidence adaptive action must require confirmation or degrade to suggestion mode.
3. Virtualized export operations must honor privacy policy and redaction rules.
4. Session logs must avoid storing sensitive content unless user opted in.

## Performance Targets

1. Direct hotkey command dispatch under 75 milliseconds local median.
2. Virtualized surface open under 150 milliseconds for cached results.
3. Structural navigation key response under 50 milliseconds.
4. Return-to-source completion under 250 milliseconds median.

## Acceptance Tests

The following list defines release gates for this spec.

1. Top 20 direct hotkeys execute in baseline apps or provide deterministic fallback.
2. Virtualized mode supports all required navigation and action keys.
3. Exit from virtualized mode restores exact source anchor in at least 95 percent of test runs.
4. Speech and braille parity tests pass for all Tier 1 commands.
5. Collision scanner catches known conflict fixtures with actionable remediation.
6. Beginner, balanced, and expert profiles apply expected verbosity behavior.
7. Single, double, and triple press bindings resolve deterministically under timing jitter fixtures.
8. Multi-press fallback behavior is announced when timing threshold is exceeded.

## Open Implementation Questions

1. Should CapsLock prefix be mandatory for all direct hotkeys in v1.
2. Which Tier 2 commands are allowed in v1 versus v2.
3. How strict should source anchor drift tolerance be before guided return.
4. What default threshold should trigger automatic virtualized mode.

## Delivery Plan

1. v1: Tier 1 hotkeys, virtualized core navigation, deterministic source return.
2. v1.1: profile-aware remap UX and collision diagnostics refinement.
3. v2: advanced block types, richer export actions, and adaptive key hinting.
