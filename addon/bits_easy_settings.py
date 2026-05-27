from __future__ import annotations

from typing import Callable

try:
    import addonHandler  # type: ignore[import-not-found]
except Exception:  # pragma: no cover - test runtime outside NVDA
    class _AddonHandlerShim:
        @staticmethod
        def initTranslation() -> None:
            return None

    addonHandler = _AddonHandlerShim()

addonHandler.initTranslation()

if "_" not in globals():
    def _(message: str) -> str:
        return message

try:
    from logHandler import log
except Exception:  # pragma: no cover - logHandler is always present inside NVDA
    import logging

    log = logging.getLogger("bits_easy.addon.settings")


_SCOPE_CHOICES = [
    ("global", _("Global")),
    ("virtualized", _("Virtualized")),
    ("app-override", _("App override")),
]

_TRIGGER_CHOICES = [
    ("single-press", _("Single press")),
    ("double-press", _("Double press")),
    ("triple-press", _("Triple press")),
    ("press-and-hold", _("Press and hold")),
]

_PROFILE_CHOICES = [
    ("beginner", _("Beginner")),
    ("balanced", _("Balanced")),
    ("expert", _("Expert")),
]


def _choice_labels(options: list[tuple[str, str]]) -> list[str]:
    return [label for _, label in options]


def _choice_set_value(choice, options: list[tuple[str, str]], value: str, default: str):
    selected = default
    for raw_value, _label in options:
        if raw_value == value:
            selected = raw_value
            break
    for index, (raw_value, _label) in enumerate(options):
        if raw_value == selected:
            choice.SetSelection(index)
            return
    if options:
        choice.SetSelection(0)


def _choice_get_value(choice, options: list[tuple[str, str]], default: str) -> str:
    selection = int(choice.GetSelection())
    if 0 <= selection < len(options):
        return options[selection][0]
    return default


def _scope_label(scope: str) -> str:
    for raw_value, label in _SCOPE_CHOICES:
        if raw_value == scope:
            return label
    return scope


def _trigger_label(trigger_kind: str) -> str:
    for raw_value, label in _TRIGGER_CHOICES:
        if raw_value == trigger_kind:
            return label
    return trigger_kind


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
        elif p in ("GRAVE", "GRAVEACCENT", "BITSEASY", "BITS-EASY", "EASY") and len(parts) > 1:
            mods.append("GRAVE")
        else:
            key = p

    ordered = []
    for m in ("GRAVE", "CONTROL", "ALT", "SHIFT", "WIN"):
        if m in mods:
            ordered.append(m)
    if key:
        ordered.append(key)
    return "+".join(ordered)


def _display_easy_sequence(chord: str) -> str:
    raw = str(chord or "").strip()
    if not raw:
        return ""

    normalized = _normalize_chord(raw)
    parts = [p.strip() for p in normalized.split("+") if p.strip()]
    if not parts:
        return raw
    if parts[0] != "GRAVE":
        return normalized
    if len(parts) == 1:
        return "EASY"
    return f"EASY then {'+'.join(parts[1:])}"


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
    chord = _display_easy_sequence(str(binding.get("keyChord", "")))
    scope = _scope_label(str(binding.get("scope", "global")))
    trigger_kind = _trigger_label(_trigger_kind(binding))
    enabled = _("Enabled") if bool(binding.get("enabled", True)) else _("Disabled")
    return f"{index + 1}. {command_name} | {chord} | {trigger_kind} | {scope} | {enabled}"


def upsert_custom_mode(modes: dict, mode_name: str, mode_payload: dict) -> dict:
    out = dict(modes or {})
    out[str(mode_name)] = dict(mode_payload or {})
    return out


def remove_custom_mode(modes: dict, mode_name: str, active_mode: str) -> tuple[dict, str]:
    out = dict(modes or {})
    target = str(mode_name)
    out.pop(target, None)
    next_active = "" if str(active_mode) == target else str(active_mode or "")
    return out, next_active


def build_mode_payload(settings, *, hotkey_bindings: list[dict] | None = None) -> dict:
    try:
        from bits_easy_runtime import mode_payload_from_settings

        return mode_payload_from_settings(settings, hotkey_bindings=hotkey_bindings)
    except Exception:
        payload = {
            "baseProfile": str(getattr(settings, "profile_id", "balanced")),
            "overrides": {
                "enable_command_palette": bool(getattr(settings, "enable_command_palette", True)),
                "enable_multi_press_gestures": bool(getattr(settings, "enable_multi_press_gestures", True)),
                "enable_raw_easy_sequences": True,
                "raw_easy_sequence_timeout_ms": int(getattr(settings, "raw_easy_sequence_timeout_ms", 900)),
                "enable_contextual_fallbacks": bool(getattr(settings, "enable_contextual_fallbacks", True)),
                "announce_surface_mode": bool(getattr(settings, "announce_surface_mode", True)),
                "enable_global_hotkeys": bool(getattr(settings, "enable_global_hotkeys", True)),
            },
        }
        if isinstance(hotkey_bindings, list) and hotkey_bindings:
            payload["hotkeyBindings"] = [dict(row) for row in hotkey_bindings if isinstance(row, dict)]
        return payload


def mode_hotkeys_for_editor(mode_payload: dict, fallback_bindings: list[dict]) -> list[dict]:
    if isinstance(mode_payload, dict):
        mode_hotkeys = mode_payload.get("hotkeyBindings")
        if isinstance(mode_hotkeys, list) and mode_hotkeys:
            return [dict(row) for row in mode_hotkeys if isinstance(row, dict)]
    return [dict(row) for row in fallback_bindings if isinstance(row, dict)]


def with_mode_hotkey_bindings(modes: dict, mode_name: str, bindings: list[dict]) -> dict:
    current = dict((modes or {}).get(str(mode_name), {}))
    current["hotkeyBindings"] = [dict(row) for row in bindings if isinstance(row, dict)]
    return upsert_custom_mode(modes, mode_name, current)


def open_hotkey_editor_dialog(parent, keymap_bindings: list[dict], command_catalog: dict, on_save: Callable[[list[dict]], None]):
    try:
        import wx
    except Exception:
        log.exception("BITS-EASY: hotkey editor wx import failed")
        return False

    class HotkeyEditorDialog(wx.Dialog):
        def __init__(self):
            super().__init__(parent, title=_("BITS-EASY Keyboard Mappings"), size=(900, 520))
            self._rows = [dict(row) for row in keymap_bindings]
            self._current_index = -1

            root = wx.BoxSizer(wx.VERTICAL)

            root.Add(
                wx.StaticText(
                    self,
                    label=(
                        _("Edit key chords and enable state for any mapping. ")
                        + _("Use Advanced mode to edit trigger kind and scope.")
                    ),
                ),
                border=8,
                flag=wx.ALL,
            )

            body = wx.BoxSizer(wx.HORIZONTAL)

            self.bindingList = wx.ListBox(self)
            body.Add(self.bindingList, proportion=1, flag=wx.EXPAND | wx.ALL, border=8)

            form = wx.BoxSizer(wx.VERTICAL)
            self.commandText = wx.StaticText(self, label=_("Command: "))
            form.Add(self.commandText, border=4, flag=wx.BOTTOM)

            self.scopeText = wx.StaticText(self, label=_("Scope: "))
            form.Add(self.scopeText, border=4, flag=wx.BOTTOM)

            self.triggerText = wx.StaticText(self, label=_("Trigger: "))
            form.Add(self.triggerText, border=8, flag=wx.BOTTOM)

            form.Add(wx.StaticText(self, label=_("Key sequence (EASY then key)")), border=4, flag=wx.BOTTOM)
            self.keyChordInput = wx.TextCtrl(self)
            form.Add(self.keyChordInput, border=8, flag=wx.EXPAND | wx.BOTTOM)

            self.enabledCheck = wx.CheckBox(self, label=_("Binding enabled"))
            form.Add(self.enabledCheck, border=8, flag=wx.BOTTOM)

            self.advancedCheck = wx.CheckBox(self, label=_("Advanced mode"))
            self.advancedCheck.SetValue(False)
            form.Add(self.advancedCheck, border=8, flag=wx.BOTTOM)

            self.scopeLabel = wx.StaticText(self, label=_("Scope"))
            form.Add(self.scopeLabel, border=4, flag=wx.BOTTOM)
            self.scopeChoice = wx.Choice(self, choices=_choice_labels(_SCOPE_CHOICES))
            form.Add(self.scopeChoice, border=8, flag=wx.EXPAND | wx.BOTTOM)

            self.appIdLabel = wx.StaticText(self, label=_("App override appId (only for app-override scope)"))
            form.Add(self.appIdLabel, border=4, flag=wx.BOTTOM)
            self.appIdInput = wx.TextCtrl(self)
            form.Add(self.appIdInput, border=8, flag=wx.EXPAND | wx.BOTTOM)

            self.triggerLabel = wx.StaticText(self, label=_("Trigger kind"))
            form.Add(self.triggerLabel, border=4, flag=wx.BOTTOM)
            self.triggerChoice = wx.Choice(self, choices=_choice_labels(_TRIGGER_CHOICES))
            form.Add(self.triggerChoice, border=8, flag=wx.EXPAND | wx.BOTTOM)

            applyRowButton = wx.Button(self, label=_("Apply To Selected"))
            form.Add(applyRowButton, border=8, flag=wx.BOTTOM)

            scrubButton = wx.Button(self, label=_("Run NVDA gesture scrub"))
            form.Add(scrubButton, border=8, flag=wx.BOTTOM)

            body.Add(form, proportion=0, flag=wx.EXPAND | wx.ALL, border=8)
            root.Add(body, proportion=1, flag=wx.EXPAND)

            buttons = wx.StdDialogButtonSizer()
            self.saveButton = wx.Button(self, wx.ID_OK, _("Save"))
            self.cancelButton = wx.Button(self, wx.ID_CANCEL, _("Cancel"))
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

            self.commandText.SetLabel(_("Command: ") + f"{command_name} ({command_id})")
            self.scopeText.SetLabel(_("Scope: ") + _scope_label(str(row.get("scope", "global"))))
            self.triggerText.SetLabel(_("Trigger: ") + _trigger_label(_trigger_kind(row)))
            self.keyChordInput.SetValue(str(row.get("keyChord", "")))
            self.enabledCheck.SetValue(bool(row.get("enabled", True)))
            scope = str(row.get("scope", "global"))
            _choice_set_value(self.scopeChoice, _SCOPE_CHOICES, scope, "global")

            app_id = row.get("appId")
            self.appIdInput.SetValue("" if app_id is None else str(app_id))

            trig = _trigger_kind(row)
            _choice_set_value(self.triggerChoice, _TRIGGER_CHOICES, trig, "single-press")

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
                wx.MessageBox(_("Key sequence must be at least 3 characters."), _("BITS-EASY"), wx.OK | wx.ICON_WARNING)
                return

            row = self._rows[self._current_index]
            row["keyChord"] = new_chord
            row["enabled"] = bool(self.enabledCheck.GetValue())

            if self.advancedCheck.GetValue():
                scope = _choice_get_value(self.scopeChoice, _SCOPE_CHOICES, "global")
                row["scope"] = scope

                if scope == "app-override":
                    app_id = self.appIdInput.GetValue().strip()
                    if not app_id:
                        wx.MessageBox(_("appId is required for app-override scope."), _("BITS-EASY"), wx.OK | wx.ICON_WARNING)
                        return
                    row["appId"] = app_id
                else:
                    row["appId"] = None

                trigger_kind = _choice_get_value(self.triggerChoice, _TRIGGER_CHOICES, "single-press")
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
            lines.append(_("Internal collisions: {count}").format(count=len(internal)))
            for sig, command_ids in internal[:12]:
                lines.append(f"- {sig}: {', '.join(command_ids)}")
            if len(internal) > 12:
                lines.append(_("- ... {count} more").format(count=len(internal) - 12))

            lines.append("")
            lines.append(_("Potential NVDA collisions: {count}").format(count=len(nvda_hits)))
            for chord, command_id in nvda_hits[:20]:
                lines.append(f"- {chord}: {command_id}")
            if len(nvda_hits) > 20:
                lines.append(_("- ... {count} more").format(count=len(nvda_hits) - 20))

            msg = "\n".join(lines)
            wx.MessageBox(msg, _("BITS-EASY Hotkey Scrub"), wx.OK | wx.ICON_INFORMATION)

    dialog = HotkeyEditorDialog()
    try:
        if dialog.ShowModal() != wx.ID_OK:
            return False
        if dialog._current_index >= 0:
            dialog._on_apply_row(None)

        internal = _collect_internal_collisions(dialog._rows)
        if internal:
            wx.MessageBox(
                _(
                    "One or more enabled bindings collide exactly (same key, trigger, scope, and app). Please resolve collisions before saving."
                ),
                _("BITS-EASY"),
                wx.OK | wx.ICON_WARNING,
            )
            return False

        on_save(dialog._rows)
        return True
    finally:
        dialog.Destroy()


def open_control_panel_dialog(
    parent,
    settings_store,
    get_settings: Callable[[], object],
    set_settings: Callable[[object], None],
    open_hotkey_editor: Callable[[], None] | None = None,
    get_hotkey_editor_context: Callable[[], tuple[list[dict], dict]] | None = None,
):
    try:
        import wx
    except Exception:
        log.exception("BITS-EASY: control panel wx import failed")
        return False

    class ControlPanelDialog(wx.Dialog):
        def __init__(self):
            super().__init__(parent, title=_("BITS-EASY Control Panel"), size=(980, 620))
            self._settings = get_settings()
            self._modes = dict(getattr(self._settings, "custom_modes", {}) or {})
            self._active_mode = str(getattr(self._settings, "active_mode", "") or "")
            self._selected_mode = ""

            root = wx.BoxSizer(wx.VERTICAL)
            root.Add(
                wx.StaticText(
                    self,
                    label=_("Manage advanced key behavior, launch key assignment tools, and create custom user modes."),
                ),
                border=8,
                flag=wx.ALL,
            )

            tools_row = wx.BoxSizer(wx.HORIZONTAL)
            self.hotkeysButton = wx.Button(self, label=_("Open Key Assignment Editor"))
            self.hotkeysButton.Bind(wx.EVT_BUTTON, self._on_open_hotkeys)
            tools_row.Add(self.hotkeysButton, border=8, flag=wx.RIGHT)
            root.Add(tools_row, border=8, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM)

            split = wx.BoxSizer(wx.HORIZONTAL)

            left = wx.BoxSizer(wx.VERTICAL)
            left.Add(wx.StaticText(self, label=_("Custom Modes")), border=4, flag=wx.BOTTOM)
            self.modeList = wx.ListBox(self)
            left.Add(self.modeList, proportion=1, flag=wx.EXPAND | wx.BOTTOM, border=8)

            create_row = wx.BoxSizer(wx.HORIZONTAL)
            self.newModeName = wx.TextCtrl(self)
            self.createModeBtn = wx.Button(self, label=_("Create"))
            self.createModeBtn.Bind(wx.EVT_BUTTON, self._on_create_mode)
            create_row.Add(self.newModeName, proportion=1, flag=wx.RIGHT, border=6)
            create_row.Add(self.createModeBtn)
            left.Add(create_row, flag=wx.EXPAND | wx.BOTTOM, border=8)

            action_row = wx.BoxSizer(wx.HORIZONTAL)
            self.deleteModeBtn = wx.Button(self, label=_("Delete"))
            self.deleteModeBtn.Bind(wx.EVT_BUTTON, self._on_delete_mode)
            self.activateModeBtn = wx.Button(self, label=_("Activate"))
            self.activateModeBtn.Bind(wx.EVT_BUTTON, self._on_activate_mode)
            action_row.Add(self.deleteModeBtn, border=8, flag=wx.RIGHT)
            action_row.Add(self.activateModeBtn)
            left.Add(action_row, border=0, flag=wx.BOTTOM)

            split.Add(left, proportion=1, flag=wx.EXPAND | wx.ALL, border=8)

            right = wx.BoxSizer(wx.VERTICAL)
            right.Add(wx.StaticText(self, label=_("Mode Configuration")), border=4, flag=wx.BOTTOM)

            self.modeInfo = wx.StaticText(self, label=_("Select or create a mode."))
            right.Add(self.modeInfo, border=8, flag=wx.BOTTOM)

            self.modeHotkeysBtn = wx.Button(self, label=_("Edit Mode Keymap"))
            self.modeHotkeysBtn.Bind(wx.EVT_BUTTON, self._on_edit_mode_hotkeys)
            self.modeHotkeysBtn.Enable(False)
            right.Add(self.modeHotkeysBtn, border=8, flag=wx.BOTTOM)

            right.Add(wx.StaticText(self, label=_("Base profile")), border=4, flag=wx.BOTTOM)
            self.baseProfile = wx.Choice(self, choices=_choice_labels(_PROFILE_CHOICES))
            right.Add(self.baseProfile, border=8, flag=wx.EXPAND | wx.BOTTOM)

            self.commandPaletteCheck = wx.CheckBox(self, label=_("Enable command palette"))
            right.Add(self.commandPaletteCheck, border=6, flag=wx.BOTTOM)

            self.multiPressCheck = wx.CheckBox(self, label=_("Enable multi-press gestures"))
            right.Add(self.multiPressCheck, border=6, flag=wx.BOTTOM)

            self.rawSeqCheck = wx.CheckBox(self, label=_("Use EASY key sequences (required)"))
            self.rawSeqCheck.SetValue(True)
            self.rawSeqCheck.Enable(False)
            right.Add(self.rawSeqCheck, border=6, flag=wx.BOTTOM)

            self.contextFallbackCheck = wx.CheckBox(self, label=_("Enable contextual fallbacks"))
            right.Add(self.contextFallbackCheck, border=6, flag=wx.BOTTOM)

            self.surfaceAnnounceCheck = wx.CheckBox(self, label=_("Announce surface mode"))
            right.Add(self.surfaceAnnounceCheck, border=6, flag=wx.BOTTOM)

            self.globalHotkeysCheck = wx.CheckBox(self, label=_("Enable OS-level hotkeys"))
            right.Add(self.globalHotkeysCheck, border=6, flag=wx.BOTTOM)

            timeout_row = wx.BoxSizer(wx.HORIZONTAL)
            timeout_row.Add(wx.StaticText(self, label=_("Raw EASY timeout (ms)")), border=4, flag=wx.RIGHT)
            self.rawTimeout = wx.SpinCtrl(self, min=250, max=3000)
            timeout_row.Add(self.rawTimeout)
            right.Add(timeout_row, border=8, flag=wx.BOTTOM)

            self.saveModeBtn = wx.Button(self, label=_("Save Mode"))
            self.saveModeBtn.Bind(wx.EVT_BUTTON, self._on_save_mode)
            right.Add(self.saveModeBtn, border=8, flag=wx.BOTTOM)

            split.Add(right, proportion=1, flag=wx.EXPAND | wx.ALL, border=8)
            root.Add(split, proportion=1, flag=wx.EXPAND)

            buttons = wx.StdDialogButtonSizer()
            self.okButton = wx.Button(self, wx.ID_OK, _("Close"))
            buttons.AddButton(self.okButton)
            buttons.Realize()
            root.Add(buttons, flag=wx.ALIGN_RIGHT | wx.ALL, border=8)

            self.SetSizer(root)
            self.modeList.Bind(wx.EVT_LISTBOX, self._on_mode_selected)
            self._refresh_mode_list()

        def _default_mode_payload(self):
            return build_mode_payload(self._settings)

        def _refresh_mode_list(self):
            names = sorted(self._modes.keys())
            self.modeList.Set(names)
            if self._selected_mode and self._selected_mode in names:
                self.modeList.SetStringSelection(self._selected_mode)
                self._load_selected_mode()
            elif names:
                self.modeList.SetSelection(0)
                self._selected_mode = names[0]
                self._load_selected_mode()
            else:
                self.modeHotkeysBtn.Enable(False)

        def _on_open_hotkeys(self, _evt):
            if open_hotkey_editor is not None:
                open_hotkey_editor()

        def _on_edit_mode_hotkeys(self, _evt):
            if not self._selected_mode:
                return
            if get_hotkey_editor_context is None:
                wx.MessageBox("Mode keymap editor is unavailable.", "BITS-EASY", wx.OK | wx.ICON_WARNING)
                return

            try:
                base_bindings, command_catalog = get_hotkey_editor_context()
            except Exception:
                log.exception("BITS-EASY: mode keymap context failed")
                wx.MessageBox(_("Mode keymap editor is unavailable."), _("BITS-EASY"), wx.OK | wx.ICON_WARNING)
                return

            selected_mode = str(self._selected_mode)
            mode_payload = dict(self._modes.get(selected_mode, {}))
            keymap_bindings = mode_hotkeys_for_editor(mode_payload, base_bindings)

            def _save_mode_bindings(bindings: list[dict]):
                self._modes = with_mode_hotkey_bindings(self._modes, selected_mode, bindings)

            changed = open_hotkey_editor_dialog(
                parent=self,
                keymap_bindings=keymap_bindings,
                command_catalog=command_catalog,
                on_save=_save_mode_bindings,
            )
            if changed:
                active_note = _(" (active)") if self._active_mode == selected_mode else ""
                self.modeInfo.SetLabel(_("Mode: {mode}{active} keymap saved").format(mode=selected_mode, active=active_note))

        def _on_create_mode(self, _evt):
            name = self.newModeName.GetValue().strip()
            if len(name) < 2:
                wx.MessageBox(_("Mode name must be at least 2 characters."), _("BITS-EASY"), wx.OK | wx.ICON_WARNING)
                return
            if name in self._modes:
                wx.MessageBox(_("Mode already exists."), _("BITS-EASY"), wx.OK | wx.ICON_WARNING)
                return
            self._modes = upsert_custom_mode(self._modes, name, self._default_mode_payload())
            self._selected_mode = name
            self.newModeName.SetValue("")
            self._refresh_mode_list()

        def _on_delete_mode(self, _evt):
            if not self._selected_mode:
                return
            name = self._selected_mode
            self._modes, self._active_mode = remove_custom_mode(self._modes, name, self._active_mode)
            self._selected_mode = ""
            self._refresh_mode_list()

        def _on_activate_mode(self, _evt):
            if not self._selected_mode:
                return
            self._active_mode = self._selected_mode
            self._apply_mode_to_settings(self._selected_mode)
            self.modeInfo.SetLabel(f"Mode: {self._selected_mode} (active)")

        def _on_mode_selected(self, _evt):
            self._selected_mode = self.modeList.GetStringSelection().strip()
            self._load_selected_mode()

        def _load_selected_mode(self):
            if not self._selected_mode:
                self.modeHotkeysBtn.Enable(False)
                return
            mode = dict(self._modes.get(self._selected_mode, {}))
            overrides = dict(mode.get("overrides", {}))
            base = str(mode.get("baseProfile", "balanced"))
            if base not in ("beginner", "balanced", "expert"):
                base = "balanced"
            _choice_set_value(self.baseProfile, _PROFILE_CHOICES, base, "balanced")
            self.commandPaletteCheck.SetValue(bool(overrides.get("enable_command_palette", True)))
            self.multiPressCheck.SetValue(bool(overrides.get("enable_multi_press_gestures", True)))
            self.rawSeqCheck.SetValue(True)
            self.contextFallbackCheck.SetValue(bool(overrides.get("enable_contextual_fallbacks", True)))
            self.surfaceAnnounceCheck.SetValue(bool(overrides.get("announce_surface_mode", True)))
            self.globalHotkeysCheck.SetValue(bool(overrides.get("enable_global_hotkeys", True)))
            self.rawTimeout.SetValue(int(overrides.get("raw_easy_sequence_timeout_ms", 900)))
            active_note = _(" (active)") if self._active_mode == self._selected_mode else ""
            self.modeInfo.SetLabel(_("Mode: {mode}{active}").format(mode=self._selected_mode, active=active_note))
            self.modeHotkeysBtn.Enable(get_hotkey_editor_context is not None)

        def _on_save_mode(self, _evt):
            if not self._selected_mode:
                return
            current = dict(self._modes.get(self._selected_mode, {}))
            next_payload = {
                "baseProfile": _choice_get_value(self.baseProfile, _PROFILE_CHOICES, "balanced"),
                "overrides": {
                    "enable_command_palette": bool(self.commandPaletteCheck.GetValue()),
                    "enable_multi_press_gestures": bool(self.multiPressCheck.GetValue()),
                    "enable_raw_easy_sequences": True,
                    "raw_easy_sequence_timeout_ms": int(self.rawTimeout.GetValue()),
                    "enable_contextual_fallbacks": bool(self.contextFallbackCheck.GetValue()),
                    "announce_surface_mode": bool(self.surfaceAnnounceCheck.GetValue()),
                    "enable_global_hotkeys": bool(self.globalHotkeysCheck.GetValue()),
                },
            }
            hotkeys = current.get("hotkeyBindings")
            if isinstance(hotkeys, list):
                next_payload["hotkeyBindings"] = [dict(row) for row in hotkeys if isinstance(row, dict)]
            self._modes = upsert_custom_mode(self._modes, self._selected_mode, next_payload)
            if self._active_mode == self._selected_mode:
                self._apply_mode_to_settings(self._selected_mode)
            self.modeInfo.SetLabel(_("Mode: {mode} saved").format(mode=self._selected_mode))

        def _apply_mode_to_settings(self, mode_name: str):
            mode = dict(self._modes.get(mode_name, {}))
            try:
                from bits_easy_runtime import apply_mode_payload_to_settings

                apply_mode_payload_to_settings(self._settings, mode)
            except Exception:
                overrides = dict(mode.get("overrides", {}))
                self._settings.profile_id = str(mode.get("baseProfile", "balanced"))
                self._settings.enable_command_palette = bool(overrides.get("enable_command_palette", True))
                self._settings.enable_multi_press_gestures = bool(overrides.get("enable_multi_press_gestures", True))
                self._settings.enable_raw_easy_sequences = True
                self._settings.raw_easy_sequence_timeout_ms = int(overrides.get("raw_easy_sequence_timeout_ms", 900))
                self._settings.enable_contextual_fallbacks = bool(overrides.get("enable_contextual_fallbacks", True))
                self._settings.announce_surface_mode = bool(overrides.get("announce_surface_mode", True))
                self._settings.enable_global_hotkeys = bool(overrides.get("enable_global_hotkeys", True))

        def commit(self):
            self._settings.custom_modes = dict(self._modes)
            self._settings.active_mode = str(self._active_mode or "")
            if self._settings.active_mode:
                self._apply_mode_to_settings(self._settings.active_mode)
            set_settings(self._settings)
            settings_store.save(self._settings)

    dialog = ControlPanelDialog()
    try:
        if dialog.ShowModal() != wx.ID_OK:
            return False
        dialog.commit()
        return True
    finally:
        dialog.Destroy()


def register_settings_panel(
    settings_store,
    get_settings: Callable[[], object],
    set_settings: Callable[[object], None],
    open_hotkey_editor: Callable[[], None] | None = None,
    open_control_panel: Callable[[], None] | None = None,
):
    try:
        import gui
        import wx
        from gui.settingsDialogs import NVDASettingsDialog, SettingsPanel
    except Exception:
        log.exception("BITS-EASY: settings panel gui import failed")
        return None

    class BitsEasySettingsPanel(SettingsPanel):
        title = _("BITS-EASY")

        def makeSettings(self, sizer):
            settings = get_settings()

            self.profileChoice = wx.Choice(self, choices=_choice_labels(_PROFILE_CHOICES))
            _choice_set_value(self.profileChoice, _PROFILE_CHOICES, settings.profile_id, "balanced")
            sizer.Add(wx.StaticText(self, label=_("Profile")), border=5, flag=wx.ALL)
            sizer.Add(self.profileChoice, border=5, flag=wx.EXPAND | wx.ALL)

            self.announceSurfaceModeCheck = wx.CheckBox(self, label=_("Announce detected surface mode"))
            self.announceSurfaceModeCheck.SetValue(settings.announce_surface_mode)
            sizer.Add(self.announceSurfaceModeCheck, border=5, flag=wx.ALL)

            self.contextFallbackCheck = wx.CheckBox(self, label=_("Enable contextual fallback steps"))
            self.contextFallbackCheck.SetValue(settings.enable_contextual_fallbacks)
            sizer.Add(self.contextFallbackCheck, border=5, flag=wx.ALL)

            self.commandPaletteCheck = wx.CheckBox(self, label=_("Enable command palette"))
            self.commandPaletteCheck.SetValue(settings.enable_command_palette)
            sizer.Add(self.commandPaletteCheck, border=5, flag=wx.ALL)

            self.globalHotkeysCheck = wx.CheckBox(self, label=_("Enable OS-level global hotkeys"))
            self.globalHotkeysCheck.SetValue(settings.enable_global_hotkeys)
            sizer.Add(self.globalHotkeysCheck, border=5, flag=wx.ALL)

            self.capsEmulationCheck = wx.CheckBox(self, label=_("Emulate CapsLock prefix as Control+Alt for OS hooks"))
            self.capsEmulationCheck.SetValue(settings.emulate_capslock_prefix_for_os_hotkeys)
            sizer.Add(self.capsEmulationCheck, border=5, flag=wx.ALL)

            self.multiPressCheck = wx.CheckBox(self, label=_("Enable multi-press gestures"))
            self.multiPressCheck.SetValue(settings.enable_multi_press_gestures)
            sizer.Add(self.multiPressCheck, border=5, flag=wx.ALL)

            self.betaFeaturesCheck = wx.CheckBox(self, label=_("Enable beta features"))
            self.betaFeaturesCheck.SetValue(bool(getattr(settings, "enable_beta_features", False)))
            sizer.Add(self.betaFeaturesCheck, border=5, flag=wx.ALL)

            self.featureFlagAlertsCheck = wx.CheckBox(self, label=_("Alert me when remote feature flags change"))
            self.featureFlagAlertsCheck.SetValue(bool(getattr(settings, "enable_feature_flag_update_alerts", True)))
            sizer.Add(self.featureFlagAlertsCheck, border=5, flag=wx.ALL)

            self.rawEasySeqCheck = wx.CheckBox(self, label=_("Use EASY key sequences (required)"))
            self.rawEasySeqCheck.SetValue(True)
            self.rawEasySeqCheck.Enable(False)
            sizer.Add(self.rawEasySeqCheck, border=5, flag=wx.ALL)

            timeout_row = wx.BoxSizer(wx.HORIZONTAL)
            timeout_row.Add(wx.StaticText(self, label=_("Raw EASY timeout (ms)")), border=5, flag=wx.ALL)
            self.rawEasyTimeout = wx.SpinCtrl(self, min=250, max=3000)
            self.rawEasyTimeout.SetValue(int(getattr(settings, "raw_easy_sequence_timeout_ms", 900)))
            timeout_row.Add(self.rawEasyTimeout, border=5, flag=wx.ALL)
            sizer.Add(timeout_row, border=0, flag=wx.LEFT)

            self.hotkeyEditorButton = wx.Button(self, label=_("Edit keyboard mappings"))
            self.hotkeyEditorButton.Bind(wx.EVT_BUTTON, self._on_open_hotkey_editor)
            sizer.Add(self.hotkeyEditorButton, border=5, flag=wx.ALL)

            self.controlPanelButton = wx.Button(self, label=_("Open BITS-EASY Control Panel"))
            self.controlPanelButton.Bind(wx.EVT_BUTTON, self._on_open_control_panel)
            sizer.Add(self.controlPanelButton, border=5, flag=wx.ALL)

        def _on_open_hotkey_editor(self, _evt):
            if open_hotkey_editor is not None:
                open_hotkey_editor()

        def _on_open_control_panel(self, _evt):
            if open_control_panel is not None:
                open_control_panel()

        def onSave(self):
            settings = get_settings()
            settings.profile_id = _choice_get_value(self.profileChoice, _PROFILE_CHOICES, "balanced")
            settings.announce_surface_mode = self.announceSurfaceModeCheck.GetValue()
            settings.enable_contextual_fallbacks = self.contextFallbackCheck.GetValue()
            settings.enable_command_palette = self.commandPaletteCheck.GetValue()
            settings.enable_global_hotkeys = self.globalHotkeysCheck.GetValue()
            settings.emulate_capslock_prefix_for_os_hotkeys = self.capsEmulationCheck.GetValue()
            settings.enable_multi_press_gestures = self.multiPressCheck.GetValue()
            settings.enable_beta_features = self.betaFeaturesCheck.GetValue()
            settings.enable_feature_flag_update_alerts = self.featureFlagAlertsCheck.GetValue()
            settings.enable_raw_easy_sequences = True
            settings.raw_easy_sequence_timeout_ms = int(self.rawEasyTimeout.GetValue())
            set_settings(settings)
            settings_store.save(settings)

    NVDASettingsDialog.categoryClasses.append(BitsEasySettingsPanel)
    log.info("BITS-EASY: settings panel registered")
    return BitsEasySettingsPanel


def unregister_settings_panel(panel_class):
    if panel_class is None:
        return
    try:
        from gui.settingsDialogs import NVDASettingsDialog
    except Exception:
        log.exception("BITS-EASY: settings panel gui import failed during unregister")
        return

    if panel_class in NVDASettingsDialog.categoryClasses:
        NVDASettingsDialog.categoryClasses.remove(panel_class)
        log.info("BITS-EASY: settings panel unregistered")

