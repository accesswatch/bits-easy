from __future__ import annotations

from typing import Callable

try:
    from logHandler import log
except Exception:  # pragma: no cover - logHandler is always present inside NVDA
    import logging

    log = logging.getLogger("spellforge.addon.settings")


_KNOWN_NVDA_GESTURES = {
    "NVDA+N",
    "NVDA+Q",
    "NVDA+S",
    "NVDA+R",
    "NVDA+TAB",
    "NVDA+F7",
    "NVDA+F12",
    "NVDA+T",
    "NVDA+B",
    "NVDA+F",
    "NVDA+SHIFT+F",
    "NVDA+CONTROL+F",
    "NVDA+SPACE",
    "NVDA+UPARROW",
    "NVDA+DOWNARROW",
    "NVDA+LEFTARROW",
    "NVDA+RIGHTARROW",
    "NVDA+HOME",
    "NVDA+END",
    "NVDA+PAGEUP",
    "NVDA+PAGEDOWN",
    "NVDA+1",
    "NVDA+2",
    "NVDA+3",
    "NVDA+4",
    "NVDA+5",
    "NVDA+6",
    "NVDA+7",
    "NVDA+8",
    "NVDA+9",
    "NVDA+SHIFT+S",
    "NVDA+SHIFT+V",
}


def _normalize_chord(chord: str) -> str:
    parts = [p.strip() for p in str(chord or "").split("+") if p.strip()]
    if not parts:
        return ""

    mods = []
    key = ""
    for part in parts:
        p = part.upper()
        if p in ("CTRL", "CONTROL"):
            mods.append("CONTROL")
        elif p == "SHIFT":
            mods.append("SHIFT")
        elif p == "ALT":
            mods.append("ALT")
        elif p in ("WIN", "WINDOWS"):
            mods.append("WIN")
        else:
            key = p

    ordered = []
    for m in ("CONTROL", "ALT", "SHIFT", "WIN"):
        if m in mods:
            ordered.append(m)
    if key:
        ordered.append(key)
    return "+".join(ordered)


def _binding_signature(binding: dict) -> str:
    trigger = _trigger_kind(binding)
    scope = str(binding.get("scope", "global"))
    app_id = binding.get("appId")
    app = "*" if app_id in (None, "") else str(app_id)
    chord = _normalize_chord(str(binding.get("keyChord", "")))
    return f"{chord}|{trigger}|{scope}|{app}"


def _collect_internal_collisions(bindings: list[dict]) -> list[tuple[str, list[str]]]:
    grouped: dict[str, list[str]] = {}
    for row in bindings:
        if not bool(row.get("enabled", True)):
            continue
        sig = _binding_signature(row)
        cid = str(row.get("commandId", ""))
        grouped.setdefault(sig, []).append(cid)

    collisions: list[tuple[str, list[str]]] = []
    for sig, command_ids in grouped.items():
        if len(command_ids) > 1:
            collisions.append((sig, command_ids))
    collisions.sort(key=lambda x: x[0])
    return collisions


def _collect_nvda_collisions(bindings: list[dict], nvda_chords: set[str]) -> list[tuple[str, str]]:
    hits: list[tuple[str, str]] = []
    for row in bindings:
        if not bool(row.get("enabled", True)):
            continue
        if _trigger_kind(row) != "single-press":
            continue
        chord = _normalize_chord(str(row.get("keyChord", "")))
        if chord in nvda_chords:
            hits.append((chord, str(row.get("commandId", ""))))
    hits.sort(key=lambda x: (x[0], x[1]))
    return hits


def _runtime_nvda_gestures() -> set[str]:
    gestures: set[str] = set()
    try:
        import globalCommands

        raw = getattr(globalCommands.commands, "_GlobalCommands__gestures", None)
        if isinstance(raw, dict):
            for gesture in raw.keys():
                g = str(gesture)
                if g.lower().startswith("kb:"):
                    g = g[3:]
                gestures.add(_normalize_chord(g))
    except Exception:
        pass
    return gestures

def _trigger_kind(binding: dict) -> str:
    trigger = binding.get("trigger") or {"kind": "single-press"}
    return str(trigger.get("kind", "single-press"))


def _binding_label(index: int, binding: dict, command_catalog: dict) -> str:
    command_id = str(binding.get("commandId", ""))
    command_name = str((command_catalog.get(command_id) or {}).get("name", command_id))
    chord = str(binding.get("keyChord", ""))
    scope = str(binding.get("scope", "global"))
    trigger_kind = _trigger_kind(binding)
    enabled = "on" if bool(binding.get("enabled", True)) else "off"
    return f"{index + 1}. {command_name} | {chord} | {trigger_kind} | {scope} | {enabled}"


def open_hotkey_editor_dialog(parent, keymap_bindings: list[dict], command_catalog: dict, on_save: Callable[[list[dict]], None]):
    try:
        import wx
    except Exception:
        log.exception("Spellforge: hotkey editor wx import failed")
        return False

    class HotkeyEditorDialog(wx.Dialog):
        def __init__(self):
            super().__init__(parent, title="Spellforge Keyboard Mappings", size=(900, 520))
            self._rows = [dict(row) for row in keymap_bindings]
            self._current_index = -1

            root = wx.BoxSizer(wx.VERTICAL)

            root.Add(
                wx.StaticText(
                    self,
                    label=(
                        "Edit key chords and enable state for any mapping. "
                        "Use Advanced mode to edit trigger kind and scope."
                    ),
                ),
                border=8,
                flag=wx.ALL,
            )

            body = wx.BoxSizer(wx.HORIZONTAL)

            self.bindingList = wx.ListBox(self)
            body.Add(self.bindingList, proportion=1, flag=wx.EXPAND | wx.ALL, border=8)

            form = wx.BoxSizer(wx.VERTICAL)
            self.commandText = wx.StaticText(self, label="Command: ")
            form.Add(self.commandText, border=4, flag=wx.BOTTOM)

            self.scopeText = wx.StaticText(self, label="Scope: ")
            form.Add(self.scopeText, border=4, flag=wx.BOTTOM)

            self.triggerText = wx.StaticText(self, label="Trigger: ")
            form.Add(self.triggerText, border=8, flag=wx.BOTTOM)

            form.Add(wx.StaticText(self, label="Key chord"), border=4, flag=wx.BOTTOM)
            self.keyChordInput = wx.TextCtrl(self)
            form.Add(self.keyChordInput, border=8, flag=wx.EXPAND | wx.BOTTOM)

            self.enabledCheck = wx.CheckBox(self, label="Binding enabled")
            form.Add(self.enabledCheck, border=8, flag=wx.BOTTOM)

            self.advancedCheck = wx.CheckBox(self, label="Advanced mode")
            self.advancedCheck.SetValue(False)
            form.Add(self.advancedCheck, border=8, flag=wx.BOTTOM)

            self.scopeLabel = wx.StaticText(self, label="Scope")
            form.Add(self.scopeLabel, border=4, flag=wx.BOTTOM)
            self.scopeChoice = wx.Choice(self, choices=["global", "virtualized", "app-override"])
            form.Add(self.scopeChoice, border=8, flag=wx.EXPAND | wx.BOTTOM)

            self.appIdLabel = wx.StaticText(self, label="App override appId (only for app-override scope)")
            form.Add(self.appIdLabel, border=4, flag=wx.BOTTOM)
            self.appIdInput = wx.TextCtrl(self)
            form.Add(self.appIdInput, border=8, flag=wx.EXPAND | wx.BOTTOM)

            self.triggerLabel = wx.StaticText(self, label="Trigger kind")
            form.Add(self.triggerLabel, border=4, flag=wx.BOTTOM)
            self.triggerChoice = wx.Choice(self, choices=["single-press", "double-press", "triple-press", "press-and-hold"])
            form.Add(self.triggerChoice, border=8, flag=wx.EXPAND | wx.BOTTOM)

            applyRowButton = wx.Button(self, label="Apply To Selected")
            form.Add(applyRowButton, border=8, flag=wx.BOTTOM)

            scrubButton = wx.Button(self, label="Run NVDA gesture scrub")
            form.Add(scrubButton, border=8, flag=wx.BOTTOM)

            body.Add(form, proportion=0, flag=wx.EXPAND | wx.ALL, border=8)
            root.Add(body, proportion=1, flag=wx.EXPAND)

            buttons = wx.StdDialogButtonSizer()
            self.saveButton = wx.Button(self, wx.ID_OK, "Save")
            self.cancelButton = wx.Button(self, wx.ID_CANCEL, "Cancel")
            buttons.AddButton(self.saveButton)
            buttons.AddButton(self.cancelButton)
            buttons.Realize()
            root.Add(buttons, flag=wx.ALIGN_RIGHT | wx.ALL, border=8)

            self.SetSizer(root)

            self.bindingList.Bind(wx.EVT_LISTBOX, self._on_select)
            applyRowButton.Bind(wx.EVT_BUTTON, self._on_apply_row)
            scrubButton.Bind(wx.EVT_BUTTON, self._on_scrub)
            self.advancedCheck.Bind(wx.EVT_CHECKBOX, self._on_toggle_advanced)
            self._set_advanced_enabled(False)

            self._refresh_list()
            if self._rows:
                self.bindingList.SetSelection(0)
                self._set_current(0)

        def _refresh_list(self):
            labels = [_binding_label(i, row, command_catalog) for i, row in enumerate(self._rows)]
            self.bindingList.Set(labels)

        def _set_current(self, index: int):
            if index < 0 or index >= len(self._rows):
                self._current_index = -1
                return

            self._current_index = index
            row = self._rows[index]
            command_id = str(row.get("commandId", ""))
            command_name = str((command_catalog.get(command_id) or {}).get("name", command_id))

            self.commandText.SetLabel(f"Command: {command_name} ({command_id})")
            self.scopeText.SetLabel(f"Scope: {row.get('scope', 'global')}")
            self.triggerText.SetLabel(f"Trigger: {_trigger_kind(row)}")
            self.keyChordInput.SetValue(str(row.get("keyChord", "")))
            self.enabledCheck.SetValue(bool(row.get("enabled", True)))
            scope = str(row.get("scope", "global"))
            if scope in ("global", "virtualized", "app-override"):
                self.scopeChoice.SetStringSelection(scope)
            else:
                self.scopeChoice.SetStringSelection("global")

            app_id = row.get("appId")
            self.appIdInput.SetValue("" if app_id is None else str(app_id))

            trig = _trigger_kind(row)
            if trig in ("single-press", "double-press", "triple-press", "press-and-hold"):
                self.triggerChoice.SetStringSelection(trig)
            else:
                self.triggerChoice.SetStringSelection("single-press")

        def _set_advanced_enabled(self, enabled: bool):
            self.scopeLabel.Enable(enabled)
            self.scopeChoice.Enable(enabled)
            self.appIdLabel.Enable(enabled)
            self.appIdInput.Enable(enabled)
            self.triggerLabel.Enable(enabled)
            self.triggerChoice.Enable(enabled)

        def _on_toggle_advanced(self, _evt):
            self._set_advanced_enabled(bool(self.advancedCheck.GetValue()))

        def _on_select(self, _evt):
            self._set_current(self.bindingList.GetSelection())

        def _on_apply_row(self, _evt):
            if self._current_index < 0:
                return

            new_chord = self.keyChordInput.GetValue().strip()
            if len(new_chord) < 3:
                wx.MessageBox("Key chord must be at least 3 characters.", "Spellforge", wx.OK | wx.ICON_WARNING)
                return

            row = self._rows[self._current_index]
            row["keyChord"] = new_chord
            row["enabled"] = bool(self.enabledCheck.GetValue())

            if self.advancedCheck.GetValue():
                scope = self.scopeChoice.GetStringSelection() or "global"
                row["scope"] = scope

                if scope == "app-override":
                    app_id = self.appIdInput.GetValue().strip()
                    if not app_id:
                        wx.MessageBox("appId is required for app-override scope.", "Spellforge", wx.OK | wx.ICON_WARNING)
                        return
                    row["appId"] = app_id
                else:
                    row["appId"] = None

                trigger_kind = self.triggerChoice.GetStringSelection() or "single-press"
                prev_trigger = row.get("trigger") if isinstance(row.get("trigger"), dict) else {}
                if trigger_kind == "single-press":
                    row.pop("trigger", None)
                elif trigger_kind in ("double-press", "triple-press"):
                    row["trigger"] = {
                        "kind": trigger_kind,
                        "multiPressWindowMs": int(prev_trigger.get("multiPressWindowMs", 350)),
                        "suppressSinglePress": bool(prev_trigger.get("suppressSinglePress", True)),
                    }
                else:
                    row["trigger"] = {
                        "kind": "press-and-hold",
                        "holdThresholdMs": int(prev_trigger.get("holdThresholdMs", 600)),
                        "suppressSinglePress": bool(prev_trigger.get("suppressSinglePress", True)),
                    }

            self._refresh_list()
            self.bindingList.SetSelection(self._current_index)

        def _on_scrub(self, _evt):
            nvda_gestures = set(_KNOWN_NVDA_GESTURES)
            nvda_gestures.update(_runtime_nvda_gestures())

            internal = _collect_internal_collisions(self._rows)
            nvda_hits = _collect_nvda_collisions(self._rows, nvda_gestures)

            lines = []
            lines.append(f"Internal collisions: {len(internal)}")
            for sig, command_ids in internal[:12]:
                lines.append(f"- {sig}: {', '.join(command_ids)}")
            if len(internal) > 12:
                lines.append(f"- ... {len(internal) - 12} more")

            lines.append("")
            lines.append(f"Potential NVDA collisions: {len(nvda_hits)}")
            for chord, command_id in nvda_hits[:20]:
                lines.append(f"- {chord}: {command_id}")
            if len(nvda_hits) > 20:
                lines.append(f"- ... {len(nvda_hits) - 20} more")

            msg = "\n".join(lines)
            wx.MessageBox(msg, "Spellforge Hotkey Scrub", wx.OK | wx.ICON_INFORMATION)

    dialog = HotkeyEditorDialog()
    try:
        if dialog.ShowModal() != wx.ID_OK:
            return False
        if dialog._current_index >= 0:
            dialog._on_apply_row(None)

        internal = _collect_internal_collisions(dialog._rows)
        if internal:
            wx.MessageBox(
                "One or more enabled bindings collide exactly (same key, trigger, scope, and app). "
                "Please resolve collisions before saving.",
                "Spellforge",
                wx.OK | wx.ICON_WARNING,
            )
            return False

        on_save(dialog._rows)
        return True
    finally:
        dialog.Destroy()


def register_settings_panel(
    settings_store,
    get_settings: Callable[[], object],
    set_settings: Callable[[object], None],
    open_hotkey_editor: Callable[[], None] | None = None,
):
    try:
        import gui
        import wx
        from gui.settingsDialogs import NVDASettingsDialog, SettingsPanel
    except Exception:
        log.exception("Spellforge: settings panel gui import failed")
        return None

    class SpellforgeSettingsPanel(SettingsPanel):
        title = "Spellforge"

        def makeSettings(self, sizer):
            settings = get_settings()

            self.profileChoice = wx.Choice(self, choices=["beginner", "balanced", "expert"])
            self.profileChoice.SetStringSelection(settings.profile_id)
            sizer.Add(wx.StaticText(self, label="Profile"), border=5, flag=wx.ALL)
            sizer.Add(self.profileChoice, border=5, flag=wx.EXPAND | wx.ALL)

            self.announceSurfaceModeCheck = wx.CheckBox(self, label="Announce detected surface mode")
            self.announceSurfaceModeCheck.SetValue(settings.announce_surface_mode)
            sizer.Add(self.announceSurfaceModeCheck, border=5, flag=wx.ALL)

            self.contextFallbackCheck = wx.CheckBox(self, label="Enable contextual fallback steps")
            self.contextFallbackCheck.SetValue(settings.enable_contextual_fallbacks)
            sizer.Add(self.contextFallbackCheck, border=5, flag=wx.ALL)

            self.commandPaletteCheck = wx.CheckBox(self, label="Enable command palette")
            self.commandPaletteCheck.SetValue(settings.enable_command_palette)
            sizer.Add(self.commandPaletteCheck, border=5, flag=wx.ALL)

            self.globalHotkeysCheck = wx.CheckBox(self, label="Enable OS-level global hotkeys")
            self.globalHotkeysCheck.SetValue(settings.enable_global_hotkeys)
            sizer.Add(self.globalHotkeysCheck, border=5, flag=wx.ALL)

            self.capsEmulationCheck = wx.CheckBox(self, label="Emulate CapsLock prefix as Control+Alt for OS hooks")
            self.capsEmulationCheck.SetValue(settings.emulate_capslock_prefix_for_os_hotkeys)
            sizer.Add(self.capsEmulationCheck, border=5, flag=wx.ALL)

            self.multiPressCheck = wx.CheckBox(self, label="Enable multi-press gestures")
            self.multiPressCheck.SetValue(settings.enable_multi_press_gestures)
            sizer.Add(self.multiPressCheck, border=5, flag=wx.ALL)

            self.hotkeyEditorButton = wx.Button(self, label="Edit keyboard mappings")
            self.hotkeyEditorButton.Bind(wx.EVT_BUTTON, self._on_open_hotkey_editor)
            sizer.Add(self.hotkeyEditorButton, border=5, flag=wx.ALL)

        def _on_open_hotkey_editor(self, _evt):
            if open_hotkey_editor is not None:
                open_hotkey_editor()

        def onSave(self):
            settings = get_settings()
            settings.profile_id = self.profileChoice.GetStringSelection()
            settings.announce_surface_mode = self.announceSurfaceModeCheck.GetValue()
            settings.enable_contextual_fallbacks = self.contextFallbackCheck.GetValue()
            settings.enable_command_palette = self.commandPaletteCheck.GetValue()
            settings.enable_global_hotkeys = self.globalHotkeysCheck.GetValue()
            settings.emulate_capslock_prefix_for_os_hotkeys = self.capsEmulationCheck.GetValue()
            settings.enable_multi_press_gestures = self.multiPressCheck.GetValue()
            set_settings(settings)
            settings_store.save(settings)

    NVDASettingsDialog.categoryClasses.append(SpellforgeSettingsPanel)
    log.info("Spellforge: settings panel registered")
    return SpellforgeSettingsPanel


def unregister_settings_panel(panel_class):
    if panel_class is None:
        return
    try:
        from gui.settingsDialogs import NVDASettingsDialog
    except Exception:
        log.exception("Spellforge: settings panel gui import failed during unregister")
        return

    if panel_class in NVDASettingsDialog.categoryClasses:
        NVDASettingsDialog.categoryClasses.remove(panel_class)
        log.info("Spellforge: settings panel unregistered")
