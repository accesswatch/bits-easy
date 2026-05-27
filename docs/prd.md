# Product Requirements Document

## Product Name
BITS-EASY Accessibility Suite for NVDA

## Date
May 21, 2026

## Author
Product and Accessibility Strategy Draft

## 1. Executive Summary
This PRD defines a full roadmap to deliver a delightful, magical, and accessibility-first NVDA feature suite that achieves practical parity with the Baseline experience and exceeds it in selected workflows through AI assistance, adaptive interaction design, and stronger cross-workflow continuity.

The top priority is selection-first productivity: cuts, clips, selection transforms, and cross-app capture. Media features including radio, podcasts, and RSS are intentionally prioritized near the bottom.

## 2. Vision
Build the most delightful productivity layer for blind users on Windows by combining:
- Fast keyboard-first interaction.
- Reliable contextual automation.
- High-confidence accessibility behavior.
- AI-assisted writing, structuring, and navigation.
- Graceful fallbacks when third-party apps change.

### 2.1 Magical North Star
The intended experience is not novelty. It is trusted flow.

1. The next action is always obvious.
2. Important operations are always reversible or recoverable.
3. Power scales with user confidence, from beginner to expert.
4. Stable users never get surprise behavior changes.
5. Accessibility quality is part of delight, not a separate checkbox.

## 3. Product Goals
1. Reduce time-to-task for high-frequency workflows by 40 percent in 6 months.
2. Achieve Full or Partial parity coverage for all major Baseline modules.
3. Deliver a clearly superior experience in selection, clips, markdown/html authoring, and AI-assisted composition.
4. Maintain accessibility as a first-class requirement in every feature and release gate.

## 4. Non-Goals
1. Recreate every legacy behavior exactly when a better user experience is available.
2. Guarantee perfect automation in all third-party web apps.
3. Replace specialized tools for full professional audio or video production.

## 5. Accessibility Requirements (Mandatory)
1. All interactions must be fully keyboard operable.
2. Speech and braille output must be concise, deterministic, and user-configurable.
3. Every critical action must have clear confirmation and recovery path.
4. Error states must provide actionable next steps.
5. New features must pass accessibility acceptance tests before release.
6. No feature can degrade baseline NVDA navigation behavior.

## 6. Naming Architecture
Suite name: BITS-EASY Accessibility Suite

Core modules:
- SnapSpan: Selection engine.
- PocketClips: Multi-slot clip system.
- MergeBoard: Intelligent clipboard and append behaviors.
- StarKey: Intent launcher and command palette.
- Waymarks: Position anchors and bookmarks.
- Trailback: Context return and session continuity.
- RelayDesk: Communication accelerators.
- Beacon Search: Unified search adapters.
- ThoughtDock: Structured note system.
- Notebook Bridge: Joplin interoperability layer.
- SignalNotes: Sticky contextual annotations.
- Day Compass: Diary and date intelligence.
- Time Lantern: Clock, timer, and monitor features.
- ScorePulse: Sports monitoring.
- Skywave: Radio tools.
- StoryStream: Podcast workflows.
- FeedWeave: RSS workflows.
- BITS-EASY Markdown: Markdown assistant.
- BITS-EASY HTML: HTML assistant.
- BITS-EASY Assist: AI transformations and remediation.

## 7. Ranked Integration Points (Highest to Lowest Priority)
This table ranks integration points by expected user impact and implementation confidence.

| Rank | Integration Point | Module Focus | Impact | Confidence | Notes |
|---|---|---|---|---|---|
| 1 | Selection and Clip Core | SnapSpan, PocketClips, MergeBoard | Very High | Very High | Must launch first |
| 2 | Cross-App Clipboard Intelligence | MergeBoard | Very High | Very High | Core daily workflow |
| 3 | Global Magical Command Palette | StarKey Everywhere | Very High | High | Must work from any app at any time |
| 4 | Position Anchors and Return | Waymarks, Trailback | High | High | Reduces disorientation |
| 5 | Writing and Communication | RelayDesk | High | Medium High | Email and messaging focus |
| 6 | Markdown and HTML Authoring | BITS-EASY Markdown, BITS-EASY HTML | High | High | Major differentiation |
| 7 | Database Builder and Structured Records | DataForge | Medium High | Medium High | New strategic capability |
| 8 | File and Path Power Workflows | PathPilot | Medium High | High | Daily operations accelerator |
| 9 | Search and Retrieval Layer | Beacon Search | Medium High | Medium High | Adapter complexity |
| 10 | Notes and Sticky Context | ThoughtDock, SignalNotes, Notebook Bridge | Medium High | High | Strong personal productivity |
| 11 | Calendar, Tasks, and Time Utility | Day Compass, Task Orbit, Time Lantern | Medium | High | Predictable local logic |
| 12 | Social App Deep Adapters | Social Orbit | Medium | Medium | UI churn risk |
| 13 | Sports Monitoring | ScorePulse | Medium | Medium High | External data dependency |
| 14 | RSS Workflows | FeedWeave | Lower | Medium High | Intentionally lower priority |
| 15 | Podcasts | StoryStream | Lower | Medium | Intentionally lower priority |
| 16 | Radio | Skywave | Lower | Medium | Intentionally lower priority |

## 8. Baseline to NVDA Parity Matrix (Full Mapping by Module)
This matrix maps Baseline module-level capabilities to planned NVDA equivalents and status.

| Baseline Capability Group | Proposed Equivalent | Status | Confidence | Priority |
|---|---|---|---|---|
| BaselineSelect | SnapSpan | Full Planned | Very High | P0 |
| BaselineClips | PocketClips | Full Planned | Very High | P0 |
| Clipboard Append Features | MergeBoard | Full Planned | Very High | P0 |
| BaselinePoints | Waymarks | Full Planned | High | P1 |
| BaselineAlerts | Signal triggers in Trailback and Beacon Search | Partial Planned | Medium High | P1 |
| BaselineStickyNotes | SignalNotes | Full Planned | High | P1 |
| BaselineNotes | ThoughtDock | Full Planned | High | P1 |
| BaselineVirtualNotes | ThoughtDock Side Panel Mode | Full Planned | High | P1 |
| External notes interoperability | Notebook Bridge for Joplin | Partial Planned | Medium High | P2 |
| BaselineConnect | Contact Orbit inside RelayDesk | Partial Planned | Medium High | P1 |
| BaselineWord Utilities | BITS-EASY Compose tools | Partial Planned | High | P1 |
| BaselineSearch | Beacon Search | Partial Planned | Medium High | P1 |
| Email enhancements (Outlook and Thunderbird) | RelayDesk adapters | Partial Planned | Medium | P1 |
| Internet enhancements | Trailback and Beacon Search browser adapters | Partial Planned | Medium | P1 |
| BaselineClock | Time Lantern | Full Planned | High | P2 |
| BaselineDiary | Day Compass | Full Planned | High | P2 |
| Markdown assistant | BITS-EASY Markdown | Full Planned and Expanded | High | P1 |
| HTML assistant | BITS-EASY HTML | Full Planned and Expanded | High | P1 |
| Progress indicator sounds | Adaptive telemetry earcons | Partial Planned | Medium High | P2 |
| Emoji helper | Character and symbol insert assistant | Partial Planned | High | P3 |
| Sports and Games | ScorePulse | Partial Planned | Medium High | P2 |
| Radio | Skywave | Partial Planned | Medium | P3 |
| Podcasts | StoryStream | Partial Planned | Medium | P3 |
| RSS reader flows | FeedWeave | Partial Planned | Medium High | P3 |
| Spotify and media control adapters | Media adapter layer | Partial Planned | Medium | P3 |
| Old Reader and feed services | FeedWeave adapters | Partial Planned | Medium | P3 |
| Twitter or X adapters | Social adapter layer | Partial Planned | Medium | P3 |
| WhatsApp desktop and web adapters | RelayDesk social adapters | Partial Planned | Medium | P3 |
| Mastodon address workflows | Contact Orbit social aliases | Partial Planned | Medium High | P2 |

### 8.1 Coverage Status Answer
Not every Baseline feature is mapped at full feature-level parity yet.

Current coverage snapshot:
1. Module-level parity mapping: Broad coverage is present across core Baseline areas.
2. Feature-level parity mapping: Partial coverage only, with several modules still grouped rather than enumerated feature-by-feature.
3. Full certainty areas: Selection, clips, clipboard intelligence, markdown and html transformation paths.
4. Lower certainty areas: Deep third-party adapters, social timeline edge cases, and some media-provider-specific workflows.

Planned remediation:
1. Add a complete feature-level checklist for each module with status labels Full, Partial, Missing.
2. Track each feature to release targets v1, v2, or v3.
3. Add confidence and dependency tags per feature.

### 8.2 Baseline 11.5 Addendum Mapping (Summer 2026)
The following upcoming Baseline 11.5 capabilities are now added to this PRD roadmap.

| Baseline 11.5 Capability | Proposed Equivalent | Status | Confidence | Priority |
|---|---|---|---|---|
| Baseline Media Centre unified model | Media Nexus shell with Skywave, StoryStream, local audio, playlists, and sound control | Partial Planned | Medium | P3 |
| Baseline Media Player global and braille-aware controls | Media Core player layer with speech and braille parity | Partial Planned | Medium | P3 |
| Scheduled radio recording and recovery | Skywave Recorder with resilient reconnection | Partial Planned | Medium | P3 |
| Podcast chapter and progress intelligence | StoryStream chapter-aware playback and progress estimates | Partial Planned | Medium | P3 |
| Advanced Notes and Simple Notes dual mode | ThoughtDock dual-mode notes model | Full Planned | High | P1 |
| Notes restore points and backups | ThoughtDock recovery engine | Full Planned | High | P1 |
| Audio notes with attachment model | ThoughtDock voice note subsystem | Full Planned | High | P1 |
| Redesigned Shortcut Catalog with categories and presets | PocketClips and PathPilot shortcut catalog | Full Planned | High | P0-P1 |
| Baseline Database Manager | DataForge database builder | Full Planned | Medium High | P1 |
| Talk to ChatGPT voice loop | BITS-EASY Assist voice chat mode | Partial Planned | Medium High | P2 |
| Transcription tool with diarization options | BITS-EASY Assist transcribe mode | Full Planned | High | P2 |
| Markdown converter to Word and HTML | BITS-EASY Markdown export bridge | Full Planned | High | P1 |
| Baseline File Manager | PathPilot file operations shell | Partial Planned | High | P1 |
| Start Menu and Main Menu curation | LaunchPad and QuickLane launch curation | Full Planned | High | P1 |
| BaselineDiary plus tasks and ICS sync | Day Compass and Task Orbit with ICS bridge | Partial Planned | High | P2 |
| Baseline Spell Check clipboard workflow | BITS-EASY Spell clipboard pass | Full Planned | High | P2 |
| BaselineSocial Mastodon and Bluesky client | Social Orbit multi-account timeline client | Partial Planned | Medium | P2 |
| Social sound packs and braille flash messaging | Social Orbit feedback channels | Partial Planned | Medium | P2 |
| Interoperability with mainstream note apps | Notebook Bridge with Joplin | Partial Planned | Medium High | P2 |

## 8.3 Database Magic Track (Including Jamal Tool Integration)
Database capability is promoted to a strategic integration point because it creates high-leverage structured workflows for accessibility users.

### DataForge Scope
1. Build accessible small-database creation and record management in Python.
2. Support field types: text, multi-line text, link, integer, decimal, date, combo, checkbox.
3. Support validation, required fields, help text, sort, filter, and export.

### Jamal Database Tool Bridge
Objective: use Jamal's Windows database tool as an accelerator and interoperability path.

Bridge plan:
1. Connector mode: import and export schemas and records using a stable interchange format such as JSON and CSV.
2. Launch mode: open selected datasets in Jamal's tool from DataForge for advanced operations.
3. Sync mode: optional bidirectional sync with conflict detection.

Integration requirements:
1. Data model translator between DataForge fields and Jamal tool structures.
2. Safe write operations with automatic snapshot before merge.
3. Accessibility verification on all bridge dialogs and conflict prompts.

Risks:
1. Schema mismatch between tools.
2. Version drift if Jamal tool file formats change.
3. Data-loss risk on merge without safeguards.

Mitigations:
1. Versioned translator contracts.
2. Pre-merge validation and dry-run preview.
3. Automatic restore points and reversible commits.

## 8.4 Notes Interoperability Track (Including Joplin)
Joplin integration should be included because many users already maintain large markdown-based notebooks and need safe coexistence or migration.

### Notebook Bridge Scope
1. Import Joplin exports into ThoughtDock.
2. Export ThoughtDock notes into Joplin-compatible formats.
3. Preserve note body, title, tags, and attachments where feasible.

### Integration Modes
1. Import and export mode for explicit transfer workflows.
2. Linked workspace mode for refresh-on-demand interoperability.
3. Optional sync-assist mode with conflict preview and user confirmation.

### Risks
1. Metadata mismatch for linked notes and advanced fields.
2. Attachment duplication and path divergence.
3. Conflict scenarios when both tools modify the same note.

### Mitigations
1. Mapping profile versions with regression tests.
2. Pre-sync dry-run and conflict report.
3. Snapshot before apply and one-command rollback.

## 8.5 Source-Inspected Add-on Patterns and Product Directives
This section captures implementation patterns verified by direct source inspection of overlapping NVDA add-ons and translates them into actionable BITS-EASY directives.

Inspected repositories:
1. placeMarkers
2. snippetsForNVDA
3. Enhanced-Clipboard-Reading
4. clipboard-content-editor
5. ClipHistory
6. outlookExtended
7. wordNav

### 8.5.1 Verified implementation patterns

#### PlaceMarkers (primary reference for bookmark navigation)
1. Uses native NVDA text surfaces first: selection, caret, first, and all text info positions.
2. Differentiates UIA browse documents from non-UIA paths and uses separate movement logic.
3. Stores bookmark data per effective document identity, not as one global list.
4. Persists position bookmarks as serialized structures and temporary bookmarks as lightweight text files.
5. Couples bookmarks with optional note metadata and exposes deterministic next and previous bookmark navigation.
6. Uses explicit backup and restore of marker folders, including migration paths from prior layouts.

#### snippetsForNVDA
1. Captures selected text through treeInterceptor selection when available, then falls back to focus object selection.
2. Uses fixed numeric memory slots for low-latency clipboard workflows.
3. Uses single-press speak and double-press paste behavior for slot recall.
4. Persists snippets to disk as JSON under user config path.

#### Enhanced-Clipboard-Reading
1. Extends existing NVDA clipboard command paths rather than replacing user mental models.
2. Uses configurable thresholding to switch from spoken output to browseable message output.
3. Adds a dedicated character-count script to improve predictability before heavy clipboard operations.

#### clipboard-content-editor
1. Uses a command-layer interaction model with fast single-key actions after activation.
2. Includes backup and restore controls for clipboard safety.
3. Maintains clipboard history and append-mode behavior with configurable limits.
4. Uses periodic polling to detect clipboard changes.

#### ClipHistory
1. Uses Windows clipboard listener events instead of polling for capture updates.
2. Applies throttling and suppression windows to avoid self-trigger loops during internal paste operations.
3. Stores rich clipboard records, including text plus HTML payload support.
4. Persists large history with pinning and debounced atomic save behavior.

#### outlookExtended
1. Builds by extending the NVDA built-in Outlook app module rather than replacing the stack.
2. Reuses native COM selection pathways for message state reporting.
3. Adds scoped behavior on top of native objects and scripts for Outlook-specific workflows.

#### wordNav
1. Provides high-power navigation value but relies heavily on regex segmentation and broad surface adaptation.
2. Demonstrates that advanced heuristics can be useful but increase long-term maintenance and compatibility risk.

### 8.5.2 Product directives for BITS-EASY
1. Native-first contract: always attempt native text and selection providers before custom normalization.
2. Surface identity model: key persisted anchors and captures by deterministic surface identity, not only process name.
3. Clipboard architecture: adopt event-driven listener capture with throttling and explicit self-write suppression.
4. Data model: preserve both plain text and rich clipboard payloads when available.
5. Safety model: require backup and rollback pathways for mutating clipboard and selection transforms.
6. Interaction model: support both direct hotkeys and optional command-layer execution for expert throughput.
7. Persistence model: separate fast transient state from durable state and use atomic writes for durable records.
8. Outlook strategy: layer behavior on top of NVDA native Outlook support and avoid bypassing native object paths.

### 8.5.3 Anti-pattern guardrails
1. Do not depend on private NVDA internals as stable contracts.
2. Do not lead with app-specific heuristic slicing when native range and selection providers already exist.
3. Do not rely on polling-only clipboard capture where event listeners are available.
4. Do not collapse all app contexts into one global bookmark namespace.

### 8.5.4 Release implications
1. P0 and P1 selection and clipboard features must pass native-first conformance checks before release.
2. Any heuristic fallback introduced for a specific surface must include explicit justification, telemetry, and removal criteria.
3. Competitive parity claims for bookmarks and clip workflows must reference these source-verified patterns.

### 8.5.5 Second-wave source additions (older and niche add-ons)
Additional inspected repositories:
1. clipContentsDesigner
2. EasyTableCopy
3. showSelectionWhenBrailleTetheredToReview
4. invisinote
5. xPlorer

#### clipContentsDesigner
1. Uses native selection capture first via `makeTextInfo(POSITION_SELECTION)` and browse mode tree interceptor handoff.
2. Uses confirmation gates before mutating clipboard state and supports browseable clipboard preview.
3. Also contains a private-internals dependency on `_selectThenCopyRange` from review-position objects.

BITS-EASY decision:
1. Keep native-first selection acquisition and confirmation-gated clipboard mutations.
2. Reject private-internals dependencies as non-contract behavior.

#### EasyTableCopy
1. Implements explicit multi-engine copy paths: native selection-and-copy first, then manual reconstruction fallback, then desktop list and explorer-specific handling.
2. Maintains explicit marked row and column state with deterministic clear and copy actions.
3. Preserves dual clipboard payloads where possible, including HTML plus plain text.

BITS-EASY decision:
1. Keep explicit engine ordering with native first and bounded fallback layers.
2. Keep deterministic marked selection state machine and explicit clear actions.
3. Keep dual payload export where the source provides structure.

#### showSelectionWhenBrailleTetheredToReview
1. Anchors selection rendering to native `POSITION_SELECTION` and review-position collapse semantics.
2. Handles no-selection and COM failure paths explicitly.
3. Integrates with braille review regions by updating selection windows only when cursor-follow contracts are satisfied.

BITS-EASY decision:
1. Keep explicit no-selection and COM-error handling contracts for selection surfaces.
2. Keep separate review and selection state paths for braille-sensitive workflows.

#### invisinote
1. Uses an explicit marker model for local text buffer selection with user-set start and end, and repeat-to-copy behavior.
2. Keeps copy behavior deterministic by operating on internal note buffers instead of external app surfaces.

BITS-EASY decision:
1. Use this model only for internal virtual surfaces and authored buffer workflows.
2. Do not generalize this local marker approach as a replacement for external native app selections.

#### xPlorer
1. Adds explorer-specific clipboard actions for selected names and file content, with explicit content filtering.
2. Implements create-folder-and-rename assist using clipboard text sanitation and staged fallback input injection paths.
3. Uses delayed action scheduling for Explorer transitions and UI timing stability.

BITS-EASY decision:
1. Keep strict sanitation and suitability checks before any clipboard-assisted rename or injection path.
2. Keep fallback injection paths as last resort and scope them to explicit user intent and known-safe contexts.

### 8.5.6 Extended guardrails from second-wave analysis
1. Do not promote local-buffer marker workflows into global cross-app selection logic.
2. Do not invoke input-injection fallback paths unless native selection and command paths have failed and user intent is explicit.
3. Require sanitization and length limits before clipboard-assisted naming workflows.
4. Preserve a deterministic engine order for complex captures: native path, structured fallback, then specialized surface adapters.

### 8.5.7 Virtualized surface parity matrix (selection and interactive controls)
Objective:
Define expected behavior for virtualized text and interactive surfaces so parity is measurable and testable.

| Surface Class | Typical APIs | Expected BITS-EASY Path | Fallback Path | Risk Notes |
|---|---|---|---|---|
| Browser virtual buffer document | treeInterceptor + `makeTextInfo(POSITION_SELECTION or POSITION_CARET)` | Use treeInterceptor as primary text provider when not pass-through | Focus object text info if interceptor unavailable | Drift between review and focus positions |
| UIA browse document variant | UIA text ranges and bookmarks | Prefer native bookmark-derived caret and range offsets | Recompute from visible text only when offsets unavailable | UIA range endpoint mismatch across versions |
| Link and button elements in virtual docs | Role and accessible name | Treat interactive label as selectable text when native selection is empty | Name and description fallback with low confidence | False positive capture when control name is generic |
| Virtualized list and tree items | List item and tree item roles under dynamic containers | Capture via role-aware traversal and active row context | Surface-specific adapter path for inaccessible child trees | Dynamic object identity can invalidate stale anchors |
| Outlook message list rows | UIA grid row and list row variants | Explicitly unsupported for stable text-range operations | User-guided fallback actions only | High churn and unstable row text anchors |
| Reading pane and compose documents | Native selection text in document or editable roles | Native selection text first | Deterministic range from visible buffer | Selection anchoring differs by Outlook build |

Implementation directives:
1. Runtime adapters must classify interactive roles and support explicit low-confidence label capture when range selection is absent.
2. Snapshot extraction must prefer interceptor-backed providers before focus-object providers.
3. Anchor restore must reject cross-control drift and clamp only within the current surface text length.
4. Any unsupported virtualized surface must return explicit reason codes, never silent no-op behavior.

Validation gates:
1. Unit coverage must include interceptor-first selection extraction, interactive-label fallback, and message-list unsupported behavior.
2. Regression tests must verify no private NVDA internals are required for offsets.
3. Release checklists must include at least one browser virtual-buffer link scenario and one list item scenario.

### 8.5.8 Third-wave source learnings from newly pulled content
Additional inspected repositories:
1. ClipHistory
2. Enhanced-Clipboard-Reading
3. xPlorer
4. snippetsForNVDA
5. outlookExtended
6. invisinote

#### ClipHistory
1. Uses native Windows clipboard listener events (`WM_CLIPBOARDUPDATE`) with bounded throttling and suppression windows.
2. Avoids self-trigger feedback loops by temporarily disabling listener processing during internal clipboard writes.
3. Uses batched delayed actions for tap-multiplexed gestures (single action versus double action).

BITS-EASY decision:
1. Promote event-listener-first clipboard capture where available and keep polling only as degraded fallback.
2. Standardize self-loop suppression windows for all clipboard-mutating commands.
3. Keep bounded tap-multiplex windows for overloaded gestures and expose timeout settings.

#### Enhanced-Clipboard-Reading
1. Uses repeat-count behavior for one command (speak, spell, browse) with explicit length thresholding.
2. Switches to browseable output when content exceeds configured size.

BITS-EASY decision:
1. Extend selection and clipboard readback commands with repeat-count tiers and deterministic escalation.
2. Add a configurable browse-threshold contract for long content in all readback surfaces.

#### xPlorer
1. Uses chunked batch operations with `core.callLater` for large explorer selections to prevent UI starvation.
2. Uses deterministic progress messaging for long-running selection transforms.

BITS-EASY decision:
1. Add chunked mutation execution for large clip and selection transforms.
2. Add progress and completion telemetry announcements for large-batch operations.

#### snippetsForNVDA
1. Uses deterministic fixed slot gestures with repeat-to-paste behavior and optional persistence.
2. Uses role-aware selection capture via treeInterceptor-first then focus fallback.

BITS-EASY decision:
1. Keep fixed slot semantics for zero-latency recall workflows and preserve repeat behavior parity.
2. Keep role-aware selection capture ordering as a hard contract.

#### outlookExtended
1. Uses robust multi-layout detection for message header extraction based on ordered control identifiers.
2. Provides explicit user-visible fallback behavior when unsupported column navigation states occur.

BITS-EASY decision:
1. Keep explicit layout-signature mapping for Outlook reading and compose surfaces.
2. Require user-visible unsupported-state messaging rather than silent fallback.

#### invisinote
1. Uses local virtual-surface editing with deterministic file type and path scoping.
2. Uses local vendored markdown stack and delayed window relocation to avoid focus churn.

BITS-EASY decision:
1. Use scoped virtual-surface editing for local notes and authoring workflows only.
2. Add focus-stability timing contracts for virtual render windows.

### 8.5.9 New implementation candidates from third-wave analysis
1. Selection and clipboard readback command family should expose repeat-tier payload fields (`repeatTier`, `renderMode`, `lengthPolicy`).
2. Clipboard capture engine should expose listener mode telemetry (`event-listener`, `polling-fallback`, `suppressed-write-window`).
3. Long-running selection transforms should expose batch telemetry (`batchSize`, `batchIndex`, `batchTotal`, `progressPercent`).
4. Outlook adapters should expose layout signature IDs and unsupported-state reason codes for reproducible diagnostics.
5. Virtual-surface note and render flows should expose focus-stability diagnostics (`focusRestoreAttempts`, `focusRestoreLatencyMs`).

## 9. Feature-Level Parity Detail and Implementation Paths

### 9.1 P0: Selection-First Experience
Feature groups:
- Begin and end selection markers.
- Quick select actions on marked range.
- Speak start and end context.
- Move back to start marker.
- Copy, cut, paste transforms.
- Multi-clip slots 1 to 12.
- Clip protect and delete.
- Clipboard append mode and divider strategy.

Implementation path:
1. Build low-level selection state engine in Python with app context adapters.
2. Build deterministic key routing and conflict manager.
3. Add clip-slot persistence in local store with lightweight encryption option.
4. Add speech and braille response templates.
5. Ship with profile-based defaults: beginner, balanced, expert.

Acceptance criteria:
1. Works in plain text editors, browser virtual buffers, and common document surfaces.
2. No silent failures on selection state loss.
3. Every action provides user feedback with reversible path where applicable.

### 9.1B P0 to P1: Reading Units, Structured Segments, and Table Export
Objective:
Replace vague block-based selection language with explicit reading units and structured segment output that users can control.

Reading unit model:
1. Default unit name is Reading Unit, not block.
2. Built-in units: character, word, line, sentence, paragraph, heading section, list item, table row, table cell, code block, quote block, page, and smart semantic chunk.
3. Users can set a per-app default unit and override unit for one command invocation.
4. Selection commands must announce active unit before capture and after unit changes.

Structured segment behavior:
1. Segment boundaries must be deterministic for structural units such as heading section, list item, table row, and table cell.
2. Smart semantic chunk mode must expose confidence and permit stepwise next or previous chunk traversal.
3. Every segment capture must include source metadata: app, control role, window title, timestamp, and capture confidence.

Table capture and export formats:
1. Table captures must preserve row and column ordering.
2. Export formats: TSV, CSV, Markdown table, HTML table, and JSON rows.
3. Clipboard copy supports format negotiation with a default profile per workflow.
4. Where table structure is uncertain, the system must provide a preview and require explicit user confirmation before overwrite or merge.

Acceptance criteria:
1. User can switch reading units without leaving the current workflow.
2. Table capture exports round-trip correctly to spreadsheet workflows for TSV and CSV.
3. Structured exports include headers when detected and indicate when headers are inferred.

### 9.1C Selection Surface Parity Matrix and Acceptance Gates
Objective:
Define parity as a measurable contract with explicit surface states and CI-enforced thresholds.

The following table defines expected selection parity state for initial v1 surfaces.

| App Surface | Expected State | Notes |
|---|---|---|
| Edge | Native range capture | Primary browser parity target |
| Chrome | Native range capture | Primary browser parity target |
| Firefox | Native range capture | Primary browser parity target |
| Word | Native range capture | Word document-focused target |
| Notepad | Native range capture | Baseline editor target |
| VS Code | Native range capture | Developer editor target |
| Outlook | Fallback-only capture | Message list and transient surfaces require deterministic fallback |

State definitions:
1. Native range capture: direct range extraction with confidence at or above 0.9 and no fallback flag.
2. Normalized partial capture: adapter-normalized extraction with confidence below 0.9 and no fallback flag.
3. Fallback-only capture: unsupported native range, captured using deterministic fallback flow with explicit fallback flag.

Acceptance gates:
1. Native plus normalized coverage must pass on at least 6 of 7 matrix surfaces in the v1 matrix.
2. Fallback-only surfaces must be at most 1 of 7 in the v1 matrix.
3. Any fallback-only result must include explicit guidance and confidence narration.
4. Secure and password-protected dialog surfaces are policy-blocked and excluded from parity targets.

Executable test contract:
1. Matrix and gates are enforced by CI tests in tests/test_release_parity_matrix.py.
2. Any adapter change that shifts a surface state must update both this matrix and the executable gate tests.

### 9.1A P0: StarKey Everywhere, Global Magical Command Palette
Objective:
Create a VS Code-like command palette that can be invoked globally from any focused application and execute context-aware actions for selection, copy, clips, merge, transforms, and navigation.

Supported target surfaces:
1. Browsers: Microsoft Edge, Google Chrome, Firefox.
2. Office and communication: Outlook, Microsoft Word.
3. Editors and shells: Notepad, VS Code and similar text environments.
4. Additional adapters can be added through the adapter SDK.

User experience requirements:
1. Global hotkey always available, with collision-safe alternatives.
2. Palette opens as a lightweight non-modal layer with immediate focus.
3. Fuzzy command search with ranking by context, recency, and confidence.
4. Natural language command input and direct command IDs.
5. Action preview and impact statement before execution for sensitive actions.
6. Keyboard-only operation with full speech and braille parity.

Core command families:
1. Selection commands: start marker, end marker, select sentence, select paragraph, select between headings, select current table row.
2. Clipboard commands: copy to clip slot, paste from slot, merge clipboard with separator profile, speak clipboard summary.
3. Transform commands: rewrite selected text, simplify language, convert to markdown list, extract action items.
4. Context commands: where am I, return to previous context, jump to last command target.
5. Workflow commands: save selection as text template, create note from selection, send selection to email draft.

Implementation architecture:
1. Global Invoker Service: registers low-level hotkey handlers and opens palette host independent of foreground app tech stack.
2. Context Provider Layer: collects app identity, focused element type, selection availability, document mode, and adapter capabilities.
3. Command Registry and Resolver: stores command metadata and resolves input using deterministic matching first and AI intent assist second.
4. Action Orchestrator: executes preflight, dry-run, preview, apply, and rollback stages.
5. Feedback Bus: emits concise speech and braille output with confidence and next-step hints.

Selection and clipboard merge integration logic:
1. Preflight selection check: use native selection when available; otherwise offer quick capture strategies for current app.
2. Merge profile engine: support profiles such as meeting notes, email summary, research extraction, and code snippet collection.
3. Citation-aware merge: optional source tags for web and email captures.
4. Safe apply flow: preview output length and destination, and require confirmation for replacement operations.

Adapter strategies by app class:
1. Browsers: accessibility tree and virtual buffer signals first, focused-element extraction fallback.
2. Outlook and Word: UIA role and document signals first, guarded keyboard orchestration fallback.
3. Notepad and VS Code: native selection and clipboard integration first, line-based capture fallback.

Text-pattern support statement:
1. Version 1 does not claim full parity with every Windows text pattern surface.
2. Version 1 scope is capability-based: use native selection providers first, then adapter-specific normalization, then deterministic fallback capture.
3. Parity reporting must classify each app and surface into one of three states: native range capture, normalized partial capture, fallback-only capture.

Dialog and transient surface capture:
1. Add a dedicated quick action: Capture dialog text.
2. Capture order: focused control text, dialog subtree text, speech-history fallback, clipboard fallback.
3. Captured dialog text must include dialog metadata: title, role, app, and confidence.
4. For secure and password dialogs, capture must be blocked and replaced with a clear explanation.
5. Dialog capture output routes to quick capture inbox, clipboard, or selected clip slot.

Performance and reliability targets:
1. Palette open under 150 milliseconds.
2. Command search response under 50 milliseconds for local index.
3. Deterministic action feedback under one second.
4. Adapter failure guidance under one second.

Safety and recovery:
1. Destructive actions require confirmation.
2. Mutating actions produce rollback token.
3. Low-confidence actions downgrade to suggestion mode or require confirmation.
4. Action logs are stored for diagnostics and trust.

Acceptance criteria:
1. Palette invocation works in baseline apps listed above.
2. Top 25 commands execute with deterministic output and accessibility parity.
3. Selection and merge workflows pass end-to-end tests in browser, Outlook, Word, Notepad, and VS Code.
4. Fallback guidance is always provided for unsupported contexts.

### 9.2 P1: Navigation Memory and Context Return
Feature groups:
- Per-document and per-page anchors.
- Mode options: item, domain, default-global.
- List anchors and jump.
- Return to previous location after opening links.

Implementation path:
1. Unified Waymarks datastore keyed by source and mode.
2. Browser and document adapters with fallback locator strategies.
3. Trailback history stack with confidence scoring.

Acceptance criteria:
1. Anchor retrieval success above 90 percent in supported contexts.
2. Transparent reporting when content drift prevents exact return.

### 9.3 P1: BITS-EASY Markdown and BITS-EASY HTML
Feature groups:
- Structural insertion commands.
- Smart list and table builders.
- Link and mailto helpers.
- Footnote and table-of-contents builders.
- Conversion and preview pipelines.
- Accessibility lint and one-command fixes.

Implementation path:
1. Parser-based transformations for markdown and html.
2. Context-sensitive command grammar in StarKey.
3. Accessibility rule engine with explainable fixes.
4. Preview adapters for browser and editor.

Magical upgrades beyond baseline parity:
1. Intent phrases such as convert this paragraph into comparison table.
2. Auto-structure from selected text blocks.
3. AI rewrite modes: concise, friendly, formal, plain language.
4. AI quality check: readability, link clarity, heading logic.

Acceptance criteria:
1. Deterministic output for all syntax operations.
2. No destructive rewrite without preview and confirm.
3. Accessibility checks integrated into authoring flow.

### 9.4 P1: Communication Accelerator
Feature groups:
- Contact insertion and quick compose.
- Attachment list extraction and quick save.
- Sender extraction and summarize thread.
- Message action shortcuts.

Implementation path:
1. RelayDesk core with adapter interfaces for Outlook and Thunderbird.
2. Contact Orbit store with labels and aliases.
3. Summarization and response assist using local or cloud AI provider.

Acceptance criteria:
1. Compose and recipient insertion from any app context.
2. Attachment list access must be keyboard-first and stable.

### 9.5 P1 to P2: Unified Search and Information Retrieval
Feature groups:
- Meta-search adapters.
- Recent searches and revisit.
- Return to results list at previous position.

Implementation path:
1. Beacon Search plugin architecture per source.
2. Resilient parser interfaces for list-first output.
3. Source health monitor and graceful fallback.

Acceptance criteria:
1. Always provide a list-first summary path.
2. Always preserve result context when opening and returning.

### 9.6 P2: Time, Diary, and Personal Workflow Utilities
Feature groups:
- Appointments and date math.
- Timers, alarms, stopwatch, and monitors.

Implementation path:
1. Local scheduler services.
2. Unified temporal grammar parser.
3. Optional cloud backup for user data.

Acceptance criteria:
1. Works offline for core features.
2. Timezone and locale behavior is explicit.

### 9.7 P2: Sports Intelligence
Feature groups:
- Live score checks.
- Event listing and filtering.
- Monitoring and reinstate sessions.

Implementation path:
1. ScorePulse provider abstraction with quality scoring.
2. Session management and timer controls.
3. Alert channels with interrupt policy controls.

Acceptance criteria:
1. Handles service latency with clear user messaging.
2. No mixed-mode monitoring if not supported.

### 9.8 P3: Media and Feed Layer (Intentionally Lower Priority)
Feature groups:
- Skywave radio.
- StoryStream podcasts.
- FeedWeave RSS management.

Implementation path:
1. Build after core productivity and authoring are stable.
2. Keep provider adapters modular and replaceable.
3. Favor synchronization-ready feed architecture.

Acceptance criteria:
1. Must not delay P0 and P1 goals.
2. Must pass same accessibility quality gates.

## 10. AI Capability Plan

### AI Scope
1. Intent resolution for StarKey.
2. Text transformation and formatting suggestions.
3. Accessibility remediation suggestions with explanations.
4. Context-preserving summaries for messages and search results.

### AI Safety and Reliability Rules
1. Human confirmation for destructive edits.
2. Explainability text for all AI-generated modifications.
3. Confidence score output with low-confidence fallback.
4. Deterministic non-AI command path always available.

### AI Interaction Modes
1. Suggest mode: no changes, recommendations only.
2. Preview mode: staged changes, user confirms.
3. Apply mode: executes confirmed changes and logs actions.

## 11. Technical Architecture
1. Core Python service with plugin adapters.
2. Event bus for command dispatch and feedback.
3. Adapter SDK for app integrations.
4. Local datastore for clips, anchors, settings, and history.
5. Accessibility output layer for speech and braille.
6. AI broker abstraction for local and cloud models.
7. Global invoker subsystem for StarKey Everywhere.
8. Context provider framework for app-aware command ranking.
9. Action orchestrator with dry-run, preview, apply, and rollback stages.
10. Virtualized return renderer with structural navigation and deterministic focus return.
11. Direct hotkey command plane with per-profile mapping, conflict detection, and safe fallback to palette.

## 12. Integration Strategy
1. Capability flags by adapter: Full, Partial, Experimental.
2. Versioned contracts for adapter responses.
3. Continuous smoke tests against adapter targets.
4. Fast update channel for breaking third-party UI changes.
5. Command parity matrix so high-frequency actions are available both in palette and direct hotkey paths.
6. Reserved keyspace policy with app-specific conflict scanner and runtime collision alerts.

## 13. Risks and Mitigations
This table lists known risks and mitigations.

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Third-party UI changes break adapters | High | High | Capability flags, fast patch channel, fallback workflows |
| Over-automation causes trust loss | High | Medium | Human-confirm checkpoints, explainable actions |
| Keybinding conflicts across apps | Medium High | High | Key routing manager, profile customization, conflict scanner |
| AI output inconsistency | Medium High | Medium | Deterministic mode fallback, confidence thresholds |
| Accessibility regressions during rapid development | High | Medium | Accessibility test gates, release blockers |
| Performance overhead from background monitors | Medium | Medium | Adaptive polling, user-configurable intervals |
| Scope creep from broad parity effort | High | High | Priority lock by phase, strict release criteria |
| Data privacy concerns for cloud AI | High | Medium | Local processing option, opt-in cloud policy |
| Virtualized reading surface drifts from source context | Medium High | Medium | Stable source anchors, deterministic focus return, parity tests for speech and braille |
| Direct hotkey collisions reduce reliability | Medium High | High | Reserved keyspace policy, conflict scanner, per-profile remap and diagnostics |

## 14. Release Plan

### Phase 1 (0 to 12 weeks)
- SnapSpan, PocketClips, MergeBoard.
- StarKey basic command launcher.
- Waymarks and Trailback baseline.
- Accessibility test framework and telemetry.

### Phase 2 (13 to 24 weeks)
- BITS-EASY Markdown and BITS-EASY HTML.
- RelayDesk adapters for Outlook and Thunderbird.
- Beacon Search initial adapters.
- ThoughtDock and SignalNotes.
- DataForge initial release with schema, records, and export.
- PathPilot initial release for copy, move, zip, tagging, and path copy.
- Notebook Bridge initial Joplin import and export.

### Phase 3 (25 to 40 weeks)
- Day Compass and Time Lantern.
- Task Orbit with due-date to diary bridge.
- ScorePulse initial providers.
- Social Orbit initial client and adapter expansions.
- BITS-EASY Assist voice chat and transcription enhancements.
- Notebook Bridge linked workspace mode with conflict-safe refresh.

### Phase 4 (41 weeks onward)
- FeedWeave, StoryStream, Skywave.
- Advanced AI orchestration and personalization.
- DataForge and Jamal bridge sync mode.

## 15. Success Metrics
1. Median task completion time for selection and clip workflows.
2. Return-to-context success rate.
3. Adapter stability rate over release windows.
4. Accessibility defect escape rate.
5. User satisfaction and delight scores.
6. AI suggestion acceptance and correction rates.
7. Virtualized return readability success rate for long-form results.
8. Direct hotkey completion rate for top workflow actions without palette invocation.

## 15A. Magical 1.0 Differentiators
This section defines the explicit capabilities that make version 1.0 feel magical rather than merely complete.

### D1 Intent Memory Per App
1. Remember command usage patterns per application and rank commands accordingly.
2. Keep ranking explainable and reversible.

### D2 One-Key Command Chains
1. Support composable command chains for common multi-step workflows.
2. Include starter chain templates for research, email triage, and note capture.
3. Allow each chain or step action to be bound to direct hotkeys where safe.

### D3 Confidence and Fallback Narration
1. Every adaptive action reports confidence level.
2. Any low-confidence action must provide immediate fallback options.

### D4 Universal Quick Capture Inbox
1. Capture snippets from any app with source metadata.
2. Route captured items later to notes, clipboard packs, or drafts.

### D5 Recover Everything Journal
1. Maintain an operation journal with rollback where feasible.
2. Include plain-language action descriptions and timestamps.

### D6 Ambient Where-Am-I Layer
1. Provide instant context readout: app, control role, selection state, active mode, and last action.
2. Offer optional auto-read on failed commands.

### D7 Accessibility Tuning Profiles
1. Provide beginner, balanced, and expert profiles that affect speech density, braille verbosity, confirmations, and earcons.
2. Apply profile settings globally across modules.

### D8 Cross-Device Workflow Portability
1. Sync not only content, but workflow preferences, command chains, and templates.
2. Allow export and import of workflow packs.

### D9 Intelligent First-Run Missions
1. Replace passive onboarding with practical missions that deliver immediate value.
2. Track mission completion and recommend next mission.

### D10 Live Integration Health Panel
1. Show adapter status by app with last verification time and health state.
2. Provide one-command diagnostics and guided remediation.

### D11 Virtualized Browse Return Surface
1. Present command output in a stable virtualized surface when source surfaces are noisy, dynamic, or structurally poor.
2. Provide structural jumps by heading, action item, citation, and reading unit segment with deterministic key behavior.
3. Guarantee exact focus return to source context when exiting virtualized view.

### D15 Reading Unit Intelligence and Structured Exports
1. Let users define preferred reading unit per app and per task profile.
2. Keep segment boundaries explainable and previewable before mutating actions.
3. Provide one-step export of captured tables and segment sets as TSV, CSV, Markdown table, HTML table, or JSON rows.
4. Preserve source metadata for downstream note, database, and audit workflows.

### D16 Dialog and Error Text Rescue
1. Add capture pathways for transient dialogs, toasts, and message surfaces that do not expose stable standard selection.
2. Provide explicit confidence narration when capture comes from fallback layers.
3. Support quick copy of captured dialog text into clipboard, quick capture inbox, and clip slots.
4. Exclude secure and password-protected surfaces by policy.

### D12 Direct Hotkey Flight Paths
1. Support direct hotkey execution for top-frequency commands without opening the palette.
2. Provide app-aware fallback when a direct hotkey is blocked or unsupported.
3. Include discoverability, remapping, and conflict diagnostics for all hotkey paths.

### D13 PocketClips Studio
1. Provide a keyboard-first browser to view all clipboard slots in one structured surface.
2. Show slot provenance, age, protection state, and quick actions in speech and braille parity.
3. Support manual slot manipulation including compare, reorder, split, merge, and batch operations.
4. Preserve confidence through safe prompts, rollback where feasible, and no silent failures.

### D14 PocketClips Library and Slot Aliases
1. Provide historical clip storage with folder and category organization for long-lived workflows.
2. Support both move and link operations when organizing clips into folders.
3. Allow users to retain recognizable slot number aliases after moving clips to folders.
4. Support restoring archived clips back into active slots with conflict-safe prompts.
5. Keep clip identity stable across linked folders, aliases, and active slot views.

## 16. Open Questions
1. Which app adapters must be guaranteed in v1 contracts.
2. Preferred default AI mode for beginner users.
3. Data retention policy for command and telemetry logs.
4. Enterprise deployment requirements and offline constraints.
5. Should EASY key sequence timing use one global timeout or per-mode timeout profiles.
6. Which Tier 2 direct hotkeys are promoted into v1.1.
7. Which Windows surfaces are committed to native text-pattern parity versus fallback-only in v1.1.
8. Should dialog capture include optional OCR for image-only message surfaces in v2.

## 17. Final Recommendation
Build selection and clip intelligence first, then command and context memory, then markdown and html magic with accessibility-first AI assistance. This sequence delivers the largest user impact with the highest implementation confidence while preserving room for richer media and feed features later without compromising accessibility quality.

## 17A. Implementation Spec References
1. Virtualized browse and direct hotkey behavior contract: BITS-EASY-COMPLETE-GUIDE.md and FULL-GUIDED-KEYSTROKE-TEST-PLAN.md.
2. This spec is normative for D11 and D12 delivery acceptance.
3. Engineering command IDs, JSON schemas, and CI matrix are tracked in config and tests, with release validation in RELEASE-HARDENING-CHECKLIST.md.

## 18. Complete Chapter Inventory and Mapping Status
This section is a comprehensive inventory based on the Baseline help index and related update material reviewed for this PRD cycle. Each chapter or feature family is mapped and assigned a parity intent and magical differentiation path.

Legend:
1. Full Planned: feature is explicitly designed with implementation path.
2. Partial Planned: feature is mapped but requires additional adapter or specification depth.
3. Pending Detail: feature family is mapped but needs feature-level decomposition in backlog.

| Baseline Chapter or Feature Family | Proposed Equivalent | Status | Magical Differentiation Path |
|---|---|---|---|
| Introduction and onboarding | LaunchPad onboarding | Full Planned | Adaptive onboarding that shifts from guided to expert mode based on user cadence |
| Installation | Setup Wizard Plus | Full Planned | Self-healing installer checks for common accessibility setup gaps and offers one-key fixes |
| What Next | First Run Coach | Full Planned | Daily quick wins panel with progressive learning prompts |
| Computer Adjustments | System Tune Assistant | Full Planned | One command environment audit with spoken remediation scripts |
| Getting Started Baseline Basic | Guided Basics Mode | Full Planned | Task cards with instant repeat and confidence score |
| Getting Started Baseline Advanced | Guided Advanced Mode | Full Planned | Intent trainer that teaches shortcuts from real usage patterns |
| Working With Sounds | Earcon Studio | Full Planned | Sound personalization with context-aware density controls |
| Baseline Word | Compose Studio | Full Planned | Writing flow mode with context hints and fewer interruptions |
| Working With Email Basic | RelayDesk Basic | Full Planned | Smart recipient and attachment intent suggestions |
| Working With Email Basic and Advanced | RelayDesk Pro | Full Planned | Message triage lane and one-key action bundles |
| BaselineConnect | Contact Orbit | Partial Planned | Relationship graph between contacts, channels, and recent actions |
| Working With the Internet Basic | Web Compass Basic | Full Planned | Guided page landmarks with fewer keystrokes |
| Working With the Internet Advanced | Web Compass Pro | Partial Planned | Predictive return-to-context and robust page drift recovery |
| BaselineSearch | Beacon Search | Partial Planned | Unified retrieval lens with source confidence and resume point memory |
| Baseline Sports and Games | ScorePulse | Partial Planned | Smart monitor profiles by sport urgency and preferred verbosity |
| BaselineDiary | Day Compass | Full Planned | Timeline lens that merges appointments, tasks, and reminders |
| BaselineSelect | SnapSpan | Full Planned | Intent-select actions that infer copy, summarize, or transform pathways |
| BaselineTexts | TextVault | Full Planned | Semantic templates and variable slots for reusable text blocks |
| BaselineClips | PocketClips | Full Planned | Auto-labeled clips from context and source tags |
| Shortcut Catalog | PathPilot shortcuts | Full Planned | Dynamic collections by workflow and current app context |
| BaselineNotes | ThoughtDock | Full Planned | Knowledge-link suggestions between notes and tasks |
| Baseline Virtual Notes | ThoughtDock Side Panel | Full Planned | Persistent side-reading with exact resume line memory |
| BaselineAlerts | SignalNotes alerts | Partial Planned | Trigger confidence and intelligent false-positive suppression |
| BaselinePoints | Waymarks | Full Planned | Multi-mode anchors with reliability scoring and fallback targeting |
| BaselineStickyNotes | SignalNotes sticky annotations | Full Planned | Contextual reminders with optional quiet mode and replay |
| Mastodon Address Book | Contact Orbit social aliases | Partial Planned | Auto-expanding social handles with profile-aware suggestions |
| X and Twitter support | Social Orbit X adapter | Partial Planned | Read model that prioritizes user-defined content fields |
| WhatsApp Classic | Social Orbit WhatsApp desktop adapter | Partial Planned | Conversation accelerators and reliable message action overlays |
| WhatsApp Web | Social Orbit WhatsApp web adapter | Partial Planned | Resilient web adapter with fallback path and quick action hints |
| Markdown | BITS-EASY Markdown | Full Planned | Intent-to-structure transformations with accessibility checks |
| Emoji | Symbol Palette | Full Planned | Contextual symbol assistant with category and usage hints |
| BaselineClock | Time Lantern | Full Planned | Braille synchronized precision clock and monitor presets |
| BaselineTags | TagFlow | Full Planned | Cross-folder and cross-mailbox tag sessions with safe batch actions |
| Progress Indicators | ProgressSense | Full Planned | Predictive completion feedback and stall detection guidance |
| Baseline Audio | AudioCore | Partial Planned | Unified playback control with context-preserving resume |
| Baseline Radio | Skywave | Partial Planned | Ranked lower priority with smart station and record automation |
| VLC Media Player and Winamp integration | Media Adapter Layer | Partial Planned | Capability-aware player abstraction with fallback commands |
| Spotify support | Music Orbit | Partial Planned | Fast transport and queue controls through stable command surface |
| The Old Reader | FeedWeave old reader adapter | Partial Planned | Digest summaries with importance scoring |
| The HTML Assistant | BITS-EASY HTML | Full Planned | Semantic HTML generation and validation by intent |
| Baseline Custom Help | Help Weave | Full Planned | Smart local playbook with searchable procedures and linkbacks |
| Baseline Custom Web Text | Web Notes Weave | Full Planned | Domain or page memory overlays with quick compare |
| WordWeb integration | Lexicon Bridge | Full Planned | Inline definitions and replacement suggestions in authoring flow |
| TinySpell integration | BITS-EASY Spell | Full Planned | Unified spelling layer with app-independent interaction model |
| Outlook Calendar integration | Calendar Bridge | Partial Planned | Day-view optimized appointment navigation with compact summaries |
| Baseline Games | Game Hub | Pending Detail | Separate optional module with progression and accessibility coaching |
| Studio Recorder support | Audio Edit Bridge | Partial Planned | Editing assist overlays with precision verbal checkpoints |
| ALT Codes tool | Symbol Codes Assistant | Full Planned | Fast searchable symbol insertion with memory of recent inserts |
| Mapping Drives to Folders | DriveMap Wizard | Full Planned | Path-to-drive automation with safety and conflict checks |
| Baseline Start Menu | LaunchPad | Full Planned | Context-aware app launcher with dynamic pinning |
| Reviewing Speech History | EchoTrail | Full Planned | In-place speech history skim with selective copy workflows |
| Table Capture | TableWeave | Full Planned | Multi-table extraction with structured output modes |
| Additional Utilities | Utility Mesh | Partial Planned | Consolidated utility command center with profile-based defaults |
| Backup and Restore Manager | RestoreShield | Full Planned | Snapshot, rollback, and selective restore with guided safety steps |
| BrailleEas | BrailleFlow | Full Planned | Braille command grammar with personal abbreviation intelligence |
| ChatGPT Setup | BITS-EASY Assist setup | Full Planned | Guided AI setup with privacy and billing clarity |
| Getting to Know ChatGPT | BITS-EASY Assist conversation | Full Planned | Context controls with explicit conversation state visibility |
| ChatGPT Tools | BITS-EASY Assist tools | Full Planned | Rewriter, summarizer, faq, action extraction, and conversion library |
| Baseline 11.5 Media Centre | Media Nexus | Partial Planned | Unified radio, podcast, audio, playlist, and sound control shell |
| Baseline 11.5 Notes redesign | ThoughtDock Advanced and Simple | Full Planned | Dual-mode notes with restore points and relationship graph |
| Baseline 11.5 Cuts redesign | PathPilot advanced cuts | Full Planned | Category, filter, and preset engine with strong import support |
| Baseline 11.5 Database | DataForge | Full Planned | Accessible schema designer and records grid with validation and export |
| Baseline 11.5 File Manager | PathPilot file shell | Partial Planned | Fast file operations with tagged sets and safe bulk workflows |
| Baseline 11.5 Social client | Social Orbit | Partial Planned | Timeline-focused, field-configurable social workspace with braille flash |

## 19. Feature Completeness Statement
Answer to the direct question, "is every Baseline feature mapped":
1. Every feature family and indexed chapter category reviewed in this cycle is now mapped to an equivalent track in this PRD.
2. Not every micro-feature is yet decomposed into a one-row engineering backlog item.
3. The remaining work is decomposition depth, not missing family coverage.

Decomposition actions required:
1. Expand each Partial Planned and Pending Detail row into atomic stories with acceptance criteria.
2. Assign owner, target release, and dependency flag per atomic feature.
3. Validate each row with a prototype confidence test.

## 20. Magical Framework by Design
To guarantee delight and not mere parity, every mapped feature must implement this framework.

### 20.1 Delight Principles
1. Zero confusion first action: user always knows the first useful key.
2. Progressive disclosure: beginner simple, expert fast, same command surface.
3. Recovery confidence: reversible actions and clear rollback.
4. Speech and braille parity: no information asymmetry.
5. Predictive assistance: suggest next action without hijacking control.

### 20.2 Magical Building Blocks
1. Intent Lens: infer likely action from context and selected text.
2. Context Memory: preserve place across app switches, dialogs, and sessions.
3. Smart Transform: convert selected content into target structure.
4. Confidence Meter: announce reliability for adaptive behaviors.
5. Gentle Automation: require confirmation for destructive actions.

### 20.3 Accessibility Guardrails
1. Keyboard-only complete path for every feature.
2. Explicit mode announcements for stateful tools.
3. Deterministic fallback path when adapter confidence is low.
4. No silent failures.
5. Performance budget for response feedback under one second for local actions.

### 20.4 AI-Enhanced Magic Requirements
1. AI suggestions are optional and never block deterministic workflows.
2. AI outputs include editable preview before apply.
3. AI workflows include a plain language rewrite option by default.
4. AI actions must emit concise rationale so users understand changes.
5. Privacy mode must allow local-first operation where possible.

## 21. Atomic Feature Checklist (Execution-Grade)
This section converts mapped feature families into implementable atomic scopes. Status values are:
1. Planned: defined and ready for backlog decomposition.
2. Scoped: acceptance criteria and interfaces defined.
3. Build-Ready: all dependencies resolved.

### 21.1 P0 Selection and Clip System
| ID | Atomic Feature | Parity Goal | Status | Release | Confidence | Magical Uplift |
|---|---|---|---|---|---|---|
| P0-SEL-01 | Mark selection start | Full | Build-Ready | v1 | Very High | Spoken and braille start marker with quick undo |
| P0-SEL-02 | Mark selection end | Full | Build-Ready | v1 | Very High | Range summary and instant action suggestions |
| P0-SEL-03 | Speak start and end context | Full | Build-Ready | v1 | Very High | Context snippets plus estimated size |
| P0-SEL-04 | Jump back to selection start | Full | Build-Ready | v1 | Very High | Optional breadcrumb history |
| P0-SEL-05 | Reading unit switcher | Full | Scoped | v1 | High | Fast unit announce and reversible unit toggle |
| P0-SEL-06 | Deterministic segment capture by unit | Full | Scoped | v1 | High | Segment preview with source metadata |
| P0-SEL-07 | Dialog and error text rescue capture | Full | Planned | v1.1 | Medium High | Multi-layer fallback capture with confidence narration |
| P0-CLIP-01 | Multi-slot clip copy 1 to 12 | Full | Build-Ready | v1 | Very High | Auto-label clips by source |
| P0-CLIP-02 | Multi-slot clip paste 1 to 12 | Full | Build-Ready | v1 | Very High | Preview clip metadata before paste |
| P0-CLIP-03 | Clip protect and unprotect | Full | Scoped | v1 | High | Lock icon and speech guardrails |
| P0-CLIP-04 | Clip delete per slot | Full | Build-Ready | v1 | Very High | One-step restore for last delete |
| P0-CLIP-05 | Clip edit before save | Full | Scoped | v1 | High | Inline cleanup suggestions |
| P0-MERGE-01 | Clipboard append mode toggle | Full | Build-Ready | v1 | Very High | Audible mode confirmation |
| P0-MERGE-02 | Divider mode line, space, paragraph | Full | Build-Ready | v1 | Very High | Divider profile presets |
| P0-MERGE-03 | Custom separator text | Full | Scoped | v1 | High | Separator templates by task |
| P0-MERGE-04 | Clear clipboard on paste option | Full | Scoped | v1 | High | Smart safety prompt on destructive clear |
| P0-MERGE-05 | Speak clipboard content fast | Full | Build-Ready | v1 | Very High | Summarized preview for large clipboard text |
| P0-TABLE-01 | Capture table to TSV or CSV | Full | Scoped | v1 | High | Header detection and confidence report |
| P0-TABLE-02 | Capture table to Markdown or HTML table | Full | Planned | v1.1 | Medium High | Structure-preserving export with preview |
| P0-TABLE-03 | Capture table to JSON rows | Full | Planned | v1.1 | Medium High | Database-ready schema-aware output |

### 21.1A Clipboard and Selection Decomposition Closure
Clipboard and selection feature decomposition is now complete at execution depth for parity tracking.

Reference:
1. This PRD sections 9.1 through 9.1C and section 21.1 serve as the canonical selection and clipboard spec.

Closure intent:
1. Every selection and clipboard feature has explicit behavior definition.
2. Every feature has mapped acceptance and fallback expectations.
3. Remaining work in this domain is implementation progression from scoped to build-ready states.

### 21.2 P1 Navigation, Anchors, and Search
| ID | Atomic Feature | Parity Goal | Status | Release | Confidence | Magical Uplift |
|---|---|---|---|---|---|---|
| P1-WAY-01 | Set anchor by number 1 to 10 | Full | Scoped | v1 | High | Confidence score on retrieval |
| P1-WAY-02 | Retrieve anchor by number | Full | Scoped | v1 | High | Optional auto-read mode |
| P1-WAY-03 | Domain mode anchors for web | Full | Planned | v2 | Medium High | Intelligent path normalization |
| P1-WAY-04 | Global default anchors | Full | Planned | v2 | Medium High | Cross-document phrase targeting |
| P1-WAY-05 | Delete one or all anchors | Full | Scoped | v1 | High | Recycle bin for recently removed anchors |
| P1-TRAIL-01 | Return to previous location after link open | Full | Planned | v2 | Medium | Smart fallback when DOM changes |
| P1-TRAIL-02 | Automatic relocation on browser back | Full | Planned | v2 | Medium | Multi-strategy location restore |
| P1-SEARCH-01 | Unified results list model | Partial | Planned | v2 | Medium High | Resume index position on return |
| P1-SEARCH-02 | Visited result cueing | Partial | Planned | v2 | Medium High | Optional quiet visited mode |

### 21.3 P1 Writing, Markdown, and HTML
| ID | Atomic Feature | Parity Goal | Status | Release | Confidence | Magical Uplift |
|---|---|---|---|---|---|---|
| P1-MD-01 | Heading insertion levels 1 to 6 | Full | Build-Ready | v1 | High | Voice prompt for heading hierarchy health |
| P1-MD-02 | Bold and italic toggles | Full | Build-Ready | v1 | High | Selection-aware wrapping with validation |
| P1-MD-03 | Block quote insertion | Full | Scoped | v1 | High | Optional source citation prompt |
| P1-MD-04 | Link builder with selected text reuse | Full | Build-Ready | v1 | High | URL sanity checks and title generation |
| P1-MD-05 | Ordered and unordered list helpers | Full | Build-Ready | v1 | High | Convert paragraph block to clean list |
| P1-MD-06 | Table builder workflow | Full | Scoped | v1 | High | Column intent suggestions from data |
| P1-MD-07 | Footnote manager create, insert, clear | Full | Planned | v2 | Medium High | Footnote integrity checker |
| P1-MD-08 | Markdown to HTML export | Full | Scoped | v1 | High | Accessibility lint before export |
| P1-MD-09 | Markdown to Word export | Full | Planned | v2 | Medium High | Style-preserving export profiles |
| P1-HTML-01 | HTML structure assistant | Full | Scoped | v1 | High | Semantic-first generator |
| P1-HTML-02 | HTML accessibility checks | Full | Scoped | v1 | High | One-command fix preview |
| P1-TXT-01 | EASYText Studio reusable text blocks with names | Full | Build-Ready | v1 | High | Template variables and quick fill |
| P1-TXT-02 | EASYText Studio trigger plus space expansion | Full | Build-Ready | v1 | High | Conflict detection and fast rename |
| P1-TXT-03 | EASYText Studio folder tree organization | Full | Build-Ready | v1 | High | Fast move and folder browse in command palette |

### 21.4 P1 Notes, Help, and Knowledge Features
| ID | Atomic Feature | Parity Goal | Status | Release | Confidence | Magical Uplift |
|---|---|---|---|---|---|---|
| P1-NOTE-01 | Quick note from anywhere | Full | Scoped | v1 | High | Context-tagged quick notes |
| P1-NOTE-02 | Advanced note categories and nesting | Full | Planned | v2 | Medium High | Smart category recommendations |
| P1-NOTE-03 | Related note links bidirectional | Full | Planned | v2 | Medium High | Auto-related suggestion engine |
| P1-NOTE-04 | Note attachments and open-copy actions | Full | Planned | v2 | Medium High | Attachment safety and provenance tags |
| P1-NOTE-05 | Audio note recording and attach | Full | Planned | v2 | Medium High | Transcript generation on save |
| P1-NOTE-06 | Backup and restore points for notes | Full | Planned | v2 | Medium High | Timeline restore visualization |
| P1-HELP-01 | Global custom help notes | Full | Scoped | v1 | High | Contextual help suggestions |
| P1-HELP-02 | App-specific custom help notes | Full | Scoped | v1 | High | Auto-scope detection by process |
| P1-WEBTXT-01 | Domain or page web reminders | Full | Planned | v2 | Medium High | Reminder confidence and stale-note detection |

### 21.5 P1 File, Shortcut, and Utility Operations
| ID | Atomic Feature | Parity Goal | Status | Release | Confidence | Magical Uplift |
|---|---|---|---|---|---|---|
| P1-CUTS-01 | File and folder shortcut creation | Full | Scoped | v1 | High | Smart naming from source context |
| P1-CUTS-02 | Web shortcut creation | Full | Scoped | v1 | High | URL normalization and dedupe |
| P1-CUTS-03 | Shortcut launch list by type | Full | Scoped | v1 | High | Dynamic relevance sort |
| P1-CUTS-04 | Insert shortcut folder path in dialogs | Full | Planned | v2 | Medium High | Dialog mode auto-detection |
| P1-CUTS-05 | Shortcut presets by number | Full | Planned | v2 | Medium High | Workflow presets |
| P1-TAG-01 | Tag files in explorer | Full | Scoped | v1 | High | Session summary and undo |
| P1-TAG-02 | Batch copy and cut tagged files | Full | Scoped | v1 | High | Dry-run preview for large operations |
| P1-TAG-03 | Batch delete tagged files with confirm | Full | Scoped | v1 | High | Safety hold timer and restore bin |
| P1-TAG-04 | Tag outlook messages and move/copy | Full | Planned | v2 | Medium | Clear mode boundaries and warnings |
| P1-TABLE-01 | Capture full table | Full | Scoped | v1 | High | Structured output modes |
| P1-TABLE-02 | Capture row, column, cell | Full | Scoped | v1 | High | Header-aware extraction |
| P1-TABLE-03 | Buffer management and copy | Full | Scoped | v1 | High | Multi-source capture session IDs |
| P1-START-01 | Curated launcher list | Full | Scoped | v1 | High | App usage-driven ranking |
| P1-START-02 | Add focused app automatically | Full | Scoped | v1 | High | Name cleanup suggestions |
| P1-MAP-01 | Map folder to drive letter | Full | Planned | v2 | Medium High | Collision and persistence diagnostics |

### 21.6 P2 Time, Calendar, Social, and AI Operations
| ID | Atomic Feature | Parity Goal | Status | Release | Confidence | Magical Uplift |
|---|---|---|---|---|---|---|
| P2-CLOCK-01 | Hear and insert time and date variants | Full | Scoped | v2 | High | Locale-aware templates |
| P2-CLOCK-02 | Stopwatch start, stop, clear, precision | Full | Scoped | v2 | High | Voice plus braille precision display |
| P2-CLOCK-03 | Countdown and alarm | Full | Planned | v2 | High | Intelligent reminders before expiry |
| P2-CLOCK-04 | Chime intervals and control | Full | Planned | v2 | Medium High | Quiet hours automation |
| P2-CLOCK-05 | Time monitor for minute boundary | Full | Planned | v2 | Medium High | Calibration mode for precision tasks |
| P2-DIARY-01 | Appointment creation and browse | Full | Planned | v2 | High | Timeline day map with fast jump |
| P2-DIARY-02 | Date math utilities | Full | Planned | v2 | High | Natural language date assistant |
| P2-DIARY-03 | Task integration and ICS sync | Partial | Planned | v3 | Medium High | Calendar bridge health checks |
| P2-SOC-01 | Mastodon and Bluesky timeline model | Partial | Planned | v3 | Medium | Field-configurable read profile |
| P2-SOC-02 | Compose, reply, quote, bookmark, filters | Partial | Planned | v3 | Medium | Intent-based quick actions |
| P2-SOC-03 | Braille flash status and sound packs | Partial | Planned | v3 | Medium | Personalized notification channels |
| P2-AI-01 | Chat menu operations and context mode | Full | Scoped | v2 | High | Conversation state announcements |
| P2-AI-02 | AI tools library for text transformation | Full | Planned | v2 | High | Tool suggestions from selected text intent |
| P2-AI-03 | Prompt library create/load/delete | Full | Planned | v2 | High | Prompt recommendations by workflow |
| P2-AI-04 | Document Q and A upload workflow | Full | Planned | v3 | Medium High | Source-cited answer sections |
| P2-AI-05 | Image generation and audio transcription | Full | Planned | v3 | Medium High | End-to-end save pipeline and metadata |

### 21.7 P3 Media and Entertainment (Intentionally Lower Priority)
| ID | Atomic Feature | Parity Goal | Status | Release | Confidence | Magical Uplift |
|---|---|---|---|---|---|---|
| P3-MEDIA-01 | Unified media center shell | Partial | Planned | v4 | Medium | One command to continue last media task |
| P3-RADIO-01 | Station search and favorites | Partial | Planned | v4 | Medium | Cross-source relevance ranking |
| P3-RADIO-02 | Scheduled recording with recovery | Partial | Planned | v4 | Medium | Recorder health monitor and auto-retry |
| P3-POD-01 | Podcast feed management | Partial | Planned | v4 | Medium | New-episode intelligence summaries |
| P3-POD-02 | Chapter-aware playback | Partial | Planned | v4 | Medium | Chapter jump memory |
| P3-AUDIO-01 | Local audio and playlists | Partial | Planned | v4 | Medium | Playlist intent actions |
| P3-SOUND-01 | Accessible sound routing controls | Partial | Planned | v4 | Medium | One-key meeting mode profiles |
| P3-GAME-01 | Game hub integration layer | Pending Detail | v4 | Medium Low | Accessibility coaching overlays |

### 21.8 P1 to P3 Database and File-Manager Expansion
| ID | Atomic Feature | Parity Goal | Status | Release | Confidence | Magical Uplift |
|---|---|---|---|---|---|---|
| P1-DATA-01 | Database create and select | Full | Planned | v2 | Medium High | Template packs by scenario |
| P1-DATA-02 | Field type model and validation rules | Full | Planned | v2 | Medium High | Guided field wizard |
| P1-DATA-03 | Entry grid view and read-only detail view | Full | Planned | v2 | Medium High | Spoken and braille column pivots |
| P1-DATA-04 | Sort and search by selected fields | Full | Planned | v2 | Medium High | Search intent shortcuts |
| P1-DATA-05 | Export to csv and readable text | Full | Planned | v2 | Medium High | Export quality checker |
| P2-DATA-06 | Jamal bridge connector import and export | Full | Planned | v3 | Medium | One-click compatibility check |
| P2-DATA-07 | Jamal launch bridge | Full | Planned | v3 | Medium | Return-path session bookmark |
| P3-DATA-08 | Jamal sync mode with conflict resolution | Full | Planned | v4 | Medium Low | Guided merge with previews and rollback |
| P1-FILE-01 | File browse list with key metadata | Partial | Planned | v2 | High | Adaptive concise or detailed read modes |
| P1-FILE-02 | File operations copy, paste, rename, delete | Partial | Planned | v2 | High | Risk-tier prompts by action type |
| P1-FILE-03 | Zip creation and full-path copy | Partial | Planned | v2 | High | One-step archive presets |
| P1-FILE-04 | File tagging and report tagged set | Partial | Planned | v2 | High | Smart group operations |

## 22. Python Implementation Blueprint
This section defines the implementation structure to keep delivery predictable.

### 22.1 Repository Structure
1. src/core: command bus, event model, state engine, telemetry.
2. src/access: speech output, braille output, earcon output, verbosity policies.
3. src/modules: snapspan, pocketclips, mergeboard, waymarks, trailback, bits_easy, relaydesk, dataforge, pathpilot, socialorbit, media.
4. src/adapters: outlook, thunderbird, browser, whatsapp desktop, whatsapp web, x, mastodon, bluesky, players.
5. src/ai: prompt manager, tool orchestrator, provider brokers, confidence engine.
6. src/storage: local sqlite plus json snapshots for portable sync.
7. tests/unit, tests/integration, tests/accessibility, tests/adapters.

### 22.2 Core Contracts
1. Command contract: id, intent, context, dry_run, requires_confirm, timeout.
2. Adapter contract: capability map, execute, fallback, diagnostics.
3. Feedback contract: speech text, braille text, earcon id, confidence, next action hints.
4. Action log contract: who, what, where, result, reversible token.

### 22.3 State and Persistence
1. Fast local state for active session.
2. Durable sqlite store for clips, anchors, notes, prompts, settings.
3. Snapshot store for restore and rollback.
4. Optional cloud-synced data root.

## 23. Test and Validation Matrix
This matrix is mandatory before release.

### 23.1 Accessibility Validation
1. Keyboard-only test pass for all interactive surfaces.
2. Speech and braille parity verification for each core action.
3. Screen-reader regression suite per module.
4. Latency target under one second for local deterministic actions.

### 23.2 Functional Validation
1. Unit coverage target 85 percent on core modules.
2. Integration tests for adapter contracts and fallback behavior.
3. End-to-end scenario tests for top 20 workflows.
4. Recovery tests for unexpected app state changes.

### 23.3 AI Validation
1. Suggestion relevance and correction-rate tracking.
2. Hallucination containment checks using source-cited output where required.
3. Deterministic fallback tests for provider outage.
4. Privacy mode verification for local-only operation.

## 24. Go and No-Go Criteria
Release cannot proceed unless all criteria pass.

### 24.1 Go Criteria
1. All P0 atomic features marked Build-Ready and verified.
2. No blocker severity accessibility defects.
3. Adapter capabilities accurately flagged Full, Partial, or Experimental.
4. Rollback and restore mechanisms validated.
5. Release notes include known limitations and workarounds.

### 24.2 No-Go Triggers
1. Any silent-failure path in P0 workflows.
2. Any speech and braille mismatch in critical actions.
3. Any destructive action without confirmation path.
4. Any unresolved data-loss risk in DataForge or bridge operations.

### 24.3 Magical 1.0 Release Gate
All items below must pass for a magical 1.0 claim:
1. Fast: palette open, command discovery, and command execution latency targets are met.
2. Reversible: all critical mutating operations have rollback or explicit undo strategy.
3. Graceful: every failed action gives immediate fallback guidance.
4. Productive: a user can complete one meaningful cross-app workflow within 60 seconds.
5. Trustworthy: confidence and action rationale are always available for adaptive behaviors.

## 25. Ownership and Delivery Cadence
1. Product Lead: prioritization and release sequencing.
2. Accessibility Lead: gatekeeper for speech, braille, and keyboard criteria.
3. Core Platform Engineer: command bus, storage, and shared services.
4. Adapter Engineers: app integrations and compatibility maintenance.
5. AI Engineer: assistant workflows and confidence systems.
6. QA Lead: automated and manual validation.

Cadence:
1. Weekly integration build.
2. Biweekly accessibility audit.
3. Monthly adapter stability review.
4. Quarterly roadmap recalibration.

## 26. Final Completeness Declaration
This PRD now includes:
1. Full feature-family mapping coverage for the Baseline help index and reviewed 11.5 additions.
2. Atomic feature checklist for execution planning.
3. Ranked priorities with lower priority placement for radio, podcasts, and RSS.
4. Database-first strategic track with Jamal bridge pathways.
5. Accessibility and AI guardrails integrated into architecture, testing, and release criteria.

Remaining effort is implementation and atomic backlog execution, not missing strategic scope.

## 27. Decomposition Work Complete
This section completes decomposition by translating all mapped families into implementation epics and story packs.

### 27.1 Decomposition Rules
1. Every mapped feature family has at least one epic and one story pack.
2. Every story pack has acceptance tests and explicit dependencies.
3. Every Partial Planned and Pending Detail family has closure milestones.
4. No release can claim parity closure without passing section 24 go criteria.

### 27.2 Epic Index
| Epic ID | Epic Name | Source Family Coverage | Release Target |
|---|---|---|---|
| E01 | Selection and Clip Intelligence | BaselineSelect, BaselineClips, clipboard append, BaselineTexts abbreviations | v1 |
| E02 | Anchors, Alerts, and Context Return | BaselinePoints, BaselineAlerts, Sticky notes context behaviors | v1-v2 |
| E03 | Markdown and HTML Authoring | Markdown, HTML Assistant, text conversion workflows | v1-v2 |
| E04 | Notes and Knowledge Workspace | BaselineNotes, Virtual Notes, Custom Help, Custom Web Text | v1-v2 |
| E05 | Shortcuts and File Navigation | Shortcut Catalog, Start Menu, Mapping drives, file property helpers | v1-v2 |
| E06 | Tagging and Table Capture | BaselineTags, Table Capture | v1-v2 |
| E07 | Time, Diary, and Task Flows | BaselineClock, BaselineDiary, calendar integration, tasks | v2-v3 |
| E08 | Communication and Social Adapters | BaselineConnect, email workflows, WhatsApp, X, Mastodon, Bluesky | v2-v3 |
| E09 | Search and Retrieval Layer | BaselineSearch, web workflow helpers, old reader and rss patterns | v2-v4 |
| E10 | Database and Structured Records | Baseline Database and Jamal bridge | v2-v4 |
| E11 | Backup, Restore, and Portability | Backup and Restore Manager, personal backup, migration flows | v2-v3 |
| E12 | AI Assistant Platform | ChatGPT setup, prompts, tools, transcription, image generation | v2-v3 |
| E13 | Utility Mesh and Accessibility Ops | Progress indicators, speech history, notifications, audio split, symbols | v1-v3 |
| E14 | Media and Entertainment Layer | Audio, Radio, Podcasts, Spotify, games, recorder integrations | v4 |
| E15 | Braille-First Command Surface | BrailleEas and braille parity across all modules | v1-v4 |
| E16 | Joplin Interoperability | Joplin import, export, linked workspace, conflict-safe sync | v2-v3 |
| E17 | StarKey Everywhere Global Palette | Global palette runtime, context routing, command orchestration, merge logic | v1-v3 |
| E18 | Magical 1.0 Differentiators | Intent memory, command chains, confidence fallback, capture inbox, recovery journal, context layer, profile tuning, portability, first-run missions, integration health | v1-v2 |

### 27.3 Story Pack Decomposition by Epic

#### E01 Selection and Clip Intelligence
Story packs:
1. SP-E01-A Selection markers, context announce, jump-back.
2. SP-E01-B Clip slots copy, paste, protect, delete, edit.
3. SP-E01-C Append clipboard modes and separator policies.
4. SP-E01-D Text expansions and primary quick insert shortcut.

Dependencies:
1. Core command bus.
2. Storage service.
3. Speech and braille output layer.

Definition of done:
1. All P0 stories pass automated and manual accessibility tests.
2. Selection state survives app focus changes within supported contexts.

#### E02 Anchors, Alerts, and Context Return
Story packs:
1. SP-E02-A Anchor set and retrieve by index.
2. SP-E02-B Domain or page anchor modes.
3. SP-E02-C Alert trigger capture and notify policies.
4. SP-E02-D Return path memory with fallback strategies.

Dependencies:
1. Browser adapter baseline.
2. Context identity model.

Definition of done:
1. Retrieval success above 90 percent in certified contexts.
2. Drift fallback path announced with actionable next step.

#### E03 Markdown and HTML Authoring
Story packs:
1. SP-E03-A Markdown structure insertion, lists, links, tables, footnotes.
2. SP-E03-B HTML generation and semantic structure validation.
3. SP-E03-C Markdown to html and markdown to word export bridges.
4. SP-E03-D Accessibility lint and corrective previews.

Dependencies:
1. BITS-EASY parser layer.
2. Accessibility rule engine.

Definition of done:
1. Deterministic output for non-ai transforms.
2. All generated content passes markdown and accessibility checks.

#### E04 Notes and Knowledge Workspace
Story packs:
1. SP-E04-A Quick note and dual-mode note views.
2. SP-E04-B Categories, nested categories, and note move workflows.
3. SP-E04-C Related notes, attachments, links, advanced fields.
4. SP-E04-D Custom help and custom web text authoring and search.
5. SP-E04-E Restore points and recovery timeline.

Dependencies:
1. Storage snapshots.
2. Search index service.

Definition of done:
1. No note-loss paths under supported operations.
2. Recovery operations validated through restore drills.

#### E05 Shortcuts and File Navigation
Story packs:
1. SP-E05-A Shortcut creation for files, folders, and web.
2. SP-E05-B Shortcut launchers, filters, categories, and presets.
3. SP-E05-C Insert folder paths in save and attach dialogs.
4. SP-E05-D Start menu curation and auto-add focused app.
5. SP-E05-E Drive map assignment and safe removal.

Dependencies:
1. Explorer adapter.
2. Dialog detection service.

Definition of done:
1. All path insert and launch actions work with predictable feedback.
2. Invalid path and collisions handled with clear error messaging.

#### E06 Tagging and Table Capture
Story packs:
1. SP-E06-A File tagging session management and verification.
2. SP-E06-B Batch copy, cut, delete, and playlist add operations.
3. SP-E06-C Outlook message tagging move and copy operations.
4. SP-E06-D Table capture row, column, cell, headers, and buffer exports.

Dependencies:
1. Explorer and outlook adapters.
2. Buffer service.

Definition of done:
1. Batch operations are reversible where feasible.
2. Table extraction preserves chosen separator and order.

#### E07 Time, Diary, and Task Flows
Story packs:
1. SP-E07-A Time speak and insert variants.
2. SP-E07-B Stopwatch with precision and recurring cues.
3. SP-E07-C Countdown, alarm, and chime policies.
4. SP-E07-D Time monitor and braille per-second display.
5. SP-E07-E Appointment, date math, and task integration.
6. SP-E07-F ICS sync and calendar bridge interoperability.

Dependencies:
1. Time service.
2. Calendar adapter.

Definition of done:
1. Time-sensitive operations meet precision and latency targets.
2. Calendar flows remain keyboard-only and screen-reader stable.

#### E08 Communication and Social Adapters
Story packs:
1. SP-E08-A Contact store and insertion workflows.
2. SP-E08-B Outlook and thunderbird core productivity actions.
3. SP-E08-C WhatsApp desktop and web conversation accelerators.
4. SP-E08-D X workflow and reading profile adapter.
5. SP-E08-E Mastodon and bluesky timeline client behaviors.
6. SP-E08-F Social nicknames, filters, and notifications.

Dependencies:
1. App adapter SDK.
2. Capability flags and fallback logic.

Definition of done:
1. Adapter stability scores meet release threshold.
2. Unsupported states always present deterministic fallback guidance.

#### E09 Search and Retrieval Layer
Story packs:
1. SP-E09-A Unified search query routing.
2. SP-E09-B Results memory and revisit.
3. SP-E09-C Source-specific parser adapters.
4. SP-E09-D Retrieval summarization and action extraction.

Dependencies:
1. Adapter registry.
2. Search index and session memory.

Definition of done:
1. Query routing returns useful results across baseline sources.
2. Return-to-result position retained after open and close cycle.

#### E10 Database and Structured Records
Story packs:
1. SP-E10-A Database create, select, and delete.
2. SP-E10-B Field model and validators.
3. SP-E10-C Entry add, edit, delete, list, and detail views.
4. SP-E10-D Sorting, searching, and export.
5. SP-E10-E Jamal connector import and export.
6. SP-E10-F Jamal launch bridge.
7. SP-E10-G Jamal optional sync with conflict resolution.

Dependencies:
1. Data model translator.
2. Snapshot and rollback service.

Definition of done:
1. No destructive merge without preview and restore point.
2. Export outputs verified for readability and integrity.

#### E11 Backup, Restore, and Portability
Story packs:
1. SP-E11-A Backup and restore for app and suite settings.
2. SP-E11-B Personal backup source and target manager.
3. SP-E11-C Selected folder backup and restore sets.
4. SP-E11-D Migration workflows between version profiles.

Dependencies:
1. Snapshot service.
2. Path validation subsystem.

Definition of done:
1. Restore drills pass with zero data loss in test scenarios.
2. All path prompts validate full path integrity.

#### E12 AI Assistant Platform
Story packs:
1. SP-E12-A API key setup and policy UX.
2. SP-E12-B Conversation state and session persistence.
3. SP-E12-C Tool menu operations for transformations.
4. SP-E12-D Prompt library lifecycle.
5. SP-E12-E Document Q and A upload workflows.
6. SP-E12-F Image generation and transcription operations.

Dependencies:
1. AI provider broker.
2. Privacy and policy controls.

Definition of done:
1. Deterministic fallback path available when AI provider unavailable.
2. All AI actions include preview and rationale text.

#### E13 Utility Mesh and Accessibility Ops
Story packs:
1. SP-E13-A Progress cues and tutorials.
2. SP-E13-B Speech history skim, copy, and continuous-range operations.
3. SP-E13-C Notification rules import and restore.
4. SP-E13-D Audio splitter and card routing.
5. SP-E13-E Window bookmarking.
6. SP-E13-F Symbol and alt-code assistant.
7. SP-E13-G Computer report and diagnostics output.

Dependencies:
1. OS integration helpers.
2. JAWS and NVDA interoperability abstraction where needed.

Definition of done:
1. Utilities avoid keystroke conflicts in baseline profile.
2. Diagnostics outputs are readable and exportable.

#### E14 Media and Entertainment Layer
Story packs:
1. SP-E14-A Unified media shell task model.
2. SP-E14-B Player controls, bookmarks, speed, sleep timer.
3. SP-E14-C Radio search, favorites, presets, and scheduled recording.
4. SP-E14-D Podcast feed and episode workflows.
5. SP-E14-E Audio playlists and metadata editors.
6. SP-E14-F Music recognition and source capture controls.
7. SP-E14-G Optional game hub integrations.

Dependencies:
1. Media adapter layer.
2. Audio device abstraction.

Definition of done:
1. P0 through P2 releases are not blocked by this epic.
2. All media features pass the same accessibility gates.

#### E15 Braille-First Command Surface
Story packs:
1. SP-E15-A Braille command grammar and abbreviations.
2. SP-E15-B Braille parity for all core feedback events.
3. SP-E15-C Braille command profile editor.
4. SP-E15-D Braille conflict resolution and fallback prompts.

Dependencies:
1. Braille output abstraction.
2. Command parser.

Definition of done:
1. All P0 actions have equivalent braille path.
2. Braille and speech content parity verified by tests.

#### E16 Joplin Interoperability
Story packs:
1. SP-E16-A Joplin note import pipeline.
2. SP-E16-B Joplin note export pipeline.
3. SP-E16-C Attachment and tag mapping.
4. SP-E16-D Linked workspace refresh and conflict reporting.

Dependencies:
1. ThoughtDock storage model.
2. Attachment manager.
3. Snapshot and rollback service.

Definition of done:
1. Import and export round-trip preserves core note content and tags.
2. Conflict handling provides non-destructive preview and rollback.

#### E17 StarKey Everywhere Global Palette
Story packs:
1. SP-E17-A Global invoker and palette shell.
2. SP-E17-B Command registry, ranking, and fuzzy resolver.
3. SP-E17-C Context provider and capability envelope.
4. SP-E17-D Action orchestrator with safety pipeline.
5. SP-E17-E Selection and merge profile integrations.
6. SP-E17-F Adapter bundles for browser, Outlook, Word, Notepad, and VS Code.

Dependencies:
1. Core command bus and feedback bus.
2. Adapter SDK and context provider interfaces.
3. Storage and rollback token services.

Definition of done:
1. Palette opens and executes core commands in baseline target apps.
2. Accessibility parity is verified for command search and execution feedback.
3. Rollback works for all mutating palette actions.

#### E18 Magical 1.0 Differentiators
Story packs:
1. SP-E18-A Intent memory per app.
2. SP-E18-B One-key command chains and templates.
3. SP-E18-C Confidence and fallback narration framework.
4. SP-E18-D Universal quick capture inbox.
5. SP-E18-E Recover everything journal.
6. SP-E18-F Ambient where-am-I layer.
7. SP-E18-G Accessibility tuning profiles.
8. SP-E18-H Cross-device workflow portability.
9. SP-E18-I Intelligent first-run missions.
10. SP-E18-J Live integration health panel.

Dependencies:
1. E17 global palette runtime.
2. E13 utility and diagnostics services.
3. E15 braille parity foundations.

Definition of done:
1. At least one cross-app mission workflow is completed by users in under 60 seconds during validation.
2. All differentiator flows pass accessibility and reliability gates.
3. Health panel detects and reports adapter degradation with actionable remediation.

## 28. Dependency and Sequencing Matrix
| Sequence | Epic | Depends On | Unlocks |
|---|---|---|---|
| S1 | E01 | Core platform | E03, E04, E08 |
| S2 | E13 | Core platform | E07, E15 |
| S3 | E03 | E01, E13 | E12 tool integration |
| S4 | E04 | E01, storage | E11 portability |
| S5 | E05 | E01, explorer adapter | E06 and E10 file workflows |
| S6 | E02 | E01, browser adapter | E09 |
| S7 | E06 | E05 | E08 productivity actions |
| S8 | E07 | E13 | E08 scheduling integrations |
| S9 | E12 | E03, E04 | advanced assist flows |
| S10 | E10 | E05, storage | Jamal bridge and structured workflows |
| S11 | E08 | E02, E05, E07 | social and communication integration |
| S12 | E11 | E04, E10 | resilience and migration |
| S13 | E15 | E01, E13 | full parity certification |
| S14 | E14 | E13, media adapters | optional lower-priority expansion |
| S15 | E16 | E04, E11 | notebook interoperability and migration |
| S16 | E17 | E01, E13, E15 | global palette and command orchestration |
| S17 | E18 | E17, E13, E15 | magical 1.0 user experience envelope |

## 29. Completion Ledger by Mapped Family
This ledger marks decomposition closure for each mapped family.

| Family Group | Decomposition Complete | Closure Evidence |
|---|---|---|
| Selection and clips | Yes | E01 and SP-E01 series |
| Anchors and alerts | Yes | E02 and SP-E02 series |
| Markdown and html | Yes | E03 and SP-E03 series |
| Notes and custom help | Yes | E04 and SP-E04 series |
| Shortcuts and launcher | Yes | E05 and SP-E05 series |
| Tagging and table capture | Yes | E06 and SP-E06 series |
| Time, diary, tasks | Yes | E07 and SP-E07 series |
| Communication and social | Yes | E08 and SP-E08 series |
| Search and retrieval | Yes | E09 and SP-E09 series |
| Database and Jamal bridge | Yes | E10 and SP-E10 series |
| Backup and restore | Yes | E11 and SP-E11 series |
| AI and prompt workflows | Yes | E12 and SP-E12 series |
| Utility mesh | Yes | E13 and SP-E13 series |
| Media and entertainment | Yes | E14 and SP-E14 series |
| Braille-first command surface | Yes | E15 and SP-E15 series |
| Joplin interoperability | Yes | E16 and SP-E16 series |
| Global command palette | Yes | E17 and SP-E17 series |
| Magical 1.0 differentiators | Yes | E18 and SP-E18 series |

## 30. Remaining Work Classification
Remaining work is now implementation execution only.

Implementation-only categories:
1. Coding and adapter integration.
2. Automated and manual testing.
3. Release hardening and performance tuning.
4. Documentation and training artifacts.

No remaining strategic decomposition gaps are open in this PRD version.

## 31. Final Decomposition Sign-Off
Decomposition is complete for all mapped Baseline families and reviewed update features, including:
1. Explicit epic coverage.
2. Story-pack breakdown.
3. Dependency sequencing.
4. Done criteria.
5. Closure ledger.

This PRD is now complete at strategic and decomposition levels and ready for implementation planning and sprint execution.

## 32. Feature Flag Governance and Beta Rollout Addendum

### 32.1 Purpose
This section defines the production policy for controlled feature rollout in BITS-EASY using feature flags, including offline safety, beta authority controls, keybinding gating, and manifest trust verification.

Objectives:
1. Keep stable users on stable behavior by default.
2. Allow controlled beta testing without shipping a new add-on package for every toggle.
3. Guarantee deterministic behavior when internet or manifest endpoints are unavailable.
4. Ensure disabled features are not executable from either palette or keyboard gesture paths.

### 32.2 Rollout Model

Feature stages:
1. stable
2. beta
3. experimental

Authority tiers:
1. stable
2. beta
3. internal

Stage visibility by authority:
1. stable authority: stable stage only.
2. beta authority: stable + beta stages.
3. internal authority: stable + beta + experimental stages.

Resolution rule:
1. A command is executable only when both conditions are true:
2. The feature flag is enabled.
3. The current authority allows the flag stage.

### 32.3 Manifest Sources and Fallback Chain

Manifest source precedence:
1. Remote manifest (if configured and reachable).
2. Cached manifest (last known valid manifest).
3. Bundled fallback manifest shipped in the add-on.

Operational behavior:
1. Startup attempts remote refresh within bounded timeout.
2. Remote failure never blocks startup.
3. Cache failure falls through to bundled fallback.
4. Bundled fallback is always required in package artifacts.

Data file contract:
1. Bundled fallback location: config/features/feature-flags.fallback.v1.json
2. Local cache: user profile AppData BITS-EASY state store.
3. Local authority and overrides state: user profile AppData BITS-EASY state store.

### 32.4 Security and Trust Model

Current baseline security:
1. Authority and overrides are local user state.
2. Beta access uses one-way SHA-256 grant matching.

Required hardening for production remote rollout:
1. Signed manifest verification using public key cryptography.
2. Signature verification must occur before accepting remote or cached manifest content.
3. On signature failure, manifest must be rejected and system must fall back to previously trusted source.
4. Key rotation policy must support at least current and next signing keys.

Manifest integrity requirements:
1. Manifest payload must include signature metadata and key identifier.
2. Client must verify payload canonicalization before signature check.
3. Unsigned payloads are valid only for bundled local fallback in development mode.

Threat model assumptions:
1. Remote endpoint tampering is possible.
2. Cache poisoning is possible.
3. Local setting tampering by same local user is in-scope but not privilege-escalating.

### 32.5 Command and Keybinding Enforcement Contract

Enforcement points:
1. Command dispatch gate: blocked commands return explicit feature-gate reason payload.
2. Keybinding registration gate: disabled-feature bindings are filtered out before OS hotkey service starts.
3. Key chord resolution gate: any blocked command is excluded from accepted chord candidates.

Required user-visible behavior:
1. If a feature is not enabled, associated keystrokes are not active.
2. If a blocked command is invoked through non-key path, user receives deterministic guidance.
3. No silent fallback to disabled feature execution.

Telemetry requirements:
1. featureGate.allowed
2. featureGate.reason
3. featureGate.flagId
4. featureGate.stage
5. featureGate.authority
6. manifest source in use: remote, cache, fallback

### 32.6 User Experience Requirements

Settings and control surface:
1. Global setting checkbox: Enable beta features.
2. Toggling off beta features must force authority back to stable.
3. Toggling on beta features must set authority to beta unless higher authority already exists.

Feature Flags panel requirements:
1. Show current authority.
2. Show manifest source and last refresh result.
3. List all flags with stage and enabled state.
4. Allow refresh manifest action.
5. Allow grant beta access code flow for authorized testers.
6. Allow per-flag override for diagnostic workflows where policy permits.

Accessibility requirements for panel:
1. Fully keyboard operable.
2. Speech and braille parity for state changes.
3. Actionable failure messages for refresh and grant operations.

### 32.7 Manifest Schema Requirements

Minimum schema:
1. version
2. authorityStages mapping
3. flags collection
4. grants collection

Flag object minimum fields:
1. id
2. name
3. description
4. stage
5. enabledByDefault
6. commandIds and or commandPrefixes

Grant object minimum fields:
1. name
2. sha256
3. authority
4. enableFlags

Forward-compatibility policy:
1. Unknown fields must be ignored safely.
2. Unknown stage values must default to blocked.
3. Unknown authority values must default to stable.

### 32.8 Example Rollout Waves

Wave model:
1. Wave A: internal only, experimental stage.
2. Wave B: closed beta, beta stage by invite grants.
3. Wave C: open beta, beta stage by default for opted-in users.
4. Wave D: stable promotion with fallback flag retained for rollback window.

Promotion criteria:
1. Accessibility acceptance complete.
2. Regression budget below threshold.
3. Recovery path validated in release hardening.
4. Support and docs artifacts complete.

### 32.9 Fail-Safe and Recovery Rules

Fail-safe rules:
1. Manifest parse error: reject and fall back.
2. Signature failure: reject and fall back.
3. Network timeout: skip remote and fall back.
4. Corrupt cache: ignore cache and use fallback.

Recovery behavior:
1. Stable user path must remain uninterrupted.
2. Hotkeys for blocked features must be absent from active registration after recovery.
3. Next successful refresh can restore prior beta availability.

### 32.10 Acceptance Criteria

Functional acceptance:
1. Disabled beta feature command cannot execute in stable authority.
2. Disabled beta feature keybinding is absent from active hotkeys.
3. Enabling beta features in settings exposes beta-eligible flags.
4. Turning beta features off hides beta-stage execution immediately.

Resilience acceptance:
1. Remote unavailable path uses cache or bundled fallback without startup failure.
2. Corrupt remote payload does not alter current trusted state.
3. Signature verification rejects tampered payloads once signing is enabled.

Accessibility acceptance:
1. Feature Flags panel passes keyboard-only and screen-reader workflow checks.
2. State transitions announce authority and activation changes clearly.

### 32.11 Test Plan Additions

Automated tests required:
1. Authority gate unit tests by stage and command mapping.
2. Binding filter tests proving blocked command hotkeys are removed.
3. Remote-refresh fallback chain tests: remote to cache to fallback.
4. Grant code tests including invalid, valid, and downgrade scenarios.
5. Signature verification tests for valid and invalid signatures.

Manual tests required:
1. NVDA settings checkbox toggle: verify immediate authority effect.
2. Feature Flags panel refresh and grant workflow.
3. Offline startup and command behavior with no network.
4. Re-enable network and confirm refresh recovery.

### 32.12 Operations and Governance

Release governance:
1. Product owner approves stage transitions.
2. Accessibility lead approves user-facing beta promotions.
3. Engineering lead approves manifest signing key rotation.

Audit requirements:
1. Record manifest version and source used at startup.
2. Record authority changes and grant events.
3. Record blocked-command events for rollout diagnostics.

Rollback policy:
1. Flag-level rollback must be possible within minutes by manifest update.
2. Add-on release rollback remains available for structural defects.

### 32.13 PRD Traceability Matrix

This matrix maps Section 32 requirement groups to concrete implementation and verification artifacts.

| Requirement ID | Section 32 Requirement Group | Primary Implementation Artifacts | Verification Artifacts | Status | Owner | Target Milestone |
|---|---|---|---|---|---|---|
| FF-R01 | 32.2 Rollout model and authority stages | src/bits_easy_runtime/feature_flags.py, config/features/feature-flags.fallback.v1.json | tests/test_feature_flags.py | Implemented | Runtime Engineering | v1.1 |
| FF-R02 | 32.3 Remote-cache-fallback manifest chain | src/bits_easy_runtime/feature_flags.py, src/bits_easy_runtime/dispatcher.py, src/bits_easy_runtime/config.py | tests/test_feature_flags.py | Implemented | Runtime Engineering | v1.1 |
| FF-R03 | 32.4 Manifest trust and signature hardening | src/bits_easy_runtime/feature_flags.py | tests/test_feature_flags.py plus signature tests to be added | Partial | Security Engineering | v1.2 |
| FF-R04 | 32.5 Dispatch and keybinding enforcement | src/bits_easy_runtime/dispatcher.py, addon/globalPlugins/bits_easy.py | tests/test_feature_flags.py, tests/test_dispatcher_integration.py | Implemented | Runtime Engineering | v1.1 |
| FF-R05 | 32.6 User UX for beta and flags control | src/bits_easy_runtime/settings.py, addon/bits_easy_settings.py, addon/globalPlugins/bits_easy.py | tests/test_settings_store.py, tests/test_mode_control_panel.py, manual NVDA settings validation | Implemented | UX and Accessibility Engineering | v1.1 |
| FF-R06 | 32.7 Manifest schema and compatibility defaults | config/features/feature-flags.fallback.v1.json, src/bits_easy_runtime/feature_flags.py | tests/test_feature_flags.py | Implemented | Runtime Engineering | v1.1 |
| FF-R07 | 32.8 Rollout waves and promotion policy | docs/FEATURE-FLAGS-BETA.md, docs/prd.md | release checklist and staged rollout review | Planned Ops | Product and Release | v1.2 |
| FF-R08 | 32.9 Fail-safe and recovery behavior | src/bits_easy_runtime/feature_flags.py, src/bits_easy_runtime/dispatcher.py, addon/globalPlugins/bits_easy.py | tests/test_feature_flags.py, manual offline startup validation | Implemented | Runtime Engineering | v1.1 |
| FF-R09 | 32.10 Functional and resilience acceptance | src/bits_easy_runtime/dispatcher.py, addon/globalPlugins/bits_easy.py, src/bits_easy_runtime/feature_flags.py | tests/test_feature_flags.py, tests/test_dispatcher_integration.py | Implemented | QA Automation | v1.1 |
| FF-R10 | 32.11 Automated and manual test expansion | tests/test_feature_flags.py, tests/test_settings_store.py, tests/test_mode_control_panel.py | CI run plus manual panel and offline scenarios | In Progress | QA Automation | v1.2 |
| FF-R11 | 32.12 Governance, audit, and rollback operations | src/bits_easy_runtime/feature_flags.py, docs/FEATURE-FLAGS-BETA.md, docs/RELEASE-HARDENING-CHECKLIST.md | release and audit process checks | Planned Ops | Product and Release | v1.2 |


