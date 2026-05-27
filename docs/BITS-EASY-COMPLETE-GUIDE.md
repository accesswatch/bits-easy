# BITS-EASY Complete Guide

BITS-EASY is built for one outcome: help you move through text work faster, safer, and with less mental load.

It is keyboard-first, NVDA-native, and designed so that beginners can succeed immediately while power users still feel unstoppable.

This guide is written as a practical magic system: every action should feel quick, understandable, and recoverable.

Key naming note:

1. `cmd.something` means a command ID you can run from the palette.
2. It does not mean a Command keyboard key.
3. Keyboard modifier naming in this project uses `Ctrl`.

## The Experience Promise

1. You are never lost. There is always a next command.
2. You are never trapped. Important actions keep clear recovery paths.
3. You are never blocked by memory. The system helps you recall what matters.
4. You are never forced into risky mode. Stable stays stable unless you explicitly opt into beta.

## First 10 Minutes

Use this once and you will understand the whole product rhythm.

1. Open the command palette with `cmd.palette.open`.
2. Run `cmd.help.availableHotkeys` to hear what works in your current app.
3. Capture one thought with `cmd.capture.quickInbox`.
4. Save one phrase in EASYText Studio so you can reuse it later.
5. Run one selection action such as summarize, extract actions, or beginner rewrite.

If that worked, you already have the core loop: discover, capture, transform, reuse.

## Core Capabilities

1. Selection and context actions across common text surfaces.
2. PocketClips for durable multi-slot clipboard workflows.
3. EASYText Studio for trigger-based phrase expansion.
4. Authoring support for Markdown and HTML.
5. Table capture with structured export paths.
6. Feature flag controls for staged rollout and beta governance.

## New in This Cycle

1. HTML assistant wizard actions: heading, paragraph, link, emailLink, list, table, image, title, toc.
2. Granular table capture commands: `cmd.table.capture.row`, `cmd.table.capture.column`, `cmd.table.capture.header`, `cmd.table.capture.cell`.
3. Emoji assistant commands: `cmd.emoji.list`, `cmd.emoji.insert`.
4. Runtime feature gate and authority controls for safer beta release.

## Fast Start for Beta Testers

1. Open palette with `cmd.palette.open`.
2. Run `cmd.feature.flags.list` to inspect available flags.
3. If authorized, run `cmd.feature.flags.grantBeta` with your access code.
4. Run `cmd.feature.flags.list` again and verify active beta features.
5. Explore `cmd.author.html.assistantList` and `cmd.emoji.list`.

## Daily Flow

### Start of day

1. Open notes and active work context.
2. Clear quick inbox into today-focused items.
3. Mark top priorities you want one-key access to.

### During work

1. Use selection commands on long text to reduce reading overhead.
2. Store repeated language in EASYText Studio.
3. Reuse PocketClips slots for rapid switching between snippets.
4. Capture tables when structured handoff is needed.

### End of day

1. Convert loose captures into named, reusable artifacts.
2. Summarize unfinished threads for fast restart tomorrow.
3. Keep rollback-safe outputs for anything high impact.

## Goal-Based Playbooks

### I need to remember this later

1. Capture with quick inbox immediately.
2. Add minimal context so future-you can trust it.
3. Route to a durable note category before ending session.

### I repeat this text every day

1. Save it to EASYText Studio.
2. Assign a clean trigger phrase.
3. Promote your best trigger to a primary one-step expansion.

### I need cleaner writing now

1. Use selection actions for rewrite and polish.
2. Use HTML assistant for structure rather than hand-coding fragments.
3. Validate accessibility before final publish.

### I am testing beta safely

1. Enable beta features in settings only when authorized.
2. Refresh flags when needed; confirm active state before testing.
3. Expect stable fallback behavior when network retrieval fails.

## Reliability and Safety

1. Feature checks run at command dispatch time.
2. Disabled or unauthorized commands are blocked with explicit reasons.
3. Related key bindings are removed before registration when a feature is off.
4. Offline fallback manifests preserve predictable behavior.

## What Makes It Feel Magical

1. You press less while getting more done.
2. The system surfaces what matters in your current context.
3. Reuse gets easier over time instead of harder.
4. Advanced power appears only when you are ready for it.

## User Contract

1. Stable-by-default behavior.
2. Explicit beta controls.
3. No silent failures.
4. One coherent documentation hub.
