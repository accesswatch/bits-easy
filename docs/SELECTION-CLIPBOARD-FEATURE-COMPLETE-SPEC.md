# Baseline Selection and Clipboard Feature Complete Spec

## Purpose

This document provides complete feature-level decomposition for selection and clipboard management so parity can be tracked and closed at execution level.

## Scope

1. Selection lifecycle behaviors.
2. Clip slot and persistence behaviors.
3. Clipboard append and merge behaviors.
4. Cross-app fallback and recovery behaviors.
5. Profile-based user experience behaviors.

## Capability Groups

1. SnapSpan selection features.
2. PocketClips slot features.
3. MergeBoard clipboard merge features.
4. Selection and clipboard diagnostics features.
5. PocketClips Studio slot browsing and manual manipulation features.
6. PocketClips Library historical archive and folder model.

## Detailed Feature Catalog

| Feature ID | Feature | Baseline parity target | Status target | User experience detail |
| --- | --- | --- | --- | --- |
| SEL-001 | Mark selection start | Full | Build-Ready | Announces marker set with short source cue |
| SEL-002 | Mark selection end | Full | Build-Ready | Announces range summary and estimated size |
| SEL-003 | Speak selection context | Full | Build-Ready | Announces start and end snippets in one message |
| SEL-004 | Jump to selection start | Full | Build-Ready | Returns focus and caret to exact marker when possible |
| SEL-005 | Cancel marker mode | Full | Build-Ready | Safe exit with no side effects |
| SEL-006 | Selection drift handling | Full | Scoped | Announces nearest valid restore point and choices |
| SEL-007 | Selection in unsupported surfaces | Full | Scoped | Provides guided capture fallback options |
| SEL-008 | Selection confidence feedback | Full | Scoped | Announces confidence for adapter-derived ranges |
| CLIP-001 | Copy to slots 1 to 12 | Full | Build-Ready | Deterministic write to selected slot |
| CLIP-002 | Paste from slots 1 to 12 | Full | Build-Ready | Deterministic paste from selected slot |
| CLIP-003 | Protect slot | Full | Scoped | Protected slot cannot be overwritten |
| CLIP-004 | Unprotect slot | Full | Scoped | Slot protection can be safely toggled |
| CLIP-005 | Delete slot | Full | Build-Ready | Deletes only targeted slot |
| CLIP-006 | Edit slot content | Full | Scoped | Edit flow preserves slot integrity after save |
| CLIP-007 | Slot metadata | Full | Scoped | Stores source app, timestamp, and length |
| CLIP-008 | Last delete restore | Full | Scoped | One-step restore for accidental delete |
| CLIP-009 | Slot preview before paste | Full | Scoped | Optional preview in beginner and balanced profiles |
| CLIP-010 | Slot search and list | Full | Planned | Searchable slot index with concise summaries |
| CLIP-011 | Open slot browser | Full | Scoped | Keyboard-first view of all slots in one surface |
| CLIP-012 | View all slots with metadata | Full | Scoped | Each slot shows label, source, timestamp, size, and protection state |
| CLIP-013 | Sort and filter slot browser | Full | Scoped | Filter by source app, age, and protection state |
| CLIP-014 | Batch select and operate | Full | Planned | Multi-select slots for copy out, delete, protect, or export |
| CLIP-015 | Reorder slot assignments | Full | Planned | Move content between slots with conflict-safe prompts |
| CLIP-016 | Pin favorite slots | Full | Planned | Favorite slots are surfaced first in browse and paste flows |
| CLIP-017 | Split and merge slot contents | Full | Planned | Manual content shaping without leaving keyboard workflow |
| CLIP-018 | Compare two slots | Full | Planned | Quick diff-style preview for deciding merge or replace |
| CLIP-019 | Export and import slot pack | Full | Planned | Portable slot bundles with integrity checks |
| CLIP-020 | Historical clip archive | Full | Planned | Persist clips beyond active slot lifespan with timeline browsing |
| CLIP-021 | Folder and category taxonomy | Full | Planned | User-defined folders and categories for curated organization |
| CLIP-022 | Move clip into folder | Full | Planned | Clip can be moved from active slot into library folder |
| CLIP-023 | Link clip into folder | Full | Planned | Folder link points to clip while keeping original slot reference |
| CLIP-024 | Retain slot number alias | Full | Planned | Optional stable slot alias is preserved after folder move |
| CLIP-025 | Slot alias conflict resolver | Full | Planned | Deterministic prompt when alias collision occurs |
| CLIP-026 | Multi-folder linking | Full | Planned | One clip can be linked into multiple folders without duplication |
| CLIP-027 | Folder-level smart views | Full | Planned | Dynamic views such as recent, pinned, by source, by project |
| CLIP-028 | Archive restore to slot | Full | Planned | Restore historical clip back to selected active slot |
| CLIP-029 | Archive retention policy | Full | Planned | Keep forever, age out, or pin-protected retention rules |
| MERGE-001 | Append mode | Full | Build-Ready | New captures append to active merge buffer |
| MERGE-002 | Replace mode | Full | Build-Ready | New captures replace active merge buffer |
| MERGE-003 | Divider line | Full | Build-Ready | Inserts line divider between segments |
| MERGE-004 | Divider space | Full | Build-Ready | Inserts single-space divider between segments |
| MERGE-005 | Divider paragraph | Full | Build-Ready | Inserts paragraph divider between segments |
| MERGE-006 | Custom separator | Full | Scoped | User-defined separator between segments |
| MERGE-007 | Clear on paste | Full | Scoped | Clears merge buffer only when enabled |
| MERGE-008 | Source tag append | Full | Scoped | Optional source metadata per merged segment |
| MERGE-009 | Merge profile presets | Full | Scoped | Meeting, email, research profile presets |
| MERGE-010 | Merge reproducibility | Full | Scoped | Same input plus profile yields same output |
| UX-001 | Beginner profile guidance | Full | Build-Ready | Rich prompts and explicit confirmations |
| UX-002 | Balanced profile guidance | Full | Build-Ready | Concise status with fallback hints |
| UX-003 | Expert profile guidance | Full | Build-Ready | Minimal prompts and high speed |
| UX-004 | Speech and braille parity | Full | Build-Ready | All critical outcomes reported in both channels |
| UX-005 | No silent failure rule | Full | Build-Ready | Every failure includes next actionable step |
| QA-001 | Per-app selection reliability metrics | Full | Scoped | Records success and drift by app |
| QA-002 | Slot protection violation metrics | Full | Scoped | Tracks blocked overwrite attempts |
| QA-003 | Merge fallback metrics | Full | Scoped | Tracks fallback invocation and reason |

## Command-Level Feature Detail

### Selection Commands

1. `cmd.selection.markStart`: sets marker and reads short location summary.
2. `cmd.selection.markEnd`: sets marker, normalizes range, reads range summary.
3. `cmd.selection.readContext`: reads start and end snippets with confidence.
4. `cmd.selection.jumpStart`: restores caret to marker with drift fallback.
5. `cmd.selection.cancel`: exits marker workflow safely.

### Clip Commands

1. `cmd.clip.copyToSlot`: writes selection or clipboard to a slot.
2. `cmd.clip.pasteFromSlot`: inserts slot content to destination.
3. `cmd.clip.protectSlot`: blocks write operations to slot.
4. `cmd.clip.unprotectSlot`: re-enables slot writes.
5. `cmd.clip.deleteSlot`: removes slot content and metadata.
6. `cmd.clip.editSlot`: edits existing slot content before save.
7. `cmd.clip.describeSlot`: reports slot metadata and content summary.
8. `cmd.clip.browser.open`: opens PocketClips Studio with all slots.
9. `cmd.clip.browser.filter`: filters slot list by source, age, or state.
10. `cmd.clip.browser.sort`: sorts slot list by recency, size, or name.
11. `cmd.clip.browser.batchAction`: applies action to selected slots.
12. `cmd.clip.browser.compare`: compares two slots with concise diff summary.
13. `cmd.clip.browser.exportPack`: exports selected slots as portable pack.
14. `cmd.clip.browser.importPack`: imports slot pack with conflict resolution.
15. `cmd.clip.library.open`: opens historical library view.
16. `cmd.clip.library.createFolder`: creates folder in library taxonomy.
17. `cmd.clip.library.moveToFolder`: moves clip to folder.
18. `cmd.clip.library.linkToFolder`: links clip to folder while preserving source.
19. `cmd.clip.library.retainSlotAlias`: toggles slot number alias retention.
20. `cmd.clip.library.restoreToSlot`: restores historical clip into active slot.
21. `cmd.clip.library.setRetentionPolicy`: sets per-folder or per-clip retention rule.
22. `cmd.clip.library.listLinkedLocations`: reports all folders linked to a clip.

### Merge Commands

1. `cmd.merge.setModeAppend`: enables append behavior.
2. `cmd.merge.setModeReplace`: enables replace behavior.
3. `cmd.merge.setDivider`: sets divider strategy line, space, paragraph.
4. `cmd.merge.setCustomSeparator`: sets custom separator text.
5. `cmd.merge.toggleClearOnPaste`: toggles clear-after-paste policy.
6. `cmd.merge.applyProfile`: applies named merge profile.
7. `cmd.merge.commit`: commits merge output to destination.

## UX Requirements by Profile

| Scenario | Beginner | Balanced | Expert |
| --- | --- | --- | --- |
| Copy to slot | Announces slot and source | Announces slot | Optional short earcon only |
| Paste from slot | Announces slot and preview | Announces slot and length | Executes with minimal prompt |
| Protected slot overwrite | Blocks and explains remediation | Blocks and concise remediation | Blocks with short failure cue |
| Merge commit | Preview plus confirmation | Preview for long output only | Immediate if safe gate allows |
| Selection drift | Guided options read in order | Concise drift plus retry options | Minimal drift alert plus retry key |
| Slot browser | Structured reading mode with hints | Compact list plus quick actions | Dense list plus direct action keys |
| Historical library | Guided move versus link suggestions | Concise folder actions | Fast folder and alias actions with minimal prompts |

## Slot Identity and Folder Linking Model

The model separates clip identity from slot placement so users can organize freely.

1. `clipId`: immutable identity for a captured item.
2. `slotId`: current active slot placement pointer.
3. `slotAlias`: optional user-facing retained slot number such as Slot 3.
4. `folderLink`: non-owning pointer from folder to clip identity.
5. `archiveState`: active, archived, pinned, or expired.

Move semantics:

1. Move transfers active slot placement into folder-managed state.
2. Optional retain-slot-alias preserves recognizable slot number reference.
3. Active slot can be freed for new captures while alias points to moved clip.

Link semantics:

1. Link keeps original slot placement and adds folder pointers.
2. Multiple folders can reference one clip identity.
3. Updates to clip metadata are reflected across all links.

## Magical Differentiators vs Baseline for Clipboard and Selection

1. PocketClips Studio all-slot browser: one command opens a complete, metadata-rich slot workspace.
2. Provenance-first clip model: source app and capture age are visible and actionable.
3. Manual manipulation without mode confusion: split, merge, reorder, and compare slots through deterministic key flows.
4. Batch operations with safety rails: bulk protect, delete, export, and restore with rollback cues.
5. Profile-aware interaction density: same power surface with beginner guidance and expert speed.
6. Drift-safe context return: users do not lose place after complex clipboard operations.
7. Historical memory workspace: clips evolve from temporary slots into organized long-term knowledge assets.
8. Move-or-link freedom: users choose archival strategy without losing slot familiarity.
9. Stable slot aliases: users can retain trusted slot numbers even after deep organization into folders.

## Closure Criteria for Full Parity in Scope

All items in this document are considered fully mapped only when all criteria are true.

1. Every feature in the catalog has a mapped command path or explicit non-command UX path.
2. Every feature has acceptance tests in sprint backlog tickets.
3. Every feature has deterministic feedback behavior defined for speech and braille.
4. Every feature has fallback behavior defined for unsupported context or drift.
5. Every feature has telemetry or diagnostics coverage where failure risk is non-trivial.

## Verification Checklist

1. Selection workflows pass in Edge, Chrome, Firefox, Outlook, Word, Notepad, and VS Code.
2. Clip slot lifecycle copy, paste, protect, unprotect, delete, edit passes end-to-end.
3. Merge mode and divider behavior passes deterministic output tests.
4. Profile behavior differs as intended for prompt density and confirmation policy.
5. Recovery behavior passes drift and fallback fixtures.
6. Slot browser lists all slots with accurate metadata and supports keyboard-only operation.
7. Manual slot manipulation operations split, merge, reorder, compare are deterministic and reversible where supported.
8. Historical library supports folder creation, move, link, restore, and alias retention with deterministic outcomes.
9. Linked clips maintain consistent metadata across all linked folder views.

## Implementation Reconciliation Snapshot (2026-05-22)

This section reconciles planning intent with current runtime behavior so roadmap and implementation are not interpreted as contradictory.

### Implemented now (runtime + tests)

1. Selection marker lifecycle, context, jump, cancel, marker status metadata, and telemetry payloads.
2. PocketClips browser open/filter/sort/search, compare, split, merge, reorder, batch actions, export/import.
3. Favorite slot pin/unpin state in browser workflows.
4. Clip library open/create/rename/delete folder, move/link, retain alias with deterministic conflict strategies, restore to slot, retention policy, linked locations.
5. Smart-view style library payload summaries (recent, pinned, by-source, by-category counts).

### Planned scope still not fully closed in implementation depth

1. Cross-app UX parity tuning in live NVDA usage remains a manual validation stream.

## Implementation Notes

1. Use existing E01 and E17 tracks as execution base.
2. Promote scoped items to build-ready through focused closure tickets.
3. Keep command IDs stable once Tier 1 contracts are published.

## Summary

This spec closes feature decomposition depth for clipboard and selection domains by enumerating all expected capabilities, user-facing behavior, and closure criteria for parity-quality execution.


