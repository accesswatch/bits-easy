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

1. `EASY key` is the BITS-EASY prefix key (physical grave key by default).
2. `EASY then X` means press and release EASY, then press `X`.
3. Existing notation like `Grave+X` in tables still maps to `EASY then X`.
4. `Palette path` always means:
   1. Press `Grave`.
   2. Type full command ID, for example `cmd.selection.summarize`.
   3. Press `Enter`.
5. For confirm dialogs:
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

### 5.7 Selection Marker Workflow (Full Selection Feature Coverage)

Run this to cover marker-based selection features that do not rely only on visible highlight.

1. Open Notepad and type: `alpha bravo charlie delta echo foxtrot`.
2. Move caret to before `bravo` using arrow keys.
3. Press `Grave+OpenBracket` to run `cmd.selection.markStart`.
4. Move caret to after `delta`.
5. Press `Grave+CloseBracket` to run `cmd.selection.markEnd`.
6. Press `Grave+Semicolon` to run `cmd.selection.markerStatus`.
7. Press `Grave+Quote` to run `cmd.selection.readContext`.
8. Press `Grave+J` to run `cmd.selection.jumpStart`.
9. Press `Grave+S` to summarize marker range.
10. Press `Grave+X` to run `cmd.selection.cancel`.
11. Press `Grave+Semicolon` again to verify markers are cleared.

Expected:

1. Start and end markers are set and reported.
2. Read context includes nearby text around marker range.
3. Jump returns caret to marker start position.
4. Selection actions execute against marker range.
5. Cancel clears marker state.

## 6. Clipboard Capabilities Guided Flow

Run this section immediately after Section 5.

### 6.1 Clipboard Baseline and Slot Flow

1. In Notepad, type `Clipboard test payload one`.
2. Press `Ctrl+A`.
3. Press `Ctrl+C`.
4. Press `Grave+1` to run `cmd.clip.copyToSlot`.
5. Press `Grave+4` to run `cmd.clip.describeSlot`.
6. Move caret to a blank line.
7. Press `Grave+2` to run `cmd.clip.pasteFromSlot`.
8. Press `Ctrl+V` only if app requires explicit paste after command.

Expected:

1. Clipboard content is captured into active slot.
2. Slot description reports non-empty slot data.
3. Paste from slot reproduces payload.

### 6.2 Function-Key Slot Sweep (F1 to F12)

Run this full sweep for slot commands and verify each index path.

For each slot key from `F1` through `F12`:

1. Press `Grave+F{n}` to run `cmd.clip.selectSlot` for slot `n`.
2. Copy sample text in app with `Ctrl+C`.
3. Press `Grave+Shift+F{n}` to run `cmd.clip.copyToSlot` for slot `n`.
4. Press `Grave+Windows+F{n}` to run `cmd.clip.describeSlot` for slot `n`.
5. Move to destination field.
6. Press `Grave+Control+F{n}` to run `cmd.clip.pasteFromSlot` for slot `n`.

Expected:

1. Slot index selection works for all 12 slots.
2. Copy and paste operations route to the selected slot.
3. Slot description maps to the correct slot each time.

### 6.3 Protection, Edit, Delete, and Recovery

1. Select slot with `Grave+F1`.
2. Press `Grave+Shift+P` to run `cmd.clip.protectSlot`.
3. Attempt overwrite with `Grave+Shift+F1`.
4. Verify overwrite is blocked or gated.
5. Press `Grave+Shift+U` to run `cmd.clip.unprotectSlot`.
6. Press `Grave+Shift+E` to run `cmd.clip.editSlot` and save a small text change.
7. Press `Grave+3` to run `cmd.clip.deleteSlot`.
8. Press `Grave+Windows+F1` to verify slot reports empty or deleted state.

Expected:

1. Protected slots cannot be overwritten without expected flow.
2. Unprotect restores write behavior.
3. Edit updates slot payload.
4. Delete clears slot content.

### 6.4 Clipboard Browser Features

1. Press `Grave+Shift+6` to open clip browser with `cmd.clip.browser.open`.
2. In palette, run the following commands one by one:
   1. `cmd.clip.browser.search`
   2. `cmd.clip.browser.filter`
   3. `cmd.clip.browser.sort`
   4. `cmd.clip.browser.compare`
   5. `cmd.clip.browser.reorder`
   6. `cmd.clip.browser.split`
   7. `cmd.clip.browser.merge`
   8. `cmd.clip.browser.batchAction`
   9. `cmd.clip.browser.exportPack`
   10. `cmd.clip.browser.importPack`

Expected:

1. Browser opens and remains interactive.
2. Search, filter, and sort alter the listing as expected.
3. Compare, reorder, split, and merge execute without crashes.
4. Export and import pack flows complete with clear status.

### 6.5 Clipboard Library Features

1. Press `Grave+6` to run `cmd.clip.library.open`.
2. Run each command through palette path:
   1. `cmd.clip.library.ingestSlot`
   2. `cmd.clip.library.createFolder`
   3. `cmd.clip.library.renameFolder`
   4. `cmd.clip.library.deleteFolder`
   5. `cmd.clip.library.moveToFolder`
   6. `cmd.clip.library.linkToFolder`
   7. `cmd.clip.library.retainSlotAlias`
   8. `cmd.clip.library.assignCategory`
   9. `cmd.clip.library.removeCategory`
   10. `cmd.clip.library.restoreToSlot`
   11. `cmd.clip.library.setRetentionPolicy`
   12. `cmd.clip.library.listLinkedLocations`
   13. `cmd.clip.library.timeline`

Expected:

1. Library opens and persists state changes.
2. Folder and category operations complete correctly.
3. Restore and retention features behave predictably.
4. Timeline and linked-location views are readable and accurate.

### 6.6 Clipboard-Adjacent Cross-Feature Commands

Run these commands because they depend on clipboard or selected text payloads.

1. `cmd.tags.session.tagFromSelection`
2. `cmd.table.capture.exportClipboard`

Execution steps for each:

1. Prepare source content in app.
2. Press `Grave`.
3. Type command ID.
4. Press `Enter`.

Expected:

1. Tag-from-selection extracts current selection path or text correctly.
2. Table capture export writes clipboard payload in expected shape.

### 6.7 Clipboard Command Coverage Checklist

Mark each command PASS or FAIL during execution.

| Command ID | Direct Hotkey | Palette Required | Result |
| --- | --- | --- | --- |
| cmd.clip.copyToSlot | Grave+1, Grave+Shift+F1..F12 | No |  |
| cmd.clip.selectSlot | Grave+F1..F12 | No |  |
| cmd.clip.pasteFromSlot | Grave+2, Grave+Control+F1..F12 | No |  |
| cmd.clip.protectSlot | Grave+Shift+P | No |  |
| cmd.clip.unprotectSlot | Grave+Shift+U | No |  |
| cmd.clip.deleteSlot | Grave+3 | No |  |
| cmd.clip.editSlot | Grave+Shift+E | No |  |
| cmd.clip.describeSlot | Grave+4, Grave+Windows+F1..F12 | No |  |
| cmd.clip.browser.open | Grave+Shift+6 | No |  |
| cmd.clip.browser.search |  | Yes |  |
| cmd.clip.browser.filter |  | Yes |  |
| cmd.clip.browser.sort |  | Yes |  |
| cmd.clip.browser.compare |  | Yes |  |
| cmd.clip.browser.reorder |  | Yes |  |
| cmd.clip.browser.split |  | Yes |  |
| cmd.clip.browser.merge |  | Yes |  |
| cmd.clip.browser.batchAction |  | Yes |  |
| cmd.clip.browser.exportPack |  | Yes |  |
| cmd.clip.browser.importPack |  | Yes |  |
| cmd.clip.library.open | Grave+6 | No |  |
| cmd.clip.library.ingestSlot |  | Yes |  |
| cmd.clip.library.createFolder |  | Yes |  |
| cmd.clip.library.renameFolder |  | Yes |  |
| cmd.clip.library.deleteFolder |  | Yes |  |
| cmd.clip.library.moveToFolder |  | Yes |  |
| cmd.clip.library.linkToFolder |  | Yes |  |
| cmd.clip.library.retainSlotAlias |  | Yes |  |
| cmd.clip.library.assignCategory |  | Yes |  |
| cmd.clip.library.removeCategory |  | Yes |  |
| cmd.clip.library.restoreToSlot |  | Yes |  |
| cmd.clip.library.setRetentionPolicy |  | Yes |  |
| cmd.clip.library.listLinkedLocations |  | Yes |  |
| cmd.clip.library.timeline |  | Yes |  |
| cmd.tags.session.tagFromSelection | Grave+Alt+Shift+G | Yes (also run palette) |  |
| cmd.table.capture.exportClipboard |  | Yes |  |

## 7. Core Global and Safety Controls

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

## 8. Direct-Bound Hotkey Matrix

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

## 9. All-Commands Completion Loop (Full Feature Coverage)

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
2. `cmd.clip.*`
3. `cmd.result.*`
4. `cmd.context.*`
5. `cmd.capture.*`
6. `cmd.journal.*`
7. `cmd.integration.*`
8. `cmd.help.*`
9. `cmd.profile.*`
10. `cmd.system.*`
11. Remaining families in alphabetical order from the catalog.

## 10. Pass Criteria

Release manual test pass requires all of the following:

1. Section 5 selection flow completed with PASS results.
2. Section 6 clipboard flow completed with PASS results.
3. Every bound command tested via direct hotkey and palette path.
4. Every command ID in tier1 catalog executed at least once via palette path.
5. All critical failures resolved or explicitly waived with risk notes.

## 11. Failure Triage Template

Use this template for each failure.

1. App and surface.
2. Exact keystrokes used.
3. Command ID.
4. Expected result.
5. Actual result.
6. Repro rate across 3 retries.
7. Fallback behavior observed.
