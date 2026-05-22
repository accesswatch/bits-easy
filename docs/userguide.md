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

### 3.1 Installing Spellforge

1. Get the `spellforgeHotkeys` add-on file (it ends in `.nvda-addon`).
2. In NVDA, open **Tools**, then choose **Manage add-ons**.
3. Press **Install** and select the add-on file you downloaded.
4. Restart NVDA when it asks you to.

That is all there is to it. When NVDA comes back, you will hear a confirmation that Spellforge has loaded.

### 3.2 Checking That Everything Is Working

After NVDA restarts, try pressing `NVDA Key+Slash`. Spellforge will read out the hotkeys available to you. If you hear that list, you are up and running.

### 3.3 Adjusting Your Settings

You can find Spellforge's settings inside the NVDA Settings dialog — just look for the **Spellforge** panel. Here you can change:

- **Profile** — choose Beginner, Balanced, or Expert (see [Section 5](#5-choosing-a-profile) for what these mean).
- **Surface announcements** — whether Spellforge tells you which mode it is operating in.
- **Contextual fallback steps** — whether Spellforge offers alternative suggestions when a command cannot run as expected.
- **Command palette** — turn the palette on or off.
- **OS-level global hotkeys** — whether hotkeys work in all applications system-wide.
- **NVDA Key prefix emulation** — how the NVDA Key-based shortcuts are registered with Windows.
- **Multi-press gestures** — whether double-press and hold gestures are active.

---

## 4. 10-Minute Quick Start

Here are eight things to try right now, each taking about a minute:

1. Press `NVDA Key+Shift+P` to open the **command palette**. Type a word like "summarise" and press Enter to run a command.
2. Select some text in any application and press `NVDA Key+S` to **summarise** it.
3. With text selected, press `NVDA Key+1` to **save it to clip slot 1**.
4. Press `NVDA Key+2` to **paste it back** from slot 1.
5. Press `NVDA Key+Q` to **capture a quick note** to your inbox.
6. Press `NVDA Key+V` to **reopen the last result** in a navigable view.
7. Press `NVDA Key+Backspace` to **return to where you were** before Spellforge opened a view.
8. If anything feels stuck, press `NVDA Key+Escape` to **stop everything** immediately.

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

You can also press `NVDA Key+Slash` at any time to hear a spoken summary of available hotkeys.

If you want to see diagnostics — for example, to check whether a hotkey is registered correctly — press `NVDA Key+D`.

### 6.2 Working with Selected Text

Spellforge can act on text you have selected in any application.

- Press `NVDA Key+S` to get a **summary** of the selected text.
- Press `NVDA Key+A` to **extract action items** — useful for emails and meeting notes.
- Press `NVDA Key+R` to **rewrite** the text in simpler language.

If you want to mark a region manually (for example when your application does not support standard selection), use `NVDA Key+[` to mark the start and `NVDA Key+]` to mark the end. Press `NVDA Key+'` to hear a description of your current selection context, `NVDA Key+J` to jump back to where your selection started, and `NVDA Key+X` to clear the markers.

### 6.3 Clip Slots and the Clip Library

Clip slots let you save up to ten pieces of text and reuse them freely, even across applications.

- **Save to a slot:** Press `NVDA Key+1` (or 2 through 0 for other slots).
- **Paste from a slot:** Press `NVDA Key+2` (matching the slot number you used).
- **Hear what is in a slot:** Press `NVDA Key+4`.
- **Open the clip library:** Press `NVDA Key+6` to browse, organise, and manage saved clips in folders.

You can also combine clips using the **MergeBoard**. Set whether clips should be joined end-to-end or replace each other (`NVDA Key+M` for append, `NVDA Key+Shift+M` for replace), choose how they are separated (line, space, or paragraph), and then commit the merge when your stack is ready.

### 6.4 Reading Long Results

When Spellforge returns a long result — a summary, extracted actions, or a retrieval response — it opens a navigable virtual view so you can read through it at your own pace.

- **Open the latest result:** `NVDA Key+V`
- **Move to the next block:** `NVDA Key+RightArrow`
- **Move to the previous block:** `NVDA Key+LeftArrow`
- **Copy the current block:** `NVDA Key+C`
- **Copy everything:** `NVDA Key+Shift+C`
- **Search inside the result:** `NVDA Key+Control+F`
- **Check how confident Spellforge is:** `NVDA Key+K`
- **See alternative suggestions:** `NVDA Key+F`
- **Save the result to your inbox:** `NVDA Key+P`
- **Return to where you came from:** `NVDA Key+Backspace`

### 6.5 Quick Capture and Your Inbox

Press `NVDA Key+Q` any time to capture what you are thinking about or working on. It goes straight to your inbox so you can deal with it later. From the palette you can list inbox items and route them to the right place when you are ready.

Spellforge also keeps a journal of recent operations. If you need to undo something that was supported, you can roll it back from the palette.

### 6.6 Text Expansion

Build up a personal shorthand dictionary — type a short trigger and Spellforge expands it into the full phrase. You can create, list, and delete expansions from the palette. Press `NVDA Key+0` for a quick insert when you want to drop a saved piece of text directly into your work.

### 6.7 Shortcuts and the Launcher

Shortcuts let you jump to files, folders, websites, or applications with a single keypress. Press `NVDA Key+7` to open the shortcut launcher and run anything you have set up. Press `NVDA Key+9` to add the application you are currently using as a shortcut. `NVDA Key+8` lists any drive aliases you have mapped.

You can group shortcuts into categories and presets, and run a whole preset at once from the palette.

### 6.8 Tags, Tables, and Speech History

- **Tag your current session** for easy retrieval later: `NVDA Key+T`
- **Tag an Outlook message:** `NVDA Key+Shift+T`
- **Browse your speech history** — what NVDA has recently announced: `NVDA Key+H`
- **Open speech history as a navigable view:** `NVDA Key+Shift+H`
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

### 6.11 Diagnostics and Utilities

If something does not seem right, these tools can help:

- `NVDA Key+D` — run hotkey diagnostics to see what is registered and why.
- Open the palette and search "integration health" to check that Spellforge's components are all working.
- `NVDA Key+=` — search for a special character by name or description.
- `NVDA Key+-` — recall a recently used special character.
- `NVDA Key+W` — jump back to a bookmarked window. `NVDA Key+Shift+W` lists all your bookmarks.
- `NVDA Key+R` — open the system report.

---

## 7. Staying Safe

Spellforge is designed to give you confidence, not anxiety. Here is how it protects you:

- **Confirmations:** Actions that cannot be undone will ask before they run.
- **Previews:** When Spellforge is about to change something significant, it shows you what will happen first.
- **Fallback suggestions:** If a command cannot run in your current application, Spellforge offers alternatives rather than just failing silently.
- **Operation history:** Many actions are logged so you can review or roll back recent changes from the palette.
- **Emergency stop:** Press `NVDA Key+Escape` at any time to halt whatever is happening immediately.
- **Return to source:** Press `NVDA Key+Backspace` to close a virtual view and return to exactly where you were.

A simple rule of thumb: start on the **Beginner** profile while you are learning, move to **Balanced** for everyday use, and switch to **Expert** once the commands feel second nature.

---

## 8. Hotkey Reference

These are all the built-in hotkeys. The NVDA Key is the key you have set as your NVDA modifier — typically Insert or CapsLock.

| Hotkey | What it does |
|---|---|
| NVDA Key+0 | Quick insert saved text |
| NVDA Key+1 | Save to clip slot 1 |
| NVDA Key+2 | Paste from clip slot 1 |
| NVDA Key+3 | Delete clip slot |
| NVDA Key+4 | Describe clip slot |
| NVDA Key+5 | Open Shortcuts dashboard |
| NVDA Key+6 | Open clip library |
| NVDA Key+7 | Open shortcut launcher |
| NVDA Key+8 | List drive aliases |
| NVDA Key+9 | Add focused app to launcher |
| NVDA Key+A | Extract action items from selection |
| NVDA Key+B | Toggle speech density |
| NVDA Key+Backspace | Return to source |
| NVDA Key+C | Copy current result block |
| NVDA Key+[ | Mark selection start |
| NVDA Key+] | Mark selection end |
| NVDA Key+Control+F | Search inside current result |
| NVDA Key+D | Hotkey diagnostics |
| NVDA Key+= | Search for a symbol |
| NVDA Key+Escape | Emergency stop |
| NVDA Key+F | Open fallback suggestions |
| NVDA Key+H | Browse speech history |
| NVDA Key+I | Set merge divider to paragraph |
| NVDA Key+J | Jump to selection start |
| NVDA Key+K | Read confidence summary |
| NVDA Key+L | Set merge divider to line |
| NVDA Key+LeftArrow | Previous result block |
| NVDA Key+M | Set merge mode to append |
| NVDA Key+- | Recall recent symbol |
| NVDA Key+N | Toggle braille density |
| NVDA Key+P | Pin result to inbox |
| NVDA Key+Q | Quick capture to inbox |
| NVDA Key+' | Read selection context |
| NVDA Key+R | Rewrite selection in simpler language |
| NVDA Key+R | Open system report |
| NVDA Key+RightArrow | Next result block |
| NVDA Key+S | Summarise selection |
| NVDA Key+Shift+7 | Detect dialog insertion surface |
| NVDA Key+Shift+C | Copy full result |
| NVDA Key+Shift+H | Open speech history as virtual view |
| NVDA Key+Shift+M | Set merge mode to replace |
| NVDA Key+Shift+P | Open command palette |
| NVDA Key+Shift+T | Report tagged Outlook messages |
| NVDA Key+Shift+W | List window bookmarks |
| NVDA Key+Slash | What can I press? (hotkey help) |
| NVDA Key+Space (hold) | What can I press? (hotkey help) |
| NVDA Key+Space (double) | What can I press? (hotkey help) |
| NVDA Key+Space (triple) | Hotkey diagnostics |
| NVDA Key+T | Report tagged files |
| NVDA Key+U | Set merge divider to space |
| NVDA Key+V | Open latest result |
| NVDA Key+W | Recall window bookmark |
| NVDA Key+X | Cancel selection markers |

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
cmd.context.returnSource
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
cmd.db.delete
cmd.db.entry.add
cmd.db.entry.delete
cmd.db.entry.detail
cmd.db.entry.edit
cmd.db.entry.list
cmd.db.export.csv
cmd.db.export.text
cmd.db.field.define
cmd.db.restore
cmd.db.search
cmd.db.select
cmd.db.sort

[diary]
cmd.diary.create
cmd.diary.listMonth

[help]
cmd.help.availableHotkeys

[jamal]
cmd.jamal.export
cmd.jamal.import
cmd.jamal.launch
cmd.jamal.return
cmd.jamal.sync

[joplin]
cmd.joplin.export
cmd.joplin.import
cmd.joplin.mapping.set
cmd.joplin.refresh
cmd.joplin.refresh.rollback

[journal]
cmd.journal.list
cmd.journal.rollback

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
cmd.notes.category.create
cmd.notes.category.move
cmd.notes.field.set
cmd.notes.help.resolve
cmd.notes.help.set
cmd.notes.mode.set
cmd.notes.quickCapture
cmd.notes.relate
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
cmd.retrieve.revisit
cmd.retrieve.summarize

[selection]
cmd.selection.cancel
cmd.selection.extractActions
cmd.selection.jumpStart
cmd.selection.markEnd
cmd.selection.markStart
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

If you ever need to move to a new machine or reinstall, you can use the portability and backup commands from the palette to export and restore your complete setup — clips, shortcuts, workflow packs, and all.

---

## 11. If Something Goes Wrong

**A hotkey does not seem to do anything**
Open the palette with `NVDA Key+Shift+P` and check that the command you expect is listed. Then press `NVDA Key+D` to run hotkey diagnostics — it will tell you whether the key is registered and whether anything is conflicting.

**Spellforge is talking too much or not enough**
Try a different profile. Open NVDA Settings, go to the Spellforge panel, and switch between Beginner, Balanced, and Expert.

**A command says it cannot run in this application**
Press `NVDA Key+F` to see if there are alternative suggestions, or open the palette and search for a related command that works differently.

**Something got stuck or feels out of control**
Press `NVDA Key+Escape` immediately. That will stop whatever is running.

**You are not sure where you are**
Press `NVDA Key+Backspace` to return to where you started, or open the palette and search "where am I" for an orientation report.

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
