# BITS-EASY Full Guided Keystroke Test Plan

## 1. Purpose

This plan is the complete manual test flow for BITS-EASY.

Goals:

1. Start with selection workflows first.
2. Keep execution simple and guided.
3. Provide every keystroke for each test step.
4. Cover all features, including all commands in `config/hotkeys/commands/tier1-commands.v1.json`.

## 2. Test Environment

1. Windows 10 or 11, 64-bit.
2. NVDA 2026.1 x64.
3. Latest BITS-EASY add-on installed.
4. Test apps ready: Notepad, Edge (or Chrome), Outlook, VS Code.

## 3. Keystroke Conventions

1. `Grave` means the key used as the BITS-EASY prefix.
2. `Grave+X` means hold `Grave`, press `X`, release both.
3. `Palette path` always means:
   1. Press `Grave`.
   2. Type full command ID, for example `cmd.selection.summarize`.
   3. Press `Enter`.
4. For confirm dialogs:
   1. Press `Tab` to move to the primary action.
   2. Press `Enter` to confirm.
   3. Press `Escape` to cancel.

## 4. Logging Template

Use one row per test execution.

The following table records test execution, expected behavior, and evidence links.

| Test ID | App | Command ID | Invocation Path | Result (PASS/FAIL) | Notes |
| --- | --- | --- | --- | --- | --- |
| SEL-01 | Notepad | cmd.selection.summarize | Grave+S |  |  |

## 5. Selection First Guided Flow

Run this section first, in this exact order.

### 5.1 Selection Baseline Setup

1. Open Notepad.
2. Type this sample text:
   1. `Sprint planning is Friday at 2 PM.`
   2. `Need to send agenda and book room.`
   3. `Open question: who owns follow up tasks?`
3. Press `Ctrl+A`.
4. Press `Ctrl+C`.

Expected:

1. Text is selected.
2. Clipboard contains the sample text.

### 5.2 Summarize Selection (Direct Hotkey)

1. In Notepad, keep text selected.
2. Press `Grave+S`.
3. If low-confidence confirmation appears:
   1. Press `Tab` until confirm action is focused.
   2. Press `Enter`.
4. Press `Grave+V` to open latest virtualized result.

Expected:

1. Summary result opens.
2. Result is understandable and related to selected text.

### 5.3 Extract Actions (Direct Hotkey)

1. Return to Notepad window.
2. Re-select the same text with `Ctrl+A`.
3. Press `Grave+A`.
4. If low-confidence confirmation appears:
   1. Press `Tab` to confirm.
   2. Press `Enter`.
5. Press `Grave+V`.

Expected:

1. Action items are listed.
2. At least one action captures "send agenda" or "book room".

### 5.4 Rewrite for Beginners (Direct Hotkey)

1. Return to Notepad.
2. Select all text with `Ctrl+A`.
3. Press `Grave+R`.
4. Confirmation is required:
   1. Press `Tab` to primary confirm.
   2. Press `Enter`.
5. Press `Grave+V` to inspect output.

Expected:

1. Output is simplified.
2. Meaning is preserved.

### 5.5 Virtualized Result Navigation for Selection Outputs

1. With virtualized result open, press `Grave+RightArrow`.
2. Press `Grave+LeftArrow`.
3. Press `Grave+C` to copy current block.
4. Press `Grave+Shift+C` to copy all blocks.
5. Press `Grave+K` to read confidence.
6. Press `Grave+F` to open fallbacks.
7. Press `Grave+Backspace` to return to source.

Expected:

1. Block navigation works in both directions.
2. Copy actions place expected text in clipboard.
3. Confidence and fallback surfaces are available.
4. Return to source moves focus back correctly.

### 5.6 Selection Commands Through Palette Path

Run all three selection commands through palette in addition to direct hotkeys.

1. Select test text in Notepad.
2. Press `Grave`.
3. Type `cmd.selection.summarize`.
4. Press `Enter`.
5. Repeat steps 1 to 4 for:
   1. `cmd.selection.extractActions`
   2. `cmd.selection.rewriteBeginner`

Expected:

1. Each command runs from palette path.
2. Behavior matches direct hotkey behavior.

## 6. Core Global and Safety Controls

### 6.1 Hotkey Help and Diagnostics

1. Press `Grave+Slash`.
2. Press `Grave` twice quickly (double press) if configured.
3. Press `Grave` three times quickly (triple press) for diagnostics.
4. Press and hold `Grave` for about 600 ms.

Expected:

1. Available hotkeys surface opens.
2. Multi-press and hold triggers behave as configured.

### 6.2 Journal and Emergency Controls

1. Press `Grave+Shift+J`.
2. Press `Grave+Escape`.

Expected:

1. Undo last reversible action executes safely.
2. Emergency stop command responds immediately.

## 7. Direct-Bound Hotkey Matrix

Run each direct chord once, then run the same command through the palette path.

The following table maps default bound chords to command IDs for dual-path validation.

| Key Chord | Scope | Command ID |
| --- | --- | --- |
| Grave | global | cmd.palette.open |
| Grave+Q | global | cmd.capture.quickInbox |
| Grave+O | global | cmd.integration.itemChooser.open |
| Grave+Shift+O | global | cmd.integration.itemChooser.openOcr |
| Grave+Y | global | cmd.integration.glow.health |
| Grave+E | global | cmd.integration.glow.audit |
| Grave+Shift+V | global | cmd.integration.glow.fix |
| Grave+Shift+K | global | cmd.integration.glow.convert |
| Grave+Shift+L | global | cmd.integration.glow.report |
| Grave+S | global | cmd.selection.summarize |
| Grave+A | global | cmd.selection.extractActions |
| Grave+R | global | cmd.selection.rewriteBeginner |
| Grave+V | global | cmd.result.virtualOpen |
| Grave+Backspace | global | cmd.context.returnSource |
| Grave+Slash | global | cmd.help.availableHotkeys |
| Grave+Shift+J | global | cmd.journal.undoLast |
| Grave+Escape | global | cmd.system.emergencyStop |
| Grave+C | virtualized | cmd.result.block.copy |
| Grave+Shift+C | virtualized | cmd.result.copyAll |
| Grave+RightArrow | virtualized | cmd.result.block.next |
| Grave+LeftArrow | virtualized | cmd.result.block.previous |
| Grave+P | virtualized | cmd.result.pinInbox |
| Grave+K | virtualized | cmd.result.readConfidence |
| Grave+F | virtualized | cmd.result.openFallbacks |
| Grave+B | virtualized | cmd.result.toggleSpeechDensity |
| Grave+Z | virtualized | cmd.result.toggleBrailleDensity |

## 8. All-Commands Completion Loop (Full Feature Coverage)

This section is required to claim complete feature coverage.

### 8.1 How to Execute Every Command

For each command ID listed in `config/hotkeys/commands/tier1-commands.v1.json`:

1. If command has a direct bound hotkey in `config/hotkeys/global-keymap.v1.json`:
   1. Run direct chord once.
   2. Validate expected behavior.
2. Run command via palette path:
   1. Press `Grave`.
   2. Type exact command ID.
   3. Press `Enter`.
3. If parameters are requested:
   1. Type requested value.
   2. Press `Tab` to next field.
   3. Press `Enter` on submit.
4. If confirmation is requested:
   1. Press `Tab` to confirm action.
   2. Press `Enter`.
5. If command is mutating:
   1. Validate data or state change.
   2. Run rollback command when available.
6. Record PASS or FAIL in the logging table.

### 8.2 Family-by-Family Order

Use this fixed order to keep testing simple and reproducible:

1. `cmd.selection.*`
2. `cmd.result.*`
3. `cmd.context.*`
4. `cmd.capture.*`
5. `cmd.journal.*`
6. `cmd.integration.*`
7. `cmd.help.*`
8. `cmd.profile.*`
9. `cmd.system.*`
10. Remaining families in alphabetical order from the catalog.

## 9. Pass Criteria

Release manual test pass requires all of the following:

1. Section 5 selection flow completed with PASS results.
2. Every bound command tested via direct hotkey and palette path.
3. Every command ID in tier1 catalog executed at least once via palette path.
4. All critical failures resolved or explicitly waived with risk notes.

## 10. Failure Triage Template

Use this template for each failure.

1. App and surface.
2. Exact keystrokes used.
3. Command ID.
4. Expected result.
5. Actual result.
6. Repro rate across 3 retries.
7. Fallback behavior observed.
