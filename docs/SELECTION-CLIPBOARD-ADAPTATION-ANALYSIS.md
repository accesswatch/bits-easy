# Baseline Selection and Clipboard Adaptation Analysis

## Purpose

This document provides an implementation-level adaptation strategy for Baseline selection, clips, and clipboard workflows, with explicit user experience upgrades for Magical 1.0.

## Scope

1. BaselineSelect equivalent capabilities.
2. BaselineClips equivalent capabilities.
3. Clipboard append and merge behavior.
4. Cross-app reliability strategy.
5. User experience upgrades beyond parity.

## Baseline Source Alignment

This analysis aligns with:

1. [docs/PRD-NVDA-Magical-Experience.md](docs/PRD-NVDA-Magical-Experience.md)
2. [docs/SPRINT-BACKLOG-EXECUTION.md](docs/SPRINT-BACKLOG-EXECUTION.md)
3. [docs/VIRTUALIZED-BROWSE-AND-HOTKEY-SPEC.md](docs/VIRTUALIZED-BROWSE-AND-HOTKEY-SPEC.md)
4. [docs/ENGINEERING-STARTER-PACK-VIRTUALIZED-HOTKEYS.md](docs/ENGINEERING-STARTER-PACK-VIRTUALIZED-HOTKEYS.md)

## Baseline to Spellforge Adaptation Matrix

| Baseline area | Parity target | Spellforge adaptation | Magical upgrade |
| --- | --- | --- | --- |
| BaselineSelect start and end markers | Full | SnapSpan marker state machine with adapter-backed range resolution | Context preview with size estimate and next-action suggestions |
| BaselineSelect context report | Full | Deterministic speech and braille summary for start and end snippets | Confidence-aware fallback suggestions when range quality is low |
| BaselineSelect jump back | Full | Source anchor plus marker restore token | Drift announcement and guided retry when exact restore fails |
| BaselineClips multi-slot copy and paste | Full | PocketClips fixed slots with typed metadata | Auto-label clips with source app and timestamp |
| BaselineClips protect and delete | Full | Slot protection policy and delete safeguards | One-step restore of last deleted slot |
| Clipboard append modes | Full | MergeBoard append or replace pipeline with profile-level settings | Profile presets by task type, including research and email digest |
| Divider and separator behavior | Full | Divider modes line, space, paragraph, custom | Adaptive separator suggestion by content class |
| Cross-app capture continuity | Partial to Full | Context provider and adapter capabilities per app class | Virtualized output handoff plus deterministic source return |

## Core UX Problems to Solve Better Than Baseline

1. Ambiguous selection state in complex app surfaces.
2. Clip slot uncertainty when users cannot remember what each slot contains.
3. Append output unpredictability when mixed sources are merged.
4. Silent or vague failures on unsupported contexts.
5. Context disorientation after command completion.

## Improvement Strategy by Problem

### 1) Selection certainty

Implementation:
1. Keep a session selection object with start marker, end marker, normalized range, and source anchor.
2. Resolve through app adapter first, with a bounded fallback chain.

UX behavior:
1. On end marker, always announce range summary with short context snippets.
2. If resolution is uncertain, offer explicit fallback options in one message.

### 2) Clip slot clarity

Implementation:
1. Persist slot metadata with source app, timestamp, length, and optional label.
2. Enforce protection checks before writes.

UX behavior:
1. Copy to slot announces slot number and short label.
2. Paste from slot announces source and age before insertion in beginner and balanced profiles.

### 3) Merge predictability

Implementation:
1. Central merge engine with strict preflight and profile-based mode rules.
2. Divider handling implemented as explicit policy, not ad hoc string concatenation.

UX behavior:
1. Merge summary before apply for long outputs.
2. Optional source tags to maintain provenance in research and email workflows.

### 4) Fallback quality

Implementation:
1. Adapter response includes capability and fallback list.
2. Command orchestrator never returns raw adapter errors directly to users.

UX behavior:
1. Unsupported context message always includes next step choices.
2. One-key route to open palette with best fallback command prefilled.

### 5) Context return confidence

Implementation:
1. Save source anchor before mutating actions and before virtualized return rendering.
2. Restore window focus, control focus, and selection in order.

UX behavior:
1. On successful return, concise confirmation.
2. On drift, explain nearest restored context and offer retry or manual return actions.

## Technical Implementation Model

## Service boundaries

1. Selection Service: marker lifecycle and normalized range assembly.
2. Clip Service: slot store and protection policy.
3. Merge Service: append and replace pipeline.
4. Context Service: app identity and capability envelope.
5. Feedback Service: speech and braille parity contracts.
6. Recovery Service: rollback tokens and action journal.

## Command families

1. Selection commands: mark start, mark end, announce context, jump to marker.
2. Clip commands: copy to slot, paste from slot, protect slot, unprotect slot, delete slot, edit slot.
3. Merge commands: set mode, set divider profile, set custom separator, merge now, clear on paste policy.

## Reliability design

1. Deterministic command path for all non-AI actions.
2. Bounded fallback chain per adapter class.
3. Command timeout and user-visible recovery hint.

## UX Profile Tuning

| Profile | Speech behavior | Confirmation behavior | Clipboard behavior |
| --- | --- | --- | --- |
| Beginner | Rich status and guidance | More confirmations for mutation | Announces slot details before paste |
| Balanced | Concise status plus confidence hints | Confirm for destructive or low-confidence actions | Announces minimal slot metadata |
| Expert | Minimal status | Confirm only for destructive actions | Fast insert, optional metadata on demand |

## Acceptance Criteria Additions

These criteria should be layered on top of existing E01 and E17 backlog tests.

1. Selection context announcement must include both semantic and positional cues.
2. Slot writes must be blocked by protection policy in all entry paths.
3. Merge output must be reproducible for identical inputs and profile settings.
4. Every unsupported context case must surface at least two actionable fallback options.
5. Return-to-source success and drift metrics must be logged and reportable.

## Metrics to Track

1. Selection resolution success rate by app.
2. Slot overwrite prevention events.
3. Merge operation rollback frequency.
4. Fallback invocation rate by command family.
5. Source return success versus drift ratio.

## Recommended Delivery Sequence

1. Finalize command-to-service contract for E01 selection and clips.
2. Implement slot metadata and protection semantics.
3. Implement merge profile determinism and source tagging.
4. Add fallback contract enforcement in orchestrator.
5. Add source-return drift diagnostics and profile-aware messaging.

## Summary

Parity with Baseline in these areas is feasible and already structurally planned. The key to a better user experience is not just feature parity, but deterministic state handling, transparent fallback behavior, profile-aware feedback, and trusted return-to-context behavior.
