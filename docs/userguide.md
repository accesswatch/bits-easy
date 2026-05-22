# Spellforge User Guide

Welcome. Spellforge is a calm, keyboard-first companion for NVDA. It listens for one friendly key chord, helps you do useful things with selected text and your clipboard, and gently keeps your work safe and reversible across every application you use.

This guide is written to be read in order the first time. After that, jump to any section you need. Nothing here assumes prior experience with Spellforge.

If you only have ten minutes, read sections 1 - 4. If you have an afternoon, read everything. You will not need to memorise commands - Spellforge will tell you what is available whenever you ask.

---

## 1. What Spellforge Is

Spellforge sits quietly alongside NVDA. It does not change how NVDA reads the screen and it does not take over the keyboard. It adds:

1. One Spellforge key chord that is always ready to help.
2. A small set of trustworthy hotkeys for daily work.
3. A searchable command palette for everything else.
4. Selection and clipboard tools that work across applications.
5. A virtualized reading surface for long results.
6. Optional AI augmentation that never replaces your deterministic results.
7. Safe recovery, previews, and an emergency stop you can rely on.

Spellforge keeps your data on your computer. AI provider keys, when you choose to add them, live in secure storage that you can verify at any time.

---

## 2. Installing Spellforge

### 2.1 Requirements

1. Windows 10 or Windows 11, 64-bit.
2. NVDA 2026.1, 64-bit.
3. The Spellforge `.nvda-addon` package.

### 2.2 Install steps

1. In NVDA, open `Tools` and choose `Manage add-ons`.
2. Press `Install` and select the Spellforge `.nvda-addon` file.
3. Restart NVDA when prompted.
4. When NVDA returns, Spellforge announces `Spellforge loaded`.

### 2.3 First-run check

Press `Control+Alt+Slash`. Spellforge will read a short summary of what you can press right now. If you hear that summary, the add-on is working.

### 2.4 Optional integrations

Most workflows need nothing extra. Install these only if you intend to use Google Calendar or Google Contacts:

1. `google-api-python-client`
2. `google-auth`
3. `google-auth-oauthlib`
4. `google-auth-httplib2`

---

## 3. Choose Your Profile

Spellforge has three profiles. They change how much it talks, how often it confirms, and how quickly it acts. Your commands and hotkeys stay the same in every profile.

1. **Beginner.** Friendly explanations, more previews, explicit confirmations. The kindest starting point.
2. **Balanced.** Concise feedback, confirmations only when something matters. The most common everyday choice.
3. **Expert.** Minimal speech, fastest action, fewest prompts. Choose this when commands feel second nature.

Open `NVDA Settings` and find the `Spellforge` panel to switch profiles, toggle multi-press gestures, choose whether OS-level global hotkeys are active, and open the keyboard mappings editor.

You can change profile any time. Your saved clips, notes, and workflows are unaffected.

---

## 4. The Spellforge Key: Your Magical Door

Before anything else, learn one chord: `NVDA Key+Space` (internally shown as `CapsLock+Space` or `Control+Alt+Space` depending on layout). This is the Spellforge key. You can press it from almost any application and it will do the right thing for the way you press it.

| How you press it | What happens |
| --- | --- |
| Single press | Opens the command palette so you can search every Spellforge command in plain language. |
| Double press | Reads `What can I press` - a concise list of hotkeys available right now. |
| Triple press | Opens hotkey diagnostics so you can see what is registered and whether anything is conflicting. |
| Press and hold | Reads `What can I press` in a calmer, more guided form. |

This is the magic Spellforge promises:

1. You never have to remember everything.
2. One key tells you what you can do.
3. The same key lets you ask for anything by name.
4. The same key shows you the truth when something feels wrong.

If you ever feel lost, press `NVDA Key+Space` twice. Spellforge will tell you what you can press from where you are.

### 4.1 LEASEY-style help layers

Spellforge now follows a layered help rhythm similar to classic screen reader companion manuals:

1. **Layer 1 (Do).** Single press opens the palette and runs commands fast.
2. **Layer 2 (Discover).** Double press reads what is available in this surface.
3. **Layer 3 (Diagnose).** Triple press explains collisions and fallback routing.
4. **Layer 4 (Guide).** Press-and-hold gives calm spoken help for newer users.

### 4.2 Companion helpers

These three keys travel alongside the Spellforge key and never change meaning:

1. `Control+Alt+Slash` - read available hotkeys for the current surface.
2. `Control+Alt+D` - open hotkey diagnostics.
3. `Control+Alt+Escape` - emergency stop. Spellforge halts whatever it was doing and returns you to a quiet state.

You can use these from any application. They never modify your files or change focus permanently.

---

## 5. Selection Magic Across Applications

Spellforge treats selected text as a first-class object. It understands native selections, marker-based selections you set yourself, and cross-app drift when a selection moves between programs.

### 5.1 The simple path

If your application supports normal selection (Outlook, Word, Notepad, Edge, Firefox, Chrome, VS Code, and most editors), select text the usual way. Then choose one:

1. `Control+Alt+S` - summarise the selection.
2. `Control+Alt+A` - extract action items.
3. `Control+Alt+R` - rewrite for beginners (with a preview before applying).
4. `Control+Alt+1` - save the selection to clip slot 1.

Spellforge will announce a short, friendly result, and offer a virtualized view if the output is long.

### 5.2 When the application is unfriendly

Some surfaces are not selection-friendly. Spellforge gives you a deterministic marker workflow instead:

1. `Control+Alt+[` - mark the start of your range.
2. `Control+Alt+]` - mark the end of your range.
3. `Control+Alt+'` - read the start and end snippets with confidence.
4. `Control+Alt+;` - read marker status and any drift hints.
5. `Control+Alt+J` - jump back to the start marker.
6. `Control+Alt+X` - cancel markers cleanly.

Once your range is set, every selection command above behaves exactly the same as if you had used native selection.

### 5.4 Start-arrow-end flow (fast selection)

This is the high-speed workflow for large text:

1. Press `Control+Alt+[` to set start.
2. Use only arrow keys to move to the end.
3. Press `Control+Alt+]` to capture the range.
4. Run normal selection actions (`Control+Alt+S`, `Control+Alt+A`, `Control+Alt+R`).

Marker-captured ranges are now treated as first-class selection for those actions.

### 5.3 What every app feels like

Spellforge tunes its behavior for the application you are in:

1. **Outlook.** Summarise long threads, extract action items, draft a reply from selection, tag a message, batch-copy, batch-move, batch-delete, and report tagged messages. Try `Control+Alt+S` on a thread, then `Control+Alt+Shift+T` to tag it.
2. **Word.** Rewrite for beginners with preview and rollback, summarise a section, capture a passage to a clip slot, and extract action items from a meeting note. Mutating commands always preview first.
3. **Notepad.** Quick capture is instant. Slot operations work even when Notepad has no rich selection. Selection markers cover any awkward range you cannot select natively.
4. **Edge, Chrome, Firefox.** Page-wide selection, paragraph capture, heading-block fallback, source-tagged merge into the active MergeBoard. If selection is hard, the fallback menu suggests `paragraph`, `heading block`, or `guided capture`.
5. **VS Code.** Selection survives moving between editor and terminal. Slot copy and paste preserve indentation. Markdown and HTML authoring helpers (see section 11) produce content that pastes cleanly back in.
6. **Other applications.** If a command cannot run safely in the current surface, Spellforge offers alternatives instead of failing silently. Press `Control+Alt+F` to see them.

### 5.4 If a selection drifts

When focus moves and your selection markers no longer match the document, Spellforge does not pretend. It announces the drift, suggests the nearest valid restore point, and lets you choose:

1. Keep the existing range and continue.
2. Re-mark the range at the nearest valid anchor.
3. Cancel markers and start over.

You will never be left guessing where your selection went.

---

## 6. Clipboard Magic: PocketClips and MergeBoard

The clipboard inside Spellforge is calmer, deeper, and safer than the system clipboard. Two surfaces work together: PocketClips (ten numbered slots plus a library) and MergeBoard (deterministic joining of captured pieces).

### 6.1 Ten slots that remember source and time

Each slot stores not just text but also which application produced it, when it was captured, its size, and whether it is protected from overwrite.

1. `Control+Alt+1` - copy current selection (or system clipboard) to slot 1.
2. `Control+Alt+2` - paste from slot 1.
3. `Control+Alt+3` - delete the current slot.
4. `Control+Alt+4` - describe the current slot in plain language.
5. `Control+Alt+6` - open the clip library.

Slots 1 through 10 follow the same pattern. The palette lets you protect, unprotect, edit, search, sort, pin favourites, batch-act, split, merge, compare, export, and import slot packs.

### 6.2 The Clip Library

The library is where slots become long-term knowledge. Open it with `Control+Alt+6` or from the palette.

You can:

1. Create folders and categories.
2. Move a clip into a folder or link it into several folders without duplication.
3. Retain a familiar slot number alias even after a clip moves into the library.
4. Choose how alias conflicts resolve (rename, replace, or reject).
5. Set retention rules - keep forever, age out, or pin-protected.
6. Restore an archived clip back into an active slot.
7. Browse a timeline of how a clip evolved.

Every action announces a short summary and is recorded in the operation journal, so you can roll back.
Use `Control+Alt+Shift+J` for one-step quick undo of the latest reversible action.

### 6.3 MergeBoard: build up output without losing your place

MergeBoard joins captured pieces deterministically. Set the mode once, then capture from wherever you like.

1. `Control+Alt+M` - set merge mode to append.
2. `Control+Alt+Shift+M` - set merge mode to replace.
3. `Control+Alt+L` - divider: line.
4. `Control+Alt+U` - divider: single space.
5. `Control+Alt+N` - divider: paragraph.
6. `Control+Alt+I` - toggle `clear-on-paste`.

Use a merge profile (meeting notes, research digest, email drafting) from the palette and Spellforge will apply the right divider, optional source tags, and clear policy automatically. Then commit the merge wherever you need the result.

### 6.4 Across applications

Slot capture in Edge and Chrome carries page provenance. Slot capture in Outlook carries sender and subject context. Slot paste into Word, Notepad, and VS Code preserves clean text. Slot paste into a webmail compose field tries to retain paragraph structure. Whenever a target surface refuses a paste, the fallback menu offers `paste as plain text`, `open in virtual view first`, or `open the palette`.

---

## 7. Quick Capture and Your Inbox

Some thoughts cannot wait. Press `Control+Alt+Q` from anywhere and Spellforge captures a quick note to your inbox without changing your focus or interrupting your flow. The capture remembers source application, timestamp, and any tag you give it.

Later, from the palette:

1. `cmd.capture.quickInbox.list` - browse what you captured.
2. `cmd.capture.quickInbox.route` - turn an inbox item into a task, a note, a draft, or a slot.

When an AI key is configured, Spellforge can attach an optional augmentation, such as a short summary suggestion, without changing the base capture. The original text is always preserved.

---

## 8. Reading Long Results: The Virtualized Surface

When a command produces something longer than a sentence, Spellforge opens a virtualized reading view. You stay in your application, but a calm structured surface holds the output.

1. `Control+Alt+V` - open the latest virtualized result.
2. `Control+Alt+RightArrow` - next block.
3. `Control+Alt+LeftArrow` - previous block.
4. `Control+Alt+C` - copy current block.
5. `Control+Alt+Shift+C` - copy the entire result.
6. `Control+Alt+Control+F` - search inside the result.
7. `Control+Alt+K` - read the confidence summary.
8. `Control+Alt+F` - open the fallback menu of alternatives.
9. `Control+Alt+P` - pin the result to your inbox for later.
10. `Control+Alt+Backspace` - return to exactly where you came from.

Toggles for output density live alongside:

1. `Control+Alt+B` - toggle speech density.
2. `Control+Alt+Z` - toggle braille density.

You never lose your place. You never have to scroll a long output inside an application that was not meant for it.

---

## 9. Text Expansion and Quick Insert

Build a personal shorthand. Type a short trigger and Spellforge expands it. Insert frequently used snippets with one press.

1. `Control+Alt+0` - quick insert a saved piece of text.
2. From the palette: create, list, rename, set primary, expand, and delete expansions.

Text expansion is local, deterministic, and works in any text field that accepts normal typing.

---

## 10. Shortcuts and the Launcher

Shortcuts are your personal jump points. They can target a file, a folder, a website, or an application. They live in categories and can be grouped into presets.

1. `Control+Alt+7` - open the shortcut launcher.
2. `Control+Alt+9` - add the application you are currently using as a shortcut.
3. `Control+Alt+8` - list mapped drive aliases.
4. `Control+Alt+5` - open the shortcuts dashboard.

Presets let you launch a full set of resources for a project, a meeting, or a daily routine, in one step.

---

## 11. Notes, Authoring, and Retrieval

Spellforge is a small, friendly authoring environment.

### 11.1 Notes

Quick capture into the notes workspace, organise into categories, set custom fields, relate notes to each other, attach files, snapshot for safety, and restore. From the palette, search `notes` to see every command.

When AI is configured, note quick capture and note help text can include an optional AI rewrite augmentation. Your original note is never overwritten without preview.

### 11.2 Markdown authoring

Markdown commands help you build structured content that pastes cleanly into any markdown-aware editor (VS Code, Obsidian, Joplin, GitHub web editors).

1. `cmd.author.markdown.insert` - insert structured markdown for headings, lists, tables, callouts, or code blocks.
2. `cmd.author.a11y.lint` - check the markdown you have for accessibility issues such as missing alt text, ambiguous link text, skipped heading levels, and emoji that should be removed.
3. `cmd.author.a11y.fixPreview` - preview the accessibility fixes Spellforge suggests before applying any of them.
4. `cmd.author.pipeline.polish` - run one-command draft-to-polished flow with transform, structure check, and style pass.
5. `cmd.author.template.apply` - apply the guided `release-notes` template scaffold with placeholder sections.
6. `cmd.author.pipeline.undo` - restore the source text from the latest authoring undo token.
7. `cmd.author.export.html` - export markdown to clean semantic HTML.
8. `cmd.author.export.word` - export to a Word-compatible stub.

Mnemonic defaults:
1. `Control+Alt+Shift+A` - run markdown polish flow.
2. `Control+Alt+Shift+N` - apply release-notes template.
3. `Control+Alt+Shift+Z` - undo latest author pipeline output.

### 11.3 HTML authoring

When you need accessible HTML directly:

1. `cmd.author.html.semantic` - generate semantic HTML with `article`, `header`, and `section` structure from a title and a list of items.
2. `cmd.author.html.validate` - validate HTML for common accessibility and structure issues, with concise per-issue guidance.
3. `cmd.author.html.fixPreview` - generate a non-destructive accessibility fix preview with before and after change details.
4. `cmd.author.html.fixApply` - apply the HTML fix preview output and create an undo token for rollback.

These helpers produce output suitable for documentation sites, email templates, intranet articles, and any place where semantic structure matters.

### 11.4 Retrieval

Spellforge can read structured information back to you on demand: parse a body of text, query it, summarise, revisit, anchor your place, return to the anchor, and report what you have visited.

1. `cmd.retrieve.parse`, `cmd.retrieve.query`, `cmd.retrieve.summarize`.
2. `cmd.retrieve.anchor.set`, `cmd.retrieve.revisit`, `cmd.retrieve.trail.open`, `cmd.retrieve.trail.return`, `cmd.retrieve.visited.report`.

### 11.5 Structured records, integrations, and workflow packs

Define typed fields, manage entries, search, sort, and export to text, CSV, or JSON. Sync with Joplin or with the Jamal bridge using plan / apply-plan / rollback. Export and import full workflow packs so your setup travels with you.

---

## 12. Working Across Your Day

Here is what Spellforge feels like in the applications you use most.

### 12.1 Outlook

1. Triage a long thread. Select it, press `Control+Alt+S` for a summary. Press `Control+Alt+A` for action items.
2. Draft a reply from extracted actions through the palette.
3. Tag a message with `Control+Alt+Shift+T`. Report tagged messages with `cmd.tags.outlook.report`.
4. Batch-copy, batch-move, or batch-delete tagged messages from the palette.

### 12.2 Word

1. Select a rough paragraph. Press `Control+Alt+R` for rewrite-for-beginners. A preview opens with confidence and main changes.
2. Save a passage with `Control+Alt+1` for later reuse.
3. Capture a multi-page passage with selection markers if the cursor cannot reach the end natively.

### 12.3 Notepad

1. Spellforge fits Notepad like a glove. Quick capture works instantly with `Control+Alt+Q`.
2. Slot save and paste use the deterministic clip path.
3. Use markers for any range Notepad cannot select cleanly.

### 12.4 Edge, Chrome, Firefox

1. Read a long article. Select a section, press `Control+Alt+S`. The virtual view opens for calm reading.
2. Capture multiple snippets into MergeBoard with `Control+Alt+M`, divide them with `Control+Alt+L`, and commit a clean digest into your notes.
3. When a page is awkward to select, press `Control+Alt+F` to choose `paragraph`, `heading block`, or `guided capture`.

### 12.5 VS Code

1. Select a code block and capture it to a slot for reuse in another file.
2. Use the markdown authoring helpers to insert structured documentation directly.
3. Run `cmd.author.html.validate` against generated HTML output.
4. Selection survives moving between the editor pane and the integrated terminal.

### 12.6 Anywhere else

If Spellforge cannot perform a command in the current application, it tells you and offers alternatives. Press `Control+Alt+F` to see them. Press `Control+Alt+Space` and ask in plain language.

---

## 13. AI Augmentation, Without Surprises

Spellforge ships strong deterministic results for every selection command. AI is optional, additive, and always under your control.

### 13.1 Setting up an AI key

From the palette:

1. `cmd.ai.key.set` - set or update a provider key (for example, Llama Cloud).
2. `cmd.ai.key.status` - check whether keys are configured.
3. `cmd.ai.key.storeStatus` - report the active key storage backend.
4. `cmd.ai.key.delete` - remove a key.

On Windows, Spellforge prefers Windows Credential Manager and never stores provider keys in plain JSON. If secure storage is unavailable, Spellforge falls back safely and tells you what the backend is.

When `cmd.ai.key.storeStatus` runs from the NVDA layer, Spellforge now speaks a short plain-language summary: backend name, whether storage is secure, whether keys persist after restart, and how many providers are configured.

### 13.2 What AI augments

When a key is configured and Spellforge has a real selection or capture, AI may add an optional augmentation to:

1. Selection summarise, action extraction, and rewrite-for-beginners.
2. Quick capture (an optional summary suggestion).
3. Notes quick capture and notes help text.
4. Spellcheck augmentation for word choice in long passages.

The deterministic primary result is always produced first. AI augmentation is presented as a suggestion, never silently applied.

### 13.3 What AI never does

1. It does not run if no key is configured.
2. It does not persist your text outside the workflow you ran it in.
3. It does not bypass previews, confirmations, or the operation journal.

### 13.4 Documents, images, prompts, and sessions

Optional AI workflows from the palette include `cmd.ai.doc.ask`, `cmd.ai.doc.upload`, `cmd.ai.doc.followUp`, `cmd.ai.image.generate`, `cmd.ai.prompt.create/list/insert/delete`, `cmd.ai.transcribe`, and AI session management with new, save, load, list, clear, and delete. Each is documented in the palette and respects the same safety story.

---

## 14. Safety, Recovery, and Diagnostics

### 14.1 Safety by design

1. **Confirmations** for any command that cannot be undone.
2. **Previews** before any substantial change to your text.
3. **Fallback suggestions** instead of silent failure.
4. **Operation journal** for rollback of supported actions.
5. **Emergency stop** at `Control+Alt+Escape`.
6. **Return to source** at `Control+Alt+Backspace` after any virtual view.

### 14.2 Diagnostics

1. `Control+Alt+D` - hotkey diagnostics with conflict detection.
2. `Control+Alt+Slash` - available hotkeys for the current surface.
3. `cmd.profile.integrationHealth` - end-to-end module health.
4. `cmd.utility.systemReport.open` and `cmd.utility.systemReport.export` - rich system report.

### 14.3 Where am I?

If context feels off, press `Control+Alt+Backspace` first. If the question remains, open the palette and search `where am I`. Spellforge will announce focus, surface, selection, and active markers in a single calm message.

---

## 15. The Command Palette In Depth

The Spellforge key chord (`NVDA Key+Space`) opens the palette. `NVDA+Shift+P` opens it too. The palette is a searchable, plain-language entry point to every Spellforge command.

1. Type one or two words describing what you want.
2. Browse the matching results with the arrow keys.
3. Press Enter to run.

The palette is context-aware. AI setup and status commands are always visible. Selection-driven AI commands appear only when Spellforge has selection context and a key is configured. Commands that cannot run in the current surface are dimmed and offer their nearest fallback.

You never need to memorise commands. The palette is the answer when you cannot remember the hotkey.

---

## 16. Hotkey Reference

These are the built-in hotkeys. The NVDA Key is the key you set as NVDA modifier - typically `Insert` or `CapsLock`.

| Hotkey | What it does |
| --- | --- |
| NVDA Key+Space | Open command palette |
| NVDA Key+Space (double) | Read available hotkeys |
| NVDA Key+Space (triple) | Hotkey diagnostics |
| NVDA Key+Space (hold) | Guided hotkey help |
| NVDA Key+Shift+P | Open command palette |
| Control+Alt+Slash | Read available hotkeys |
| Control+Alt+D | Hotkey diagnostics |
| Control+Alt+Escape | Emergency stop |
| Control+Alt+Backspace | Return to source anchor |
| Control+Alt+S | Summarise selection |
| Control+Alt+A | Extract action items |
| Control+Alt+R | Rewrite selection for beginners |
| Control+Alt+[ | Mark selection start |
| Control+Alt+] | Mark selection end |
| Control+Alt+' | Read selection context |
| Control+Alt+; | Read selection marker status |
| Control+Alt+J | Jump to selection start |
| Control+Alt+X | Cancel selection markers |
| CapsLock+F1..F12 | Select active clip slot 1..12 |
| CapsLock+Shift+F1..F12 | Copy to clip slot 1..12 |
| CapsLock+Control+F1..F12 | Paste from clip slot 1..12 |
| CapsLock+Windows+F1..F12 | Describe clip slot 1..12 |
| Control+Alt+3 | Delete active clip slot |
| Control+Alt+Shift+P | Protect active clip slot |
| Control+Alt+Shift+U | Unprotect active clip slot |
| Control+Alt+Shift+E | Edit active clip slot |
| Control+Alt+5 | Open shortcuts dashboard |
| Control+Alt+6 | Open clip library |
| Control+Alt+Shift+6 | Open clip browser |
| Control+Alt+7 | Open shortcut launcher |
| Control+Alt+8 | List drive aliases |
| Control+Alt+9 | Add focused app as shortcut |
| Control+Alt+0 | Quick insert saved text |
| Control+Alt+V | Open latest virtualized result |
| Control+Alt+RightArrow | Next virtual block |
| Control+Alt+LeftArrow | Previous virtual block |
| Control+Alt+C | Copy current virtual block |
| Control+Alt+Shift+C | Copy full result |
| Control+Alt+Control+F | Search in virtualized result |
| Control+Alt+K | Read confidence summary |
| Control+Alt+F | Open fallback menu |
| Control+Alt+P | Pin result to inbox |
| Control+Alt+B | Toggle speech density |
| Control+Alt+Z | Toggle braille density |
| Control+Alt+Q | Quick capture to inbox |
| Control+Alt+M | Merge mode: append |
| Control+Alt+Shift+M | Merge mode: replace |
| Control+Alt+L | Merge divider: line |
| Control+Alt+U | Merge divider: space |
| Control+Alt+N | Merge divider: paragraph |
| Control+Alt+I | Toggle merge clear-on-paste |
| Control+Alt+T | Tag current session |
| Control+Alt+Shift+T | Tag Outlook message |
| Control+Alt+Shift+Y | Speak current time |
| Control+Alt+H | Browse speech history |
| Control+Alt+Shift+H | Open speech history as virtual view |
| Control+Alt+W | Recall window bookmark |
| Control+Alt+Shift+W | List window bookmarks |
| Control+Alt+= | Search symbol by name |
| Control+Alt+- | Recent symbol |

If you would like to change a chord, open `NVDA Settings > Spellforge > Edit keyboard mappings`, or use `Tools > Spellforge keyboard mappings`. Run `Run NVDA gesture scrub` in the editor to detect internal collisions and clashes with known NVDA gestures.

---

## 17. Command Catalogue

The palette holds every command. Use it as your discovery surface. Here is a grouped overview so you know what exists before you search for it.

1. **author** - markdown insert, markdown polish pipeline, markdown undo, template apply, HTML semantic, HTML validate, HTML fix preview and apply, accessibility lint, accessibility fix preview, export HTML, export Word.
2. **backup** - migrate, run selected, create settings backup, restore settings, add source, set target.
3. **capture** - quick capture to inbox, list captures, route captures.
4. **ai** - key set, key delete, key status, key store status, billing status, doc ask, doc follow-up, doc upload, image generate, prompt create/list/insert/delete, session new/save/load/list/clear/delete, tool run, transcribe.
5. **clip** - slot copy/paste/delete/describe/edit/protect/unprotect, browser open/search/filter/sort/batch action/compare/split/merge/reorder/export/import, library open/create folder/rename folder/delete folder/move/link/list linked locations/retain alias/restore to slot/set retention policy/timeline.
6. **contacts** - create, search, copy field, insert field, sync Google.
7. **context** - capability envelope, return source, drift-safe return source, where am I.
8. **cuts** - quick cuts launch, list, assign category, create preset, run preset, export presets, import presets, dashboard.
9. **date** - insert, day of week, add days.
10. **db** - create, list, select, delete, restore, template apply, field define, entry add/edit/delete/list/grid/detail, search, advanced search, sort, export CSV/JSON/text, dashboard.
11. **diary** - create, list month.
12. **file** - browse, copy, move, rename, delete, copy path, zip create, batch tag.
13. **help** - available hotkeys.
14. **jamal** - launch, export, import, sync, plan, apply plan, rollback, return.
15. **joplin** - import, export, refresh, refresh rollback, set mapping.
16. **journal** - list, rollback, undo last reversible action, trends.
17. **mail** - extract sender, attachments action.
18. **merge** - mode append/replace, divider line/space/paragraph, custom separator, toggle clear on paste, apply profile, commit.
19. **missions** - start, complete, status.
20. **notes** - quick capture, mode set, field set, relate, related graph, category create/move/tree, attachment add/action, backup export/restore, snapshot create/restore, help set, help resolve.
21. **nvda** - readiness API, baseline, security.
22. **palette** - open.
23. **profile** - hotkey chain create/list/run, hotkey diagnostics, hotkey preset export/import, integration health, portability backup/restore.
24. **result** - virtual open, block next/previous/copy, copy all, search, read confidence, toggle speech density, toggle braille density, open fallbacks, pin inbox.
25. **retrieve** - parse, query, summarize, anchor set, revisit, trail open, trail return, visited report.
26. **selection** - mark start, mark end, read context, marker status, jump start, cancel, summarize, extract actions, rewrite beginner.
27. **shortcuts** - create, list, dialog detect, dialog insert path, drive list/map/unmap, launcher add/add focused app/open/remove/restore defaults, assign category, create preset, run preset.
28. **social** - nickname upsert/replace, notifications set, orbit summary.
29. **speech** - history browse/capture/copy item/copy range/virtual view.
30. **system** - emergency stop.
31. **table** - capture, capture clear buffer, capture export clipboard.
32. **tags** - Outlook tag/untag/cancel/report/batch copy/batch move/batch delete, session tag/untag/cancel/count/report/batch copy/batch cut/batch delete/batch playlist add.
33. **tasks** - create, complete, list, export ICS, sync Google Calendar.
34. **text** - expansion upsert/list/rename/expand/delete/set primary, quick insert.
35. **time** - speak, speak seconds, insert, alarm set/status/cancel, countdown start/status/stop, monitor start/status/stop, stopwatch start/stop/elapsed/clear/set precision.
36. **utility** - audio cycle card/split/restore balance, notifications import/restore, progress cues plan, symbol insert by code/recent/search, system report open/export, window bookmark assign/list/recall/rename.
37. **whatsapp** - recent, voice.
38. **workflow** - pack export, pack import.
39. **x** - timeline.

You do not need to remember any of these. Press `Control+Alt+Space` and ask in plain language.

---

## 18. Your Data and Portability

Spellforge stores your clips, settings, palette history, notes, journals, and other personal data under your Windows user profile, typically `AppData\Spellforge`. Everything stays on your computer.

1. AI provider keys live in secure storage (Windows Credential Manager when available) and not in plain JSON.
2. Use `cmd.ai.key.storeStatus` to confirm the active backend.
3. Use `cmd.profile.portabilityBackup` and `cmd.profile.portabilityRestore` to move your full setup to a new machine.
4. Use `cmd.workflow.pack.export` and `cmd.workflow.pack.import` to take whole workflows with you.

---

## 19. Troubleshooting

**A hotkey did nothing.** Press `Control+Alt+D` for hotkey diagnostics. Open the palette and search the command name to confirm it exists in your current build.

**Spellforge is talking too much, or not enough.** Switch profile in `NVDA Settings > Spellforge`.

**A command cannot run in this application.** Press `Control+Alt+F` for alternatives, or open the palette and ask Spellforge in plain language.

**Something feels stuck.** Press `Control+Alt+Escape`. Spellforge stops.

**You feel lost.** Press `Control+Alt+Backspace` to return to source. If you are still uncertain, press `Control+Alt+Space` twice to hear what you can press right now.

**An AI command says it is unavailable.** Run `cmd.ai.key.status` to check whether a key is configured, then `cmd.ai.key.storeStatus` to confirm secure storage. Deterministic primary results never require AI.

---

## 20. A Gentle Path Through Your First Week

There is no pressure to learn everything at once. Here is a one-week shape if it helps.

1. **Day 1.** Press `Control+Alt+Space` and read the palette. Press it twice and hear your hotkeys. Try `Control+Alt+Q` to capture a thought.
2. **Day 2.** Select text in a browser and press `Control+Alt+S`. Read the result in the virtual view with `Control+Alt+V`.
3. **Day 3.** Save two passages into slots 1 and 2. Paste them somewhere. Open the clip library with `Control+Alt+6`.
4. **Day 4.** Set up two text expansions. Add the application you use most as a shortcut with `Control+Alt+9`.
5. **Day 5.** Try the markdown authoring helpers and the accessibility lint on a notes file.
6. **Day 6.** Add tasks, diary entries, or time alarms from the palette.
7. **Day 7.** Run `cmd.profile.integrationHealth` and `cmd.profile.portabilityBackup` so your setup is safe.

Once you can open the palette, capture a thought, save and reuse a clip, and read one long result in the virtual view, Spellforge is already earning its place. Everything else is here when you are ready.

Welcome aboard.
