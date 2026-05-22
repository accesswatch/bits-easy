# Spellforge User Guide

Welcome to Spellforge — a productivity add-on for NVDA that brings a powerful set of commands right to your fingertips, all without leaving the keyboard. This guide will walk you through everything you need to know, step by step, in plain language.

If you are new here, start with the [10-Minute Quick Start](#4-10-minute-quick-start). You can always come back to the other sections as you explore more.

---

## 1. What Is Spellforge?

Spellforge sits quietly alongside NVDA and gives you a set of keyboard shortcuts and tools you can use from any application on your computer. Think of it as a personal assistant that is always ready when you press the right key.

Here is a flavour of what you can do:

- **Open a command palette** — a searchable list of everything Spellforge can do, so you never have to memorise a hotkey to get started.
- **Work with text** — summarise, rewrite, or extract action items from anything you have selected.
- **Save and reuse text** — store clips in numbered slots and paste them back whenever you need them.
- **Capture ideas quickly** — press one key to save a thought to your inbox before it slips away.
- **Read long results comfortably** — navigate through structured output block by block at your own pace.
- **Stay safe** — Spellforge will ask before doing anything significant, and there is always an emergency stop if something feels wrong.

---

## 2. How Spellforge Works

You do not need to understand the internals to use Spellforge, but here is the short version if you are curious.

When you press a hotkey or choose a command from the palette, Spellforge looks at what application and text you are currently working with. It then runs the command at the right level of care — asking for confirmation when something is irreversible, and giving you a preview when the output is long. Results are announced through speech and braille, and anything you might want to revisit is available as a navigable virtual view.

---

## 3. Getting Started

### 3.0 Compatibility Requirements

Before you install Spellforge, confirm these requirements:

1. Windows 10 or 11, 64-bit.
2. NVDA 2026.1, 64-bit.
3. Spellforge `.nvda-addon` package.

For this release, support is intentionally limited to NVDA 2026.1 x64.

### 3.1 Installing Spellforge

1. Get the `spellforgeHotkeys` add-on file (it ends in `.nvda-addon`).
2. In NVDA, open **Tools**, then choose **Manage add-ons**.
3. Press **Install** and select the add-on file you downloaded.
4. Restart NVDA when it asks you to.

That is all there is to it. When NVDA comes back, you will hear a confirmation that Spellforge has loaded.

### 3.1.1 Optional Dependencies for Advanced Integrations

Most users do not need to install any extra libraries. If you use Google Calendar or Google Contacts integration features, install:

1. `google-api-python-client`
2. `google-auth`
3. `google-auth-oauthlib`
4. `google-auth-httplib2`

If you are not using those integrations, you can skip these packages.

### 3.1.2 Tester Quick Copy

Use this quick checklist when handing the add-on to a tester.

1. Confirm tester machine is Windows 10 or 11, 64-bit.
2. Confirm NVDA version is 2026.1, 64-bit.
3. Send the tester the Spellforge .nvda-addon file.
4. In NVDA, open Tools > Manage add-ons > Install.
5. Select the Spellforge .nvda-addon file and restart NVDA.
6. After restart, press Control+Alt+Slash.
7. If hotkeys are announced, installation passed.
8. If hotkeys are not announced, run Control+Alt+D for diagnostics and capture the spoken result.

Optional Google integration setup for testers who need Calendar or Contacts scenarios:

1. Install Python 3.13 x64.
2. Run: pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2

### 3.2 Checking That Everything Is Working

After NVDA restarts, try pressing `Control+Alt+Slash`. Spellforge will read out the hotkeys available to you. If you hear that list, you are up and running.

### 3.3 Adjusting Your Settings

You can find Spellforge's settings inside the NVDA Settings dialog — just look for the **Spellforge** panel. Here you can change:

- **Profile** — choose Beginner, Balanced, or Expert (see [Section 5](#5-choosing-a-profile) for what these mean).
- **Surface announcements** — whether Spellforge tells you which mode it is operating in.
- **Contextual fallback steps** — whether Spellforge offers alternative suggestions when a command cannot run as expected.
- **Command palette** — turn the palette on or off.
- **OS-level global hotkeys** — whether hotkeys work in all applications system-wide.
- **Control+Alt prefix emulation** — how the Control+Alt-based shortcuts are registered with Windows.
- **Multi-press gestures** — whether double-press and hold gestures are active.
- **Keyboard mappings editor** — edit command key chords and enabled state from a dedicated editor dialog.

You can open the keyboard mappings editor in two ways:

1. NVDA Settings > Spellforge > Edit keyboard mappings.
2. NVDA Tools menu > Spellforge keyboard mappings.

In the editor, turn on Advanced mode if you need to change scope, app override target, or trigger kind.

Use Run NVDA gesture scrub in the editor to detect:

1. Internal collisions between Spellforge bindings.
2. Potential collisions with known NVDA gestures.

### 3.4 Spellforge Key Model

Spellforge includes a dedicated Spellforge key chord for helper actions.

1. Primary model: Control+Alt based hotkeys (for example Control+Alt+S, Control+Alt+Q).
2. Dedicated Spellforge helper key: Control+Alt+Space (single, double, triple, and hold variants).
3. OS hook compatibility model: CapsLock prefix can be emulated as Control+Alt for registration.

This avoids base NVDA gesture conflicts while still giving a single Spellforge-oriented entry point similar to a leader key workflow.

---

## 4. 10-Minute Quick Start

Here are eight things to try right now, each taking about a minute:

1. Press `NVDA Key+Shift+P` to open the **command palette**. Type a word like "summarise" and press Enter to run a command.
2. Select some text in any application and press `Control+Alt+S` to **summarise** it.
3. With text selected, press `Control+Alt+1` to **save it to clip slot 1**.
4. Press `Control+Alt+2` to **paste it back** from slot 1.
5. Press `Control+Alt+Q` to **capture a quick note** to your inbox.
6. Press `Control+Alt+V` to **reopen the last result** in a navigable view.
7. Press `Control+Alt+Backspace` to **return to where you were** before Spellforge opened a view.
8. If anything feels stuck, press `Control+Alt+Escape` to **stop everything** immediately.

---

## 5. Choosing a Profile

Spellforge has three built-in profiles that control how much it talks, how often it asks for confirmation, and how quickly it acts. You can switch at any time from the settings panel.

**Beginner**
Spellforge explains more, asks before doing most things, and gives you previews so you always know what is about to happen. This is the best place to start.

**Balanced**
A good everyday setting. Output is concise, Spellforge only asks when it really needs to, and previews appear for longer operations.

**Expert**
Minimal speech, fast execution, and fewer prompts. Ideal once you know the commands well and want to move quickly.

You can change your profile at any time — your commands stay the same, only the level of guidance changes.

---

## 6. What You Can Do — Feature by Feature

### 6.1 The Command Palette

If you ever forget a hotkey, the palette is your starting point. Press `NVDA Key+Shift+P` to open it, type a word or two describing what you want to do, and press Enter to run the matching command.

You can also press `Control+Alt+Slash` at any time to hear a spoken summary of available hotkeys.

If you want to see diagnostics — for example, to check whether a hotkey is registered correctly — press `Control+Alt+D`.

AI commands in the palette are context-aware:

- AI setup and status commands stay visible so you can always configure or check AI.
- Selection-driven AI commands appear when Spellforge has selection context and an AI key is configured.

### 6.2 Working with Selected Text

Spellforge can act on text you have selected in any application.

- Press `Control+Alt+S` to get a **summary** of the selected text.
- Press `Control+Alt+A` to **extract action items** — useful for emails and meeting notes.
- Press `Control+Alt+R` to **rewrite** the text in simpler language.

When an AI key is configured, Spellforge can attach optional AI augmentation to these selection workflows while preserving the deterministic primary result.

If you want to mark a region manually (for example when your application does not support standard selection), use `Control+Alt+[` to mark the start and `Control+Alt+]` to mark the end. Press `Control+Alt+'` to hear a description of your current selection context, `Control+Alt+;` to hear marker status and cross-surface drift hints, `Control+Alt+J` to jump back to where your selection started, and `Control+Alt+X` to clear the markers.

From the palette you can also run `cmd.selection.markerStatus` to hear whether start and end markers are set and whether a usable range is already cached.

### 6.3 Clip Slots and the Clip Library

Clip slots let you save up to ten pieces of text and reuse them freely, even across applications.

- **Save to a slot:** Press `Control+Alt+1` (or 2 through 0 for other slots).
- **Paste from a slot:** Press `Control+Alt+2` (matching the slot number you used).
- **Hear what is in a slot:** Press `Control+Alt+4`.
- **Open the clip library:** Press `Control+Alt+6` to browse, organise, and manage saved clips in folders.

You can also combine clips using the **MergeBoard**. Set whether clips should be joined end-to-end or replace each other (`Control+Alt+M` for append, `Control+Alt+Shift+M` for replace), choose how they are separated (line, space, or paragraph), and then commit the merge when your stack is ready.

From the palette, advanced PocketClips workflows now include search in slot browser (`cmd.clip.browser.search`), pin or unpin favorite slots via batch action (`action=pin` or `action=unpin`), clip category assignment (`cmd.clip.library.assignCategory`), and alias conflict handling strategy for retained slot aliases (`aliasStrategy=rename|replace|reject`).

### 6.4 Reading Long Results

When Spellforge returns a long result — a summary, extracted actions, or a retrieval response — it opens a navigable virtual view so you can read through it at your own pace.

- **Open the latest result:** `Control+Alt+V`
- **Move to the next block:** `Control+Alt+RightArrow`
- **Move to the previous block:** `Control+Alt+LeftArrow`
- **Copy the current block:** `Control+Alt+C`
- **Copy everything:** `Control+Alt+Shift+C`
- **Search inside the result:** `Control+Alt+Control+F`
- **Check how confident Spellforge is:** `Control+Alt+K`
- **See alternative suggestions:** `Control+Alt+F`
- **Save the result to your inbox:** `Control+Alt+P`
- **Return to where you came from:** `Control+Alt+Backspace`

### 6.5 Quick Capture and Your Inbox

Press `Control+Alt+Q` any time to capture what you are thinking about or working on. It goes straight to your inbox so you can deal with it later. From the palette you can list inbox items and route them to the right place when you are ready.

When AI is configured, quick capture can include optional AI augmentation (for example a compact summary suggestion) without changing the base capture output.

Spellforge also keeps a journal of recent operations. If you need to undo something that was supported, you can roll it back from the palette.

### 6.6 Text Expansion

Build up a personal shorthand dictionary — type a short trigger and Spellforge expands it into the full phrase. You can create, list, and delete expansions from the palette. Press `Control+Alt+0` for a quick insert when you want to drop a saved piece of text directly into your work.

### 6.7 Shortcuts and the Launcher

Shortcuts let you jump to files, folders, websites, or applications with a single keypress. Press `Control+Alt+7` to open the shortcut launcher and run anything you have set up. Press `Control+Alt+9` to add the application you are currently using as a shortcut. `Control+Alt+8` lists any drive aliases you have mapped.

You can group shortcuts into categories and presets, and run a whole preset at once from the palette.

### 6.8 Tags, Tables, and Speech History

- **Tag your current session** for easy retrieval later: `Control+Alt+T`
- **Tag an Outlook message:** `Control+Alt+Shift+T`
- **Browse your speech history** — what NVDA has recently announced: `Control+Alt+H`
- **Open speech history as a navigable view:** `Control+Alt+Shift+H`
- **Capture a table** from an application into Spellforge: use the palette and search "table capture."

### 6.9 Tasks, Time, Diary, Contacts, and More

Spellforge has a full personal workflow suite you can access from the palette:

- **Tasks:** Create, list, and mark tasks complete. Export to a calendar file or sync with Google Calendar.
- **Time tools:** Speak the current time, insert a timestamp, run a stopwatch or countdown, and set alarms.
- **Diary:** Write and list diary entries by month.
- **Contacts:** Create, search, and sync contacts. Insert or copy individual fields.
- **Mail helpers:** Extract the sender from an email or take action on attachments.

### 6.10 Notes, Authoring, and Retrieval

- **Quick capture a note:** Use the palette and search "quick capture note."
- **Organise notes** with categories, custom fields, and relations.
- **Author content** in Markdown or HTML, with built-in accessibility checking.
- **Retrieve information** — query, parse, summarise, and revisit results.
- **Structured records:** Define fields, manage entries, search, sort, and export to text or CSV.
- **Joplin and Jamal integration:** Import, export, and sync notes with your preferred note app.
- **Workflow packs:** Export and import your entire workflow setup so you can take it with you.

When AI is configured, note quick capture and note help text workflows can include optional AI rewrite augmentation while keeping the original note pipeline unchanged.

### 6.12 AI Keys and Storage Diagnostics

Spellforge supports AI provider keys, including Llama Cloud.

Use these commands from the palette:

- `cmd.ai.key.set` - set or update a provider key.
- `cmd.ai.key.status` - check whether keys are configured.
- `cmd.ai.key.storeStatus` - report which key storage backend is active.

Key storage behavior:

1. On Windows, Spellforge stores provider keys in Windows Credential Manager when available.
2. Provider keys are not persisted in plain JSON state files.
3. If secure storage is unavailable, Spellforge falls back safely and reports the backend through `cmd.ai.key.storeStatus`.

When you run `cmd.ai.key.storeStatus`, Spellforge speaks a plain-language summary that includes backend, security/persistence mode, and configured provider count.

### 6.11 Diagnostics and Utilities

If something does not seem right, these tools can help:

- `Control+Alt+D` — run hotkey diagnostics to see what is registered and why.
- Open the palette and search "integration health" to check that Spellforge's components are all working.
- `Control+Alt+=` — search for a special character by name or description.
- `Control+Alt+-` — recall a recently used special character.
- `Control+Alt+W` — jump back to a bookmarked window. `Control+Alt+Shift+W` lists all your bookmarks.
- `Control+Alt+R` — open the system report.

---

## 7. Staying Safe

Spellforge is designed to give you confidence, not anxiety. Here is how it protects you:

- **Confirmations:** Actions that cannot be undone will ask before they run.
- **Previews:** When Spellforge is about to change something significant, it shows you what will happen first.
- **Fallback suggestions:** If a command cannot run in your current application, Spellforge offers alternatives rather than just failing silently.
- **Operation history:** Many actions are logged so you can review or roll back recent changes from the palette.
- **Emergency stop:** Press `Control+Alt+Escape` at any time to halt whatever is happening immediately.
- **Return to source:** Press `Control+Alt+Backspace` to close a virtual view and return to exactly where you were.

A simple rule of thumb: start on the **Beginner** profile while you are learning, move to **Balanced** for everyday use, and switch to **Expert** once the commands feel second nature.

---

## 8. Hotkey Reference

These are all the built-in hotkeys. The NVDA Key is the key you have set as your NVDA modifier — typically Insert or CapsLock.

| Hotkey | What it does |
|---|---|
| Control+Alt+0 | Quick insert saved text |
| Control+Alt+1 | Save to clip slot 1 |
| Control+Alt+2 | Paste from clip slot 1 |
| Control+Alt+3 | Delete clip slot |
| Control+Alt+4 | Describe clip slot |
| Control+Alt+5 | Open Shortcuts dashboard |
| Control+Alt+6 | Open clip library |
| Control+Alt+7 | Open shortcut launcher |
| Control+Alt+8 | List drive aliases |
| Control+Alt+9 | Add focused app to launcher |
| Control+Alt+A | Extract action items from selection |
| Control+Alt+B | Toggle speech density |
| Control+Alt+Backspace | Return to source |
| Control+Alt+C | Copy current result block |
| Control+Alt+[ | Mark selection start |
| Control+Alt+] | Mark selection end |
| Control+Alt+Control+F | Search inside current result |
| Control+Alt+D | Hotkey diagnostics |
| Control+Alt+= | Search for a symbol |
| Control+Alt+Escape | Emergency stop |
| Control+Alt+F | Open fallback suggestions |
| Control+Alt+H | Browse speech history |
| Control+Alt+I | Set merge divider to paragraph |
| Control+Alt+J | Jump to selection start |
| Control+Alt+K | Read confidence summary |
| Control+Alt+L | Set merge divider to line |
| Control+Alt+LeftArrow | Previous result block |
| Control+Alt+M | Set merge mode to append |
| Control+Alt+- | Recall recent symbol |
| Control+Alt+N | Toggle braille density |
| Control+Alt+P | Pin result to inbox |
| Control+Alt+Q | Quick capture to inbox |
| Control+Alt+' | Read selection context |
| Control+Alt+; | Read selection marker status |
| Control+Alt+R | Rewrite selection in simpler language |
| Control+Alt+Shift+R | Open system report |
| Control+Alt+RightArrow | Next result block |
| Control+Alt+S | Summarise selection |
| Control+Alt+Shift+7 | Detect dialog insertion surface |
| Control+Alt+Shift+C | Copy full result |
| Control+Alt+Shift+H | Open speech history as virtual view |
| Control+Alt+Shift+M | Set merge mode to replace |
| NVDA Key+Shift+P | Open command palette |
| Control+Alt+Shift+T | Report tagged Outlook messages |
| Control+Alt+Shift+W | List window bookmarks |
| Control+Alt+Slash | What can I press? (hotkey help) |
| Control+Alt+Space | Open command palette |
| Control+Alt+Space (hold) | What can I press? (hotkey help) |
| Control+Alt+Space (double) | What can I press? (hotkey help) |
| Control+Alt+Space (triple) | Hotkey diagnostics |
| Control+Alt+T | Report tagged files |
| Control+Alt+U | Set merge divider to space |
| Control+Alt+V | Open latest result |
| Control+Alt+W | Recall window bookmark |
| Control+Alt+X | Cancel selection markers |

---

## 9. All Available Commands

Below is the complete list of commands you can access from the palette. You do not need to memorise these — just open the palette with `NVDA Key+Shift+P` and type a word or two to find what you need.

```text
[author]
cmd.author.a11y.fixPreview
cmd.author.a11y.lint
cmd.author.export.html
cmd.author.export.word
cmd.author.html.semantic
cmd.author.html.validate
cmd.author.markdown.insert

[backup]
cmd.backup.migrate
cmd.backup.selected.run
cmd.backup.settings.create
cmd.backup.settings.restore
cmd.backup.source.add
cmd.backup.target.set

[capture]
cmd.capture.quickInbox
cmd.capture.quickInbox.list
cmd.capture.quickInbox.route

[ai]
cmd.ai.billingStatus
cmd.ai.doc.ask
cmd.ai.doc.followUp
cmd.ai.doc.upload
cmd.ai.image.generate
cmd.ai.key.delete
cmd.ai.key.set
cmd.ai.key.status
cmd.ai.key.storeStatus
cmd.ai.prompt.create
cmd.ai.prompt.delete
cmd.ai.prompt.insert
cmd.ai.prompt.list
cmd.ai.session.clear
cmd.ai.session.delete
cmd.ai.session.list
cmd.ai.session.load
cmd.ai.session.new
cmd.ai.session.save
cmd.ai.tool.run
cmd.ai.transcribe

[clip]
cmd.clip.browser.batchAction
cmd.clip.browser.compare
cmd.clip.browser.exportPack
cmd.clip.browser.filter
cmd.clip.browser.importPack
cmd.clip.browser.merge
cmd.clip.browser.open
cmd.clip.browser.reorder
cmd.clip.browser.sort
cmd.clip.browser.split
cmd.clip.copyToSlot
cmd.clip.deleteSlot
cmd.clip.describeSlot
cmd.clip.editSlot
cmd.clip.library.createFolder
cmd.clip.library.deleteFolder
cmd.clip.library.ingestSlot
cmd.clip.library.linkToFolder
cmd.clip.library.listLinkedLocations
cmd.clip.library.moveToFolder
cmd.clip.library.open
cmd.clip.library.renameFolder
cmd.clip.library.restoreToSlot
cmd.clip.library.retainSlotAlias
cmd.clip.library.setRetentionPolicy
cmd.clip.library.timeline
cmd.clip.pasteFromSlot
cmd.clip.protectSlot
cmd.clip.unprotectSlot

[contacts]
cmd.contacts.copyField
cmd.contacts.create
cmd.contacts.insertField
cmd.contacts.search
cmd.contacts.syncGoogle

[context]
cmd.context.capabilityEnvelope
cmd.context.returnSource
cmd.context.returnSourceDriftSafe
cmd.context.whereAmI

[cuts]
cmd.cuts.assignCategory
cmd.cuts.create
cmd.cuts.createPreset
cmd.cuts.dashboard
cmd.cuts.delete
cmd.cuts.exportPresets
cmd.cuts.importPresets
cmd.cuts.launch
cmd.cuts.list
cmd.cuts.runPreset

[date]
cmd.date.addDays
cmd.date.dayOfWeek
cmd.date.insert

[db]
cmd.db.create
cmd.db.dashboard
cmd.db.delete
cmd.db.entry.add
cmd.db.entry.delete
cmd.db.entry.detail
cmd.db.entry.edit
cmd.db.entry.grid
cmd.db.entry.list
cmd.db.export.csv
cmd.db.export.json
cmd.db.export.text
cmd.db.field.define
cmd.db.list
cmd.db.restore
cmd.db.search
cmd.db.search.advanced
cmd.db.select
cmd.db.sort
cmd.db.template.apply

[diary]
cmd.diary.create
cmd.diary.listMonth

[file]
cmd.file.browse
cmd.file.copy
cmd.file.delete
cmd.file.move
cmd.file.path.copy
cmd.file.rename
cmd.file.tag.batch
cmd.file.zip.create

[help]
cmd.help.availableHotkeys

[jamal]
cmd.jamal.export
cmd.jamal.import
cmd.jamal.launch
cmd.jamal.return
cmd.jamal.sync
cmd.jamal.sync.applyPlan
cmd.jamal.sync.plan
cmd.jamal.sync.rollback

[joplin]
cmd.joplin.export
cmd.joplin.import
cmd.joplin.mapping.set
cmd.joplin.refresh
cmd.joplin.refresh.rollback

[journal]
cmd.journal.list
cmd.journal.rollback
cmd.journal.trends

[mail]
cmd.mail.attachments.action
cmd.mail.extractSender

[merge]
cmd.merge.applyProfile
cmd.merge.commit
cmd.merge.setCustomSeparator
cmd.merge.setDividerLine
cmd.merge.setDividerParagraph
cmd.merge.setDividerSpace
cmd.merge.setModeAppend
cmd.merge.setModeReplace
cmd.merge.toggleClearOnPaste

[missions]
cmd.missions.complete
cmd.missions.start
cmd.missions.status

[notes]
cmd.notes.attachment.add
cmd.notes.attachment.action
cmd.notes.backup.export
cmd.notes.backup.restore
cmd.notes.category.create
cmd.notes.category.move
cmd.notes.category.tree
cmd.notes.field.set
cmd.notes.help.resolve
cmd.notes.help.set
cmd.notes.mode.set
cmd.notes.quickCapture
cmd.notes.relate
cmd.notes.related.graph
cmd.notes.snapshot.create
cmd.notes.snapshot.restore

[nvda]
cmd.nvda.readiness.api
cmd.nvda.readiness.baseline
cmd.nvda.readiness.security

[palette]
cmd.palette.open

[profile]
cmd.profile.hotkeyChainCreate
cmd.profile.hotkeyChainList
cmd.profile.hotkeyChainRun
cmd.profile.hotkeyDiagnostics
cmd.profile.hotkeyPresetExport
cmd.profile.hotkeyPresetImport
cmd.profile.integrationHealth
cmd.profile.portabilityBackup
cmd.profile.portabilityRestore

[result]
cmd.result.block.copy
cmd.result.block.next
cmd.result.block.previous
cmd.result.copyAll
cmd.result.openFallbacks
cmd.result.pinInbox
cmd.result.readConfidence
cmd.result.search
cmd.result.toggleBrailleDensity
cmd.result.toggleSpeechDensity
cmd.result.virtualOpen

[retrieve]
cmd.retrieve.parse
cmd.retrieve.query
cmd.retrieve.anchor.set
cmd.retrieve.revisit
cmd.retrieve.summarize
cmd.retrieve.trail.open
cmd.retrieve.trail.return
cmd.retrieve.visited.report

[selection]
cmd.selection.cancel
cmd.selection.extractActions
cmd.selection.jumpStart
cmd.selection.markEnd
cmd.selection.markStart
cmd.selection.markerStatus
cmd.selection.readContext
cmd.selection.rewriteBeginner
cmd.selection.summarize

[shortcuts]
cmd.shortcuts.assignCategory
cmd.shortcuts.create
cmd.shortcuts.createPreset
cmd.shortcuts.dialog.detect
cmd.shortcuts.dialog.insertPath
cmd.shortcuts.drive.list
cmd.shortcuts.drive.map
cmd.shortcuts.drive.unmap
cmd.shortcuts.launcher.add
cmd.shortcuts.launcher.addFocusedApp
cmd.shortcuts.launcher.open
cmd.shortcuts.launcher.remove
cmd.shortcuts.launcher.restoreDefaults
cmd.shortcuts.list
cmd.shortcuts.runPreset

[social]
cmd.social.nickname.replace
cmd.social.nickname.upsert
cmd.social.notifications.set
cmd.social.orbit.summary

[speech]
cmd.speech.history.browse
cmd.speech.history.capture
cmd.speech.history.copyItem
cmd.speech.history.copyRange
cmd.speech.history.virtualView

[system]
cmd.system.emergencyStop

[table]
cmd.table.capture
cmd.table.capture.clearBuffer
cmd.table.capture.exportClipboard

[tags]
cmd.tags.outlook.batchCopy
cmd.tags.outlook.batchDelete
cmd.tags.outlook.batchMove
cmd.tags.outlook.cancel
cmd.tags.outlook.report
cmd.tags.outlook.tag
cmd.tags.outlook.untag
cmd.tags.session.batchCopy
cmd.tags.session.batchCut
cmd.tags.session.batchDelete
cmd.tags.session.batchPlaylistAdd
cmd.tags.session.cancel
cmd.tags.session.count
cmd.tags.session.report
cmd.tags.session.tag
cmd.tags.session.untag

[tasks]
cmd.tasks.complete
cmd.tasks.create
cmd.tasks.exportIcs
cmd.tasks.list
cmd.tasks.syncGoogleCalendar

[text]
cmd.text.expansion.delete
cmd.text.expansion.expand
cmd.text.expansion.list
cmd.text.expansion.rename
cmd.text.expansion.setPrimary
cmd.text.expansion.upsert
cmd.text.quickInsert

[time]
cmd.time.alarm.cancel
cmd.time.alarm.set
cmd.time.alarm.status
cmd.time.countdown.start
cmd.time.countdown.status
cmd.time.countdown.stop
cmd.time.insert
cmd.time.monitor.start
cmd.time.monitor.status
cmd.time.monitor.stop
cmd.time.speak
cmd.time.speakSeconds
cmd.time.stopwatch.clear
cmd.time.stopwatch.elapsed
cmd.time.stopwatch.setPrecision
cmd.time.stopwatch.start
cmd.time.stopwatch.stop

[utility]
cmd.utility.audio.cycleCard
cmd.utility.audio.restoreBalance
cmd.utility.audio.split
cmd.utility.notifications.import
cmd.utility.notifications.restore
cmd.utility.progressCues.plan
cmd.utility.symbol.insertByCode
cmd.utility.symbol.recent
cmd.utility.symbol.search
cmd.utility.systemReport.export
cmd.utility.systemReport.open
cmd.utility.windowBookmark.assign
cmd.utility.windowBookmark.list
cmd.utility.windowBookmark.recall
cmd.utility.windowBookmark.rename

[whatsapp]
cmd.whatsapp.recent
cmd.whatsapp.voice

[workflow]
cmd.workflow.pack.export
cmd.workflow.pack.import

[x]
cmd.x.timeline
```

---

## 10. Your Data and Portability

Spellforge saves your clips, settings, palette history, and other personal data to a folder under your Windows user profile (usually in AppData\Spellforge). Everything stays on your own computer.

AI provider keys are handled separately from regular JSON state. When available, Spellforge stores them in Windows Credential Manager. Use `cmd.ai.key.storeStatus` to confirm the active key storage backend on your system.

If you ever need to move to a new machine or reinstall, you can use the portability and backup commands from the palette to export and restore your complete setup — clips, shortcuts, workflow packs, and all.

---

## 11. If Something Goes Wrong

**A hotkey does not seem to do anything**
Open the palette with `NVDA Key+Shift+P` and check that the command you expect is listed. Then press `Control+Alt+D` to run hotkey diagnostics — it will tell you whether the key is registered and whether anything is conflicting.

**Spellforge is talking too much or not enough**
Try a different profile. Open NVDA Settings, go to the Spellforge panel, and switch between Beginner, Balanced, and Expert.

**A command says it cannot run in this application**
Press `Control+Alt+F` to see if there are alternative suggestions, or open the palette and search for a related command that works differently.

**Something got stuck or feels out of control**
Press `Control+Alt+Escape` immediately. That will stop whatever is running.

**You are not sure where you are**
Press `Control+Alt+Backspace` to return to where you started, or open the palette and search "where am I" for an orientation report.

---

## 12. Building Up Your Skills

There is no pressure to learn everything at once. Here is a gentle week-by-week path if you want one:

- **Day 1:** Get comfortable with the palette and hotkey help. Try quick capture and text summarise.
- **Day 2:** Explore clip slots and the virtual result view.
- **Day 3:** Set up a few text expansions and try the merge modes.
- **Day 4:** Use the tasks, diary, and time tools for your daily planning.
- **Day 5:** Explore notes and the retrieval tools.
- **Day 6:** Set up shortcuts and try the tagging features.
- **Day 7:** Look at backup and portability so your setup is protected.

Once you can open the palette, capture a thought, save and reuse a clip, and run one daily planning command — you are already getting real value from Spellforge. Everything else is there when you are ready for it.
