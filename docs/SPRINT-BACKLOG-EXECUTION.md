# Sprint Backlog Execution Plan

## Scope
This backlog translates the PRD decomposition into sprint-ready tickets.

Sources:
1. PRD epic and story-pack decomposition.
2. Dependency sequencing and release priorities.
3. Accessibility and AI guardrails.

## Usage
1. Treat each ticket ID as a work item key.
2. Keep acceptance tests binary: pass or fail.
3. Do not mark a ticket complete until all acceptance tests pass.

## Labels
Use these labels on all tickets:
- Priority: P0, P1, P2, P3
- Type: Core, Adapter, AI, Accessibility, QA, Infra
- Risk: Low, Medium, High
- Confidence: VeryHigh, High, Medium, Low
- Release: v1, v2, v3, v4

## Sprint Phases
1. Sprint Group A (Foundations): E01, E13, E15, E17 baseline
2. Sprint Group B (Core Productivity): E03, E04, E05, E06
3. Sprint Group C (Structured and AI): E10, E12
4. Sprint Group D (Calendar and Social): E07, E08, E09, E11
5. Sprint Group E (Lower Priority): E14
6. Sprint Group F (Magical 1.0): E18

## Ticket Backlog

## E01 Selection and Clip Intelligence

### TKT-E01-001 SP-E01-A Selection markers and context
- Priority: P0
- Risk: Medium
- Confidence: VeryHigh
- Release: v1
- Dependencies: Core command bus, feedback layer
- Description: Implement begin-selection marker, end-selection marker, context announce, and jump-back.
- Acceptance tests:
1. Mark start and end works in supported text surfaces.
2. Context announce includes start snippet and end snippet.
3. Jump-back returns cursor to exact marker location.
4. Escape exits marker mode without side effects.

### TKT-E01-002 SP-E01-B Clip slots 1 to 12
- Priority: P0
- Risk: Medium
- Confidence: VeryHigh
- Release: v1
- Dependencies: Storage service, feedback layer
- Description: Implement copy to slot, paste from slot, protect and unprotect, delete, and edit.
- Acceptance tests:
1. Copy and paste to all 12 slots function deterministically.
2. Protected slot cannot be overwritten.
3. Delete removes only selected slot.
4. Edited slot content persists after restart.

### TKT-E01-003 SP-E01-C Clipboard append engine
- Priority: P0
- Risk: Medium
- Confidence: VeryHigh
- Release: v1
- Dependencies: Clipboard abstraction
- Description: Implement append mode, replace mode, divider options, custom separator, and clear-on-paste behavior.
- Acceptance tests:
1. Append mode and replace mode toggle correctly.
2. Divider modes line, space, paragraph produce expected output.
3. Custom separator inserts between appended segments.
4. Clear-on-paste only executes when enabled.

### TKT-E01-004 SP-E01-D Text expansion and primary quick insert
- Priority: P0
- Risk: Low
- Confidence: High
- Release: v1
- Dependencies: Storage service
- Description: Implement reusable text expansions, abbreviation trigger, primary quick insert shortcut.
- Acceptance tests:
1. Abbreviation expands exact mapped text.
2. Expansion list can be viewed, renamed, and deleted.
3. Primary quick insert executes in text fields.
4. Conflicting abbreviation prompts user with resolution choice.

### TKT-E01-005 SP-E01-E Slot metadata and preview UX
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: E01 clip storage, feedback layer
- Description: Add slot metadata persistence and profile-aware slot preview behavior before paste.
- Spec reference: SELECTION-CLIPBOARD-FEATURE-COMPLETE-SPEC.md
- Acceptance tests:
1. Slot metadata stores source app, timestamp, and content length.
2. Beginner and balanced profiles announce slot preview before paste.
3. Expert profile can skip preview and still request metadata on demand.

### TKT-E01-006 SP-E01-F Selection drift and fallback UX
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: E01 selection engine, E17 context provider
- Description: Implement deterministic drift handling and guided fallbacks for selection restore failures.
- Spec reference: SELECTION-CLIPBOARD-FEATURE-COMPLETE-SPEC.md
- Acceptance tests:
1. Drift events announce nearest valid restore target.
2. Users can retry exact restore or choose manual return options.
3. No selection restore failure exits without actionable next step.

### TKT-E01-007 SP-E01-G Merge profile determinism and source tags
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: E01 merge engine, E17 orchestration
- Description: Implement deterministic merge profile behavior with source tagging and reproducibility checks.
- Spec reference: SELECTION-CLIPBOARD-FEATURE-COMPLETE-SPEC.md
- Acceptance tests:
1. Identical inputs with identical profile settings produce identical output.
2. Source tags append correctly when enabled.
3. Merge output summaries are announced before apply for long outputs.

### TKT-E01-008 SP-E01-H Clip edit and protect closure
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: E01 clip service, validation layer
- Description: Move clip protect, unprotect, and edit capabilities from scoped to build-ready with full guardrail coverage.
- Spec reference: SELECTION-CLIPBOARD-FEATURE-COMPLETE-SPEC.md
- Acceptance tests:
1. Protected slot blocks overwrite across all write paths.
2. Unprotect operation restores write behavior without data loss.
3. Edit slot flow persists safely and supports rollback on failed save.

### TKT-E01-009 SP-E01-I Clipboard and selection parity closure gate
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: E01 suite completion, QA matrix
- Description: Add parity closure gate for all clipboard and selection features defined in complete spec.
- Spec reference: SELECTION-CLIPBOARD-FEATURE-COMPLETE-SPEC.md
- Acceptance tests:
1. Every catalog feature has pass or fail evidence in test artifacts.
2. Speech and braille parity checks pass for all critical outcomes.
3. Unsupported context and drift fixtures pass no-silent-failure requirements.

### TKT-E01-010 SP-E01-J PocketClips Studio all-slot browser
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1.1
- Dependencies: E01 clip service, E17 renderer and feedback layer
- Description: Implement a keyboard-first all-slot browser with structured metadata and fast actions.
- Spec reference: SELECTION-CLIPBOARD-FEATURE-COMPLETE-SPEC.md
- Acceptance tests:
1. Browser displays all slots with label, source, age, size, and protection state.
2. Users can filter and sort slots using deterministic keyboard paths.
3. Speech and braille output are equivalent for focused slot details.

### TKT-E01-011 SP-E01-K Manual slot manipulation workflows
- Priority: P1
- Risk: Medium
- Confidence: MediumHigh
- Release: v1.1
- Dependencies: E01 clip service, E01 metadata model
- Description: Add manual manipulation workflows for reorder, compare, split, merge, and batch actions.
- Spec reference: SELECTION-CLIPBOARD-FEATURE-COMPLETE-SPEC.md
- Acceptance tests:
1. Users can reorder slot content safely with overwrite confirmation.
2. Compare operation reports concise content diff summary.
3. Split and merge slot operations produce deterministic outcomes.
4. Batch protect and delete operations include explicit safety confirmation.

### TKT-E01-012 SP-E01-L Slot pack portability and restore
- Priority: P2
- Risk: Medium
- Confidence: MediumHigh
- Release: v2
- Dependencies: E01 clip service, export and import infrastructure
- Description: Add export and import for slot packs with integrity validation and conflict-safe restore.
- Spec reference: SELECTION-CLIPBOARD-FEATURE-COMPLETE-SPEC.md
- Acceptance tests:
1. Exported slot pack restores on a second machine without corruption.
2. Import conflict workflow preserves existing data unless user confirms replacement.
3. Integrity checks reject malformed or incompatible slot pack files.

### TKT-E01-013 SP-E01-M Historical clip library foundation
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1.2
- Dependencies: E01 clip identity model, storage migration layer
- Description: Implement historical clip archive with timeline browsing and retention states.
- Spec reference: SELECTION-CLIPBOARD-FEATURE-COMPLETE-SPEC.md
- Acceptance tests:
1. Clips persist in historical library beyond active slot churn.
2. Users can browse historical clips by recency and source metadata.
3. Archive state active, archived, pinned, expired is stored and surfaced correctly.

### TKT-E01-014 SP-E01-N Folder taxonomy and clip categorization
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1.2
- Dependencies: E01 library foundation
- Description: Add folder and category organization for historical clips with keyboard-first operations.
- Spec reference: SELECTION-CLIPBOARD-FEATURE-COMPLETE-SPEC.md
- Acceptance tests:
1. Users can create, rename, and remove folders without data loss.
2. Users can assign clips to categories and filter by folder or category.
3. Speech and braille parity is maintained for folder operations.

### TKT-E01-015 SP-E01-O Move versus link clip behavior
- Priority: P1
- Risk: Medium
- Confidence: MediumHigh
- Release: v1.2
- Dependencies: E01 library and identity model
- Description: Implement explicit move-to-folder and link-to-folder semantics with multi-folder links.
- Spec reference: SELECTION-CLIPBOARD-FEATURE-COMPLETE-SPEC.md
- Acceptance tests:
1. Move operation changes ownership to folder-managed state.
2. Link operation preserves source placement and adds folder references.
3. A clip can be linked into multiple folders without duplication or drift.

### TKT-E01-016 SP-E01-P Retain slot alias after move
- Priority: P1
- Risk: Medium
- Confidence: MediumHigh
- Release: v1.2
- Dependencies: E01 move versus link behavior
- Description: Support optional retained slot number aliases for moved clips with conflict-safe resolution.
- Spec reference: SELECTION-CLIPBOARD-FEATURE-COMPLETE-SPEC.md
- Acceptance tests:
1. User can retain original slot alias when moving clip into folder.
2. Alias collision prompts deterministic resolution options.
3. Alias remains searchable and addressable from clip browser and command surface.

### TKT-E01-017 SP-E01-Q Restore archived clip to active slot
- Priority: P2
- Risk: Medium
- Confidence: High
- Release: v2
- Dependencies: E01 library foundation, alias model
- Description: Restore archived or folder-managed clips into active slots with conflict-safe prompts.
- Spec reference: SELECTION-CLIPBOARD-FEATURE-COMPLETE-SPEC.md
- Acceptance tests:
1. Archived clip restore to chosen slot succeeds with deterministic output.
2. Conflict prompts allow replace, merge, or cancel actions.
3. Restore actions preserve clip identity and linked folder metadata.

## E17 StarKey Everywhere Global Palette

### TKT-E17-001 SP-E17-A Global invoker and palette shell
- Priority: P0
- Risk: High
- Confidence: High
- Release: v1
- Dependencies: Core command bus, feedback layer
- Description: Implement global hotkey invoker and non-modal command palette shell that can open from browsers, Office apps, editors, and IDEs.
- Acceptance tests:
1. Palette hotkey opens from Edge, Chrome, Firefox, Outlook, Word, Notepad, and VS Code.
2. Palette focus is immediate and keyboard-only.
3. Close and reopen behavior is stable across rapid invocations.

### TKT-E17-002 SP-E17-B Command registry and fuzzy resolver
- Priority: P0
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: Command registry service
- Description: Build command metadata registry, fuzzy search, recent command weighting, and deterministic command resolution.
- Acceptance tests:
1. Search ranks top relevant commands by context and recency.
2. Deterministic exact command IDs bypass fuzzy ambiguity.
3. Resolver returns fallback suggestions when confidence is low.

### TKT-E17-003 SP-E17-C Context provider and capability envelope
- Priority: P0
- Risk: High
- Confidence: MediumHigh
- Release: v1
- Dependencies: Adapter SDK, app identity service
- Description: Capture focused app context, selection availability, element type, and adapter capability flags for command gating.
- Acceptance tests:
1. Context envelope reports app, selection state, and capabilities correctly in baseline apps.
2. Unsupported contexts surface guidance instead of hard failure.
3. Context updates after focus changes are reflected within one second.

### TKT-E17-004 SP-E17-D Action orchestrator and safety pipeline
- Priority: P0
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: Rollback token service
- Description: Implement preflight, dry-run, preview, apply, confirmation, and rollback stages for palette actions.
- Acceptance tests:
1. Mutating commands support preview before apply.
2. Destructive actions require explicit confirmation.
3. Rollback restores prior state for supported mutating actions.

### TKT-E17-005 SP-E17-E Selection and merge profile integration
- Priority: P0
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: E01 selection and merge engine
- Description: Integrate selection capture and clipboard merge profiles into palette workflows.
- Acceptance tests:
1. Palette commands can capture selection and merge outputs using configured profile separators.
2. Merge profiles meeting notes, email summary, research digest produce expected output format.
3. Source tagging option appends origin metadata when enabled.

### TKT-E17-006 SP-E17-F Baseline adapter bundle
- Priority: P1
- Risk: High
- Confidence: Medium
- Release: v2
- Dependencies: Adapter SDK, context provider
- Description: Implement and harden baseline adapters for Edge, Chrome, Firefox, Outlook, Word, Notepad, and VS Code.
- Acceptance tests:
1. Top 25 palette commands execute correctly in each baseline app where supported.
2. Adapter failures emit clear fallback guidance.
3. Smoke tests detect adapter regressions on update.

### TKT-E17-007 SP-E17-G Direct hotkey command plane
- Priority: P0
- Risk: High
- Confidence: MediumHigh
- Release: v1
- Dependencies: Global invoker, command registry, conflict scanner
- Description: Implement direct hotkey execution for top workflow commands so users can run actions without opening the palette.
- Spec reference: VIRTUALIZED-BROWSE-AND-HOTKEY-SPEC.md
- Starter pack reference: ENGINEERING-STARTER-PACK-VIRTUALIZED-HOTKEYS.md
- Acceptance tests:
1. Top 20 high-frequency commands execute from direct hotkeys in baseline apps.
2. Unsupported contexts emit deterministic fallback guidance and optional palette handoff.
3. Hotkey collisions are detected and surfaced with remap options before enabling profile changes.

### TKT-E17-008 SP-E17-H Hotkey discoverability and diagnostics
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: settings profile service, diagnostics output
- Description: Add searchable hotkey map, what-can-I-press prompt, and per-app conflict diagnostics.
- Spec reference: VIRTUALIZED-BROWSE-AND-HOTKEY-SPEC.md
- Starter pack reference: ENGINEERING-STARTER-PACK-VIRTUALIZED-HOTKEYS.md
- Acceptance tests:
1. Users can query available hotkeys by app and command family.
2. Diagnostic output identifies conflicting mappings with clear remediation steps.
3. Beginner profile includes guided hotkey hints while expert profile remains concise.

### TKT-E17-009 SP-E17-I Multi-press hotkey gesture engine
- Priority: P1
- Risk: Medium
- Confidence: MediumHigh
- Release: v1.1
- Dependencies: E17 global invoker, key routing, diagnostics
- Description: Add single, double, triple, and press-and-hold gesture resolution for shared key chords with deterministic timing behavior.
- Spec reference: VIRTUALIZED-BROWSE-AND-HOTKEY-SPEC.md
- Acceptance tests:
1. Single, double, and triple press bindings resolve correctly under timing jitter fixtures.
2. Multi-press behavior can be disabled globally per profile.
3. Multi-press collisions never block emergency stop.
4. Speech and braille feedback identify triggered gesture type.

### TKT-E17-010 SP-E17-J Baseline hotkey manager parity closure
- Priority: P1
- Risk: High
- Confidence: Medium
- Release: v2
- Dependencies: E17 direct hotkey plane, E17 diagnostics, profile service
- Description: Close remaining hotkey manager flexibility gaps versus Baseline including layered mappings, fallback ordering, macro-friendly chains, and importable preset packs.
- Analysis reference: SELECTION-CLIPBOARD-ADAPTATION-ANALYSIS.md
- Acceptance tests:
1. Keymap supports layered global, app, and mode-specific overrides with deterministic precedence.
2. Key binding presets can be exported and imported with integrity checks.
3. Fallback ordering is configurable and visible in diagnostics output.
4. Hotkey manager parity checklist is complete with no unresolved P1 gaps.

## E18 Magical 1.0 Differentiators

### TKT-E18-001 SP-E18-A Intent memory per app
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: E17 command resolver
- Description: Learn command ranking per app context while preserving explainability and user override.
- Acceptance tests:
1. Command ranking shifts by app usage profile.
2. Ranking explanation can be surfaced in palette help.
3. User can reset learned ranking by app.

### TKT-E18-002 SP-E18-B One-key command chains
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: E17 action orchestrator
- Description: Provide chain templates and custom chain builder for multi-step workflows.
- Acceptance tests:
1. Chain executes steps in order with per-step status.
2. Chain failures surface fallback and partial-success report.
3. Users can save and rerun custom chains.

### TKT-E18-003 SP-E18-C Confidence and fallback narration
- Priority: P1
- Risk: Low
- Confidence: High
- Release: v1
- Dependencies: E17 context provider
- Description: Add confidence scoring and immediate fallback narration for adaptive actions.
- Acceptance tests:
1. Adaptive commands report confidence.
2. Low confidence requires confirmation or suggestion mode.
3. Fallback options are always announced on failure.

### TKT-E18-004 SP-E18-D Universal quick capture inbox
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: E01 selection and clip engine, storage service
- Description: Capture snippets globally with source metadata and deferred routing.
- Acceptance tests:
1. Capture works from baseline app set.
2. Captured items include source context metadata.
3. Items can be routed to notes, clips, or drafts.

### TKT-E18-005 SP-E18-E Recover everything journal
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: rollback token service
- Description: Persist operation journal with reversible actions and readable summaries.
- Acceptance tests:
1. Mutating operations create journal entries.
2. Supported operations can rollback from journal.
3. Journal entries are searchable by app and action type.

### TKT-E18-006 SP-E18-F Ambient where-am-I layer
- Priority: P1
- Risk: Low
- Confidence: High
- Release: v1
- Dependencies: context provider
- Description: Instant context panel with app, element role, selection state, mode, and last action.
- Acceptance tests:
1. Context readout returns all required fields.

## E19 NVDA Upstream Compatibility and Readiness

### TKT-E19-001 SP-E19-A Platform and architecture baseline
- Priority: P0
- Risk: High
- Confidence: VeryHigh
- Release: v1
- Dependencies: none
- Description: Lock implementation assumptions to current NV Access support matrix and remove unsupported platform assumptions.
- Source reference: NVDA-UPSTREAM-IMPLEMENTATION-READINESS.md
- Acceptance tests:
1. Project docs and tickets no longer assume support for Windows 8.1.
2. Project docs and tickets no longer assume support for 32-bit Windows.
3. Project docs and tickets no longer assume support for Windows 10 ARM.
4. All baseline assumptions explicitly target 64-bit Windows 10 or Windows 11.

### TKT-E19-002 SP-E19-B Add-on API break readiness
- Priority: P0
- Risk: High
- Confidence: High
- Release: v1
- Dependencies: E17 adapter SDK planning
- Description: Prepare adapter and add-on implementation paths for 2026.1+ API break boundaries and manifest compatibility updates.
- Source reference: NVDA-UPSTREAM-IMPLEMENTATION-READINESS.md
- Acceptance tests:
1. A compatibility checklist exists for minimum and last-tested manifest fields.
2. API breaking changes and deprecations are mapped to internal work items.
3. Build and test gates include lint, unit, translation, and license checks aligned with NV Access guidance.
4. Upgrade guidance includes fallback behavior for incompatible add-ons.

### TKT-E19-003 SP-E19-C Security and disclosure alignment
- Priority: P0
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: incident response playbook
- Description: Align vulnerability reporting and triage workflow to NV Access security policy.
- Source reference: NVDA-UPSTREAM-IMPLEMENTATION-READINESS.md
- Acceptance tests:
1. Security workflow avoids public issue reporting for vulnerabilities.
2. Security reporting path includes GitHub Advisory and info@nvaccess.org options.
3. Severity labels P1, P2, and P3 are documented for internal triage.
4. Security handoff template includes reproduction steps, impact, and workaround fields.
2. Optional auto-read triggers after failed commands.
3. Speech and braille outputs are equivalent.

### TKT-E18-007 SP-E18-G Accessibility tuning profiles
- Priority: P1
- Risk: Low
- Confidence: High
- Release: v1
- Dependencies: settings profile service
- Description: Add beginner, balanced, and expert profile presets affecting all modules.
- Acceptance tests:
1. Profile change updates verbosity and confirmation behavior globally.
2. Profile persistence survives restart and export.
3. Users can clone and edit a profile safely.

### TKT-E18-008 SP-E18-H Cross-device workflow portability
- Priority: P2
- Risk: Medium
- Confidence: MediumHigh
- Release: v2
- Dependencies: sync and export services
- Description: Sync and package workflow artifacts such as command chains, templates, and settings.
- Acceptance tests:
1. Exported workflow pack imports on second device without corruption.
2. Sync conflict handling is explicit and non-destructive.
3. Profile and chain integrity checks pass post-import.

### TKT-E18-009 SP-E18-I Intelligent first-run missions
- Priority: P1
- Risk: Low
- Confidence: High
- Release: v1
- Dependencies: onboarding engine
- Description: Replace passive onboarding with practical missions and progress tracking.
- Acceptance tests:
1. New users receive mission sequence based on profile.
2. Completion state persists and unlocks next missions.
3. Mission success correlates with first-day workflow completion.

### TKT-E18-010 SP-E18-J Live integration health panel
- Priority: P1
- Risk: Medium
- Confidence: MediumHigh
- Release: v2
- Dependencies: adapter diagnostics service
- Description: Surface app adapter health, drift detection, and one-command diagnostics.
- Acceptance tests:
1. Panel reports status for baseline adapters.
2. Failing adapters include suggested remediation steps.
3. Health scans can be run on demand without blocking active workflow.

### TKT-E18-011 SP-E18-K Virtualized browse return mode
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: feedback bus, context provider, source anchor service
- Description: Present long or structurally complex command output in a virtualized browse surface with structural navigation and exact context return.
- Spec reference: VIRTUALIZED-BROWSE-AND-HOTKEY-SPEC.md
- Starter pack reference: ENGINEERING-STARTER-PACK-VIRTUALIZED-HOTKEYS.md
- Acceptance tests:
1. Users can navigate returned content by heading, action item, and citation block using deterministic keys.
2. Speech and braille outputs remain semantically equivalent in virtualized mode.
3. Exiting virtualized mode restores exact source focus and selection state.

## E13 Utility Mesh and Accessibility Ops

### TKT-E13-001 SP-E13-A Progress cues and tutorials
- Priority: P0
- Risk: Low
- Confidence: High
- Release: v1
- Dependencies: Earcon engine
- Description: Implement progress tones at increments with optional tutorial mode.
- Acceptance tests:
1. Increment tones fire at configured interval.
2. Tick feedback occurs between major increments.
3. Tutorial mode demonstrates all cue levels.

### TKT-E13-002 SP-E13-B Speech history in-place browse
- Priority: P0
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: Speech capture buffer
- Description: Implement in-context history browse, copy one item, copy range, and virtual-view inspection.
- Acceptance tests:
1. History capture does not shift app focus.
2. Left and right browse traverses captured history deterministically.
3. Single item and range copy produce expected clipboard contents.

### TKT-E13-003 SP-E13-C Notification rules import and restore
- Priority: P1
- Risk: Medium
- Confidence: Medium
- Release: v2
- Dependencies: Rules storage
- Description: Import notification rules, restore previous rules, and maintain safe rollback.
- Acceptance tests:
1. Import overwrites target rules only after explicit confirmation.
2. Restore reinstates previous set.
3. Failure states include actionable instructions.

### TKT-E13-004 SP-E13-D Audio splitter and card routing
- Priority: P1
- Risk: Medium
- Confidence: Medium
- Release: v2
- Dependencies: Audio device abstraction
- Description: Implement left-right speech split, restore balance, and sound-card cycle.
- Acceptance tests:
1. Speech and app audio route as selected.
2. Restore balance returns neutral stereo.
3. Card cycle reports active output reliably.

### TKT-E13-005 SP-E13-E Window bookmarks
- Priority: P1
- Risk: Low
- Confidence: High
- Release: v2
- Dependencies: Window manager helper
- Description: Bookmark up to 10 windows and return by slot.
- Acceptance tests:
1. Slot assign and recall works for running windows.
2. Slot names persist across restart.
3. Missing window state reports clear message.

### TKT-E13-006 SP-E13-F Symbol and alt-code assistant
- Priority: P1
- Risk: Low
- Confidence: High
- Release: v1
- Dependencies: Character map service
- Description: Provide searchable symbol insertion by code and description.
- Acceptance tests:
1. Enter by code inserts expected symbol.
2. Search list returns matching symbols.
3. Recent symbol memory recalls last code used.

### TKT-E13-007 SP-E13-G Computer report and diagnostics
- Priority: P2
- Risk: Low
- Confidence: High
- Release: v2
- Dependencies: System info collector
- Description: Generate machine report with export option.
- Acceptance tests:
1. Report includes core OS, memory, storage, and network fields.
2. Report opens in readable view.
3. Export writes to target path successfully.

## E15 Braille-First Command Surface

### TKT-E15-001 SP-E15-A Braille command grammar
- Priority: P0
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: Command parser
- Description: Implement braille command entry and abbreviation grammar.
- Acceptance tests:
1. Core command set executes from braille input.
2. Abbreviation file updates are loaded without restart.
3. Invalid commands return concise error guidance.

### TKT-E15-002 SP-E15-B Braille parity for core feedback
- Priority: P0
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: Feedback contract
- Description: Ensure speech events have equivalent braille output in core modules.
- Acceptance tests:
1. P0 actions emit both speech and braille feedback.
2. Braille output content matches speech meaning.

### TKT-E15-003 SP-E15-C Braille profile editor
- Priority: P1
- Risk: Low
- Confidence: High
- Release: v2
- Dependencies: Settings store
- Description: Edit and persist braille command mappings and preferences.
- Acceptance tests:
1. Mapping changes save and reload correctly.
2. Duplicate mapping conflicts are detected and resolved.

### TKT-E15-004 SP-E15-D Braille conflict fallback
- Priority: P1
- Risk: Medium
- Confidence: Medium
- Release: v2
- Dependencies: Conflict scanner
- Description: Detect command conflicts and suggest fallback mappings.
- Acceptance tests:
1. Conflict detection runs on profile save.
2. Fallback suggestion list is generated and selectable.

## E03 Markdown and HTML Authoring

### TKT-E03-001 SP-E03-A Markdown structure engine
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: Parser layer
- Description: Implement headings, emphasis, lists, quotes, links, tables, footnotes workflows.
- Acceptance tests:
1. All insertions produce valid markdown syntax.
2. Selected-text wrapping behaves consistently.
3. Table creation workflow closes correctly.

### TKT-E03-002 SP-E03-B Semantic HTML assistant
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: HTML transform layer
- Description: Generate semantic html structures and validate element intent.
- Acceptance tests:
1. Generated html uses semantic tags.
2. Validation catches heading order and link clarity issues.

### TKT-E03-003 SP-E03-C Export bridges
- Priority: P1
- Risk: Medium
- Confidence: Medium
- Release: v2
- Dependencies: Export adapters
- Description: Implement markdown-to-html and markdown-to-word export paths.
- Acceptance tests:
1. Exported html preserves document structure.
2. Exported word file preserves headings and lists.

### TKT-E03-004 SP-E03-D Accessibility lint and fix preview
- Priority: P1
- Risk: Low
- Confidence: High
- Release: v1
- Dependencies: Rule engine
- Description: Add accessibility checks and non-destructive fix previews.
- Acceptance tests:
1. Rule checks return location and remediation text.
2. Fix preview can be accepted or rejected.

## E04 Notes and Knowledge Workspace

### TKT-E04-001 SP-E04-A Quick note and dual mode
- Priority: P1
- Risk: Low
- Confidence: High
- Release: v1
- Dependencies: Storage service
- Description: Implement quick-note capture and simple versus advanced modes.
- Acceptance tests:
1. Quick note works from any supported app.
2. Mode switching does not delete hidden advanced data.

### TKT-E04-002 SP-E04-B Category hierarchy
- Priority: P1
- Risk: Medium
- Confidence: Medium
- Release: v2
- Dependencies: Tree model
- Description: Nested categories, move operations, and position memory.
- Acceptance tests:
1. Category open and closed states persist.
2. Move note and move category actions preserve integrity.

### TKT-E04-003 SP-E04-C Relationships and attachments
- Priority: P1
- Risk: Medium
- Confidence: Medium
- Release: v2
- Dependencies: File store
- Description: Related notes, web links, attachments, and advanced fields.
- Acceptance tests:
1. Related notes are bidirectional.
2. Attachment add and open workflows function reliably.
3. Advanced field values are searchable.

### TKT-E04-004 SP-E04-D Custom help and web text
- Priority: P1
- Risk: Medium
- Confidence: Medium
- Release: v2
- Dependencies: Context scope model
- Description: Implement global and app-specific help notes plus page and domain web notes.
- Acceptance tests:
1. Global notes are accessible from any context.
2. App-specific notes resolve by process name.
3. Page and domain scope can be toggled and persisted.

### TKT-E04-005 SP-E04-E Restore timeline
- Priority: P1
- Risk: Medium
- Confidence: Medium
- Release: v2
- Dependencies: Snapshot manager
- Description: Implement restore points and rollback for notes.
- Acceptance tests:
1. Mutating operations create restore points.
2. Restore operation returns note state correctly.

## E16 Joplin Interoperability

### TKT-E16-001 SP-E16-A Joplin import pipeline
- Priority: P1
- Risk: Medium
- Confidence: MediumHigh
- Release: v2
- Dependencies: ThoughtDock storage model, markdown parser
- Description: Import Joplin note exports into ThoughtDock with folder and tag mapping.
- Acceptance tests:
1. Imported notes preserve title and markdown body.
2. Imported tags are mapped and searchable.
3. Import summary reports successes, skips, and failures.

### TKT-E16-002 SP-E16-B Joplin export pipeline
- Priority: P1
- Risk: Medium
- Confidence: MediumHigh
- Release: v2
- Dependencies: Export service, attachment manager
- Description: Export ThoughtDock notes to Joplin-compatible package format.
- Acceptance tests:
1. Exported notes open in Joplin with expected structure.
2. Export process includes attachment references when present.
3. Export completion report is produced.

### TKT-E16-003 SP-E16-C Attachment and tag mapping hardening
- Priority: P2
- Risk: High
- Confidence: Medium
- Release: v3
- Dependencies: Attachment manager, mapping profile store
- Description: Handle duplicate attachments, path normalization, and tag collisions.
- Acceptance tests:
1. Duplicate attachments are de-duplicated or flagged.
2. Tag collisions are resolved predictably.
3. Mapping profile can be reused in future imports and exports.

### TKT-E16-004 SP-E16-D Linked workspace refresh and conflict handling
- Priority: P2
- Risk: High
- Confidence: Medium
- Release: v3
- Dependencies: Snapshot manager, conflict resolver
- Description: Add on-demand linked refresh with dry-run conflict report and confirm-to-apply workflow.
- Acceptance tests:
1. Dry-run identifies all potential conflicts without writing changes.
2. Apply step requires explicit confirmation.
3. Rollback restores pre-apply state successfully.

## E05 Shortcuts and File Navigation

### TKT-E05-001 SP-E05-A Shortcut creation workflows
- Priority: P1
- Risk: Low
- Confidence: High
- Release: v1
- Dependencies: Path resolver
- Description: Create shortcuts for file, folder, and web targets.
- Acceptance tests:
1. Shortcut save validates path or url.
2. Shortcut list displays type and target metadata.

### TKT-E05-002 SP-E05-B Categories and presets
- Priority: P1
- Risk: Low
- Confidence: High
- Release: v2
- Dependencies: Shortcut store
- Description: Category assignment, search filters, and preset slots.
- Acceptance tests:
1. Category and filter combinations return correct list.
2. Preset invocation opens assigned shortcut.

### TKT-E05-003 SP-E05-C Insert path in dialogs
- Priority: P1
- Risk: Medium
- Confidence: Medium
- Release: v2
- Dependencies: Dialog detector
- Description: Insert mapped folder path into open, save, and attach dialogs.
- Acceptance tests:
1. Path insertion works in tested dialog surfaces.
2. Failure state provides manual fallback instructions.

### TKT-E05-004 SP-E05-D Launcher curation
- Priority: P1
- Risk: Low
- Confidence: High
- Release: v1
- Dependencies: Launcher config
- Description: Curated launcher plus automatic add focused app.
- Acceptance tests:
1. Add and remove items works without config corruption.
2. Restore defaults reinstates base launcher entries.

### TKT-E05-005 SP-E05-E Drive mapping
- Priority: P2
- Risk: Medium
- Confidence: Medium
- Release: v2
- Dependencies: Drive mapping helper
- Description: Map folder to drive letter and remove mappings safely.
- Acceptance tests:
1. Mapping creates accessible drive alias.
2. Delete mapping removes alias only and preserves source folder.

## E06 Tagging and Table Capture

### TKT-E06-001 SP-E06-A File tagging session
- Priority: P1
- Risk: Low
- Confidence: High
- Release: v1
- Dependencies: Explorer adapter
- Description: Tag, untag, report tags, count tags, and cancel session.
- Acceptance tests:
1. Tagged files are audible and reportable.
2. Cancel clears tags without file mutation.

### TKT-E06-002 SP-E06-B Batch file actions
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: Explorer adapter
- Description: Copy, cut, delete, and playlist add from tag set.
- Acceptance tests:
1. Batch copy and cut move all tagged files.
2. Batch delete requires confirmation and reports result.

### TKT-E06-003 SP-E06-C Outlook message tagging
- Priority: P2
- Risk: Medium
- Confidence: Medium
- Release: v2
- Dependencies: Outlook adapter
- Description: Tag mail items then move, copy, or delete in batch.
- Acceptance tests:
1. Tagged message list is reviewable before action.
2. Move and copy operations target selected folder correctly.

### TKT-E06-004 SP-E06-D Table capture extractor
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v1
- Dependencies: Table parser
- Description: Capture table, row, column, cell, headers, buffer, and clipboard export.
- Acceptance tests:
1. Captured output respects selected separator.
2. Multiple captures append in expected order.

## E10 Database and Structured Records

### TKT-E10-001 SP-E10-A Database lifecycle
- Priority: P1
- Risk: Medium
- Confidence: MediumHigh
- Release: v2
- Dependencies: Data store
- Description: Create, select, and delete database containers.
- Acceptance tests:
1. Database create validates name and uniqueness.
2. Delete requires confirmation and supports restore point.

### TKT-E10-002 SP-E10-B Field model and validation
- Priority: P1
- Risk: Medium
- Confidence: MediumHigh
- Release: v2
- Dependencies: Schema engine
- Description: Field types, required flags, help text, validators, combo choices.
- Acceptance tests:
1. Field constraints are enforced on entry save.
2. Validation errors are clear and navigable.

### TKT-E10-003 SP-E10-C Entry workflows
- Priority: P1
- Risk: Medium
- Confidence: MediumHigh
- Release: v2
- Dependencies: Schema engine
- Description: Add, edit, delete, list columns, and read-only detail view.
- Acceptance tests:
1. Required field enforcement blocks incomplete save.
2. Entry list and detail view stay synchronized.

### TKT-E10-004 SP-E10-D Sort, search, export
- Priority: P1
- Risk: Low
- Confidence: MediumHigh
- Release: v2
- Dependencies: Query layer
- Description: Field-based search, sorting, export to csv and text.
- Acceptance tests:
1. Search scopes selected fields correctly.
2. Export files open and preserve expected columns.

### TKT-E10-005 SP-E10-E Jamal connector import and export
- Priority: P2
- Risk: High
- Confidence: Medium
- Release: v3
- Dependencies: Translator contract
- Description: Schema and data interchange bridge with Jamal tool formats.
- Acceptance tests:
1. Import maps all supported field types correctly.
2. Export round-trip preserves values and schema where possible.

### TKT-E10-006 SP-E10-F Jamal launch bridge
- Priority: P2
- Risk: Medium
- Confidence: Medium
- Release: v3
- Dependencies: External tool launcher
- Description: Open selected dataset in Jamal tool and return with context bookmark.
- Acceptance tests:
1. Launch action opens expected target dataset.
2. Return action restores previous context.

### TKT-E10-007 SP-E10-G Jamal sync mode
- Priority: P3
- Risk: High
- Confidence: Low
- Release: v4
- Dependencies: Merge engine
- Description: Optional bidirectional sync with conflict detection and resolution.
- Acceptance tests:
1. Sync dry-run reports all conflicts without writing changes.
2. Merge apply requires explicit confirmation and creates restore snapshot.

## E12 AI Assistant Platform

### TKT-E12-001 SP-E12-A Key setup and policy UX
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v2
- Dependencies: AI broker
- Description: API key setup, delete, billing status, and policy messaging.
- Acceptance tests:
1. Key save and delete functions reliably.
2. Billing status opens expected provider endpoint.

### TKT-E12-002 SP-E12-B Conversation state and sessions
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v2
- Dependencies: AI broker, storage
- Description: New prompt, clear conversation, save, load, view, delete sessions.
- Acceptance tests:
1. Context-aware mode preserves conversation continuity.
2. Clear operation resets context state fully.

### TKT-E12-003 SP-E12-C Tools library
- Priority: P1
- Risk: Medium
- Confidence: High
- Release: v2
- Dependencies: Prompt templates
- Description: Spell check, summarize, rewrite, extract actions, dictionary, thesaurus, accessibility rewrite and related tools.
- Acceptance tests:
1. Selected text or typed input routes correctly to tool pipeline.
2. Tool output supports copy and replace actions.

### TKT-E12-004 SP-E12-D Prompt library
- Priority: P1
- Risk: Low
- Confidence: High
- Release: v2
- Dependencies: Storage
- Description: Create, insert, and delete reusable prompts.
- Acceptance tests:
1. Prompt list is searchable and reusable.
2. Delete removes selected prompt only.

### TKT-E12-005 SP-E12-E Document Q and A
- Priority: P2
- Risk: Medium
- Confidence: MediumHigh
- Release: v3
- Dependencies: Upload service
- Description: Upload file, ask question, follow-up, copy answers, and close-session privacy behavior.
- Acceptance tests:
1. Supported file types upload and query successfully.
2. Follow-up questions preserve document context.

### TKT-E12-006 SP-E12-F Image and transcription flows
- Priority: P2
- Risk: Medium
- Confidence: MediumHigh
- Release: v3
- Dependencies: AI media endpoints
- Description: Image generation, transcription with optional speaker separation, translation transcription.
- Acceptance tests:
1. Generated image saves with requested filename.
2. Transcription returns text and supports clipboard copy.

## E07 Time, Diary, and Task Flows

### TKT-E07-001 SP-E07-A Time speak and insert
- Priority: P2
- Risk: Low
- Confidence: High
- Release: v2
- Dependencies: Time service
- Description: Speak time, speak time with seconds, insert time, insert date.
- Acceptance tests:
1. Time and date formats reflect locale settings.
2. Insert actions write at cursor position.

### TKT-E07-002 SP-E07-B Stopwatch and precision
- Priority: P2
- Risk: Low
- Confidence: High
- Release: v2
- Dependencies: Time service
- Description: Start, stop, clear, elapsed query, decimal precision settings, recurring cue.
- Acceptance tests:
1. Stopwatch state persists through stop and resume.
2. Precision setting changes spoken decimals correctly.

### TKT-E07-003 SP-E07-C Countdown and alarm
- Priority: P2
- Risk: Low
- Confidence: High
- Release: v2
- Dependencies: Time service
- Description: Minute timer, alarm time, remaining time query.
- Acceptance tests:
1. Countdown triggers at configured duration.
2. Alarm triggers at configured time and can be stopped.

### TKT-E07-004 SP-E07-D Time monitor and braille clock
- Priority: P2
- Risk: Medium
- Confidence: MediumHigh
- Release: v2
- Dependencies: Braille layer
- Description: Minute-boundary monitor and per-second braille output mode.
- Acceptance tests:
1. Monitor announces final second countdown and boundary event.
2. Braille updates each second until cancel key pressed.

### TKT-E07-005 SP-E07-E Diary and date utilities
- Priority: P2
- Risk: Medium
- Confidence: High
- Release: v2
- Dependencies: Storage
- Description: Create appointment, list month entries, date math, day lookups.
- Acceptance tests:
1. Date parsing supports configured locale format.
2. Day and interval calculations return expected values.

### TKT-E07-006 SP-E07-F Tasks and ICS bridge
- Priority: P2
- Risk: Medium
- Confidence: MediumHigh
- Release: v3
- Dependencies: Calendar bridge
- Description: Task records, filters, due-date bridge to calendar, ICS sync path.
- Acceptance tests:
1. Task filters by status, category, and priority.
2. ICS file updates and remains subscribable.

## E08 Communication and Social Adapters

### TKT-E08-001 SP-E08-A Contact store and insertions
- Priority: P1
- Risk: Low
- Confidence: High
- Release: v2
- Dependencies: Contact store
- Description: Create, search, and insert contact details in workflows.
- Acceptance tests:
1. Contact lookup and insertion completes from any supported context.
2. Copy-to-clipboard actions are available per contact field.

### TKT-E08-002 SP-E08-B Outlook and Thunderbird productivity
- Priority: P1
- Risk: Medium
- Confidence: Medium
- Release: v2
- Dependencies: Mail adapters
- Description: Sender extraction, attachment list operations, compose accelerators.
- Acceptance tests:
1. Attachment list actions are keyboard-only and stable.
2. Sender extraction copies expected fields.

### TKT-E08-003 SP-E08-C WhatsApp desktop and web
- Priority: P2
- Risk: High
- Confidence: Medium
- Release: v3
- Dependencies: WhatsApp adapters
- Description: Chat navigation, message actions, voice message controls, nickname layer.
- Acceptance tests:
1. Most recent message read keys return expected content.
2. Voice message controls record, pause, send, cancel correctly.

### TKT-E08-004 SP-E08-D X adapter
- Priority: P3
- Risk: High
- Confidence: Medium
- Release: v3
- Dependencies: X web adapter
- Description: Timeline read model, post actions, profile and conversation navigation.
- Acceptance tests:
1. Timeline navigation remains stable across refresh.
2. Core actions like reply and repost execute reliably.

### TKT-E08-005 SP-E08-E Social Orbit timelines
- Priority: P2
- Risk: High
- Confidence: Medium
- Release: v3
- Dependencies: Mastodon and Bluesky adapters
- Description: Multi-account timelines, post details, compose, filters, sounds, and braille flash.
- Acceptance tests:
1. New item announcements include account context.
2. Timeline filtering is applied as configured.

### TKT-E08-006 SP-E08-F Social nicknames and notifications
- Priority: P2
- Risk: Medium
- Confidence: Medium
- Release: v3
- Dependencies: Social adapters
- Description: Nickname replacement and notification control across social channels.
- Acceptance tests:
1. Nickname replacements appear in speech and braille outputs.
2. Notification preferences apply per timeline and account.

## E09 Search and Retrieval Layer

### TKT-E09-001 SP-E09-A Query routing and source adapters
- Priority: P2
- Risk: Medium
- Confidence: MediumHigh
- Release: v2
- Dependencies: Adapter registry
- Description: Route queries to configured sources and normalize results.
- Acceptance tests:
1. Source routing follows selected provider order.
2. Errors in one source do not crash aggregate results.

### TKT-E09-002 SP-E09-B Results memory and revisit
- Priority: P2
- Risk: Medium
- Confidence: Medium
- Release: v2
- Dependencies: Session memory
- Description: Remember current result list, visited status, and return position.
- Acceptance tests:
1. Reopen returns to prior result index.
2. Visited markers are accurate and resettable.

### TKT-E09-003 SP-E09-C Source parser resilience
- Priority: P2
- Risk: High
- Confidence: Medium
- Release: v3
- Dependencies: Parser framework
- Description: Implement resilient parsing and fallback for source format changes.
- Acceptance tests:
1. Parser failures degrade gracefully with explicit messaging.
2. Fallback parser path returns partial usable output.

### TKT-E09-004 SP-E09-D Retrieval summaries and action extraction
- Priority: P2
- Risk: Medium
- Confidence: MediumHigh
- Release: v3
- Dependencies: AI tools
- Description: Summarize retrieval outputs and extract action items.
- Acceptance tests:
1. Summary preserves key points and source references.
2. Action extraction produces concise task list.

## E11 Backup, Restore, and Portability

### TKT-E11-001 SP-E11-A Settings backup and restore
- Priority: P2
- Risk: Medium
- Confidence: High
- Release: v2
- Dependencies: Snapshot manager
- Description: Backup and restore suite settings and profile data.
- Acceptance tests:
1. Backup writes complete snapshot to target path.
2. Restore reinstates prior configuration successfully.

### TKT-E11-002 SP-E11-B Personal backup source and target manager
- Priority: P2
- Risk: Medium
- Confidence: MediumHigh
- Release: v2
- Dependencies: Path resolver
- Description: Configure backup target and source folders with validation.
- Acceptance tests:
1. Full path validation blocks invalid targets.
2. Duplicate source adds are prevented.

### TKT-E11-003 SP-E11-C Selected backup and restore sets
- Priority: P2
- Risk: Medium
- Confidence: MediumHigh
- Release: v2
- Dependencies: Backup engine
- Description: Backup and restore selected folders only.
- Acceptance tests:
1. Selected set processing includes only listed paths.
2. Completion reports include failures and skipped paths.

### TKT-E11-004 SP-E11-D Migration workflows
- Priority: P2
- Risk: Medium
- Confidence: Medium
- Release: v3
- Dependencies: Profile migration tool
- Description: Migrate profile data between versions safely.
- Acceptance tests:
1. Migration copies expected files and restarts cleanly.
2. Rollback path is available if migration fails.

## E14 Media and Entertainment Layer

### TKT-E14-001 SP-E14-A Unified media shell
- Priority: P3
- Risk: Medium
- Confidence: Medium
- Release: v4
- Dependencies: Media adapters
- Description: Build single shell for radio, podcasts, audio, playlists, and sound control.
- Acceptance tests:
1. Task switch works by keyboard and shortcut.
2. Current task state persists across reopen.

### TKT-E14-002 SP-E14-B Player controls and bookmarks
- Priority: P3
- Risk: Medium
- Confidence: Medium
- Release: v4
- Dependencies: Player core
- Description: Play, pause, stop, seek, speed, bookmarks, and sleep timer.
- Acceptance tests:
1. Global hotkeys control playback from other apps.
2. Bookmark add and jump work in long audio.

### TKT-E14-003 SP-E14-C Radio workflows
- Priority: P3
- Risk: High
- Confidence: Medium
- Release: v4
- Dependencies: Radio providers
- Description: Search, favorites, presets, recent station, and scheduled recording.
- Acceptance tests:
1. Search aggregates configured sources.
2. Scheduled recording executes at target time.

### TKT-E14-004 SP-E14-D Podcast workflows
- Priority: P3
- Risk: Medium
- Confidence: Medium
- Release: v4
- Dependencies: Feed adapters
- Description: Add feed, refresh episodes, show notes, chapter-aware playback, progress estimate.
- Acceptance tests:
1. New episode detection reports correctly.
2. Chapter navigation works when markers exist.

### TKT-E14-005 SP-E14-E Local audio and playlists
- Priority: P3
- Risk: Medium
- Confidence: Medium
- Release: v4
- Dependencies: File and player adapters
- Description: Create playlists, add files and folders, reorder tracks, edit tags.
- Acceptance tests:
1. Playlist operations persist and reload accurately.
2. Tag edits apply to supported file formats.

### TKT-E14-006 SP-E14-F Music recognition
- Priority: P3
- Risk: Medium
- Confidence: Medium
- Release: v4
- Dependencies: Recognition service
- Description: Recognize track from selected audio source and return linked results.
- Acceptance tests:
1. Recognition returns result details or explicit no-match state.
2. Result links are keyboard navigable.

### TKT-E14-007 SP-E14-G Game hub optional
- Priority: P3
- Risk: Medium
- Confidence: MediumLow
- Release: v4
- Dependencies: Optional game integrations
- Description: Integrate supported game launch and help pathways.
- Acceptance tests:
1. Game launch list is accessible and categorized.
2. Help links open reliably from game contexts.

## QA and Definition of Done Addendum

### Cross-ticket required checks
1. Keyboard-only pass.
2. Speech and braille parity pass for all user-visible outcomes.
3. Error path clarity pass.
4. Telemetry event emitted for action success and failure.

### Done definition for each ticket
1. Code merged with tests passing.
2. Accessibility acceptance complete.
3. Release notes updated with user-visible behavior.
4. No unresolved blocker defects.

## Risk Register Tags
Apply one primary risk tag per ticket:
- AdapterChurn
- DataLoss
- KeyConflict
- Performance
- Privacy
- AIReliability
- UXComplexity

## Final Execution Note
This file is the implementation backlog companion to the PRD. It is ready for import into a tracking system with minimal transformation.
