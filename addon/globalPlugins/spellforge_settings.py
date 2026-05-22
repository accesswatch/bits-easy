from __future__ import annotations

from typing import Callable


def register_settings_panel(settings_store, get_settings: Callable[[], object], set_settings: Callable[[object], None]):
    try:
        import gui
        import wx
        from gui.settingsDialogs import NVDASettingsDialog, SettingsPanel
    except Exception:
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
    return SpellforgeSettingsPanel


def unregister_settings_panel(panel_class):
    if panel_class is None:
        return
    try:
        from gui.settingsDialogs import NVDASettingsDialog
    except Exception:
        return

    if panel_class in NVDASettingsDialog.categoryClasses:
        NVDASettingsDialog.categoryClasses.remove(panel_class)
