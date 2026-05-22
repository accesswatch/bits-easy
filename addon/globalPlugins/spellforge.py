from __future__ import annotations

from pathlib import Path
import os
import sys
import time

import globalPluginHandler
import scriptHandler
import ui


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = "Spellforge"

    def __init__(self):
        super().__init__()
        self._runtime = None
        self._dispatcher = None
        self._config = None
        self._settings_store = None
        self._settings = None
        self._settings_panel_class = None
        self._palette = None
        self._palette_tick = 0
        self._hotkeys = None
        self._context = None
        self._current_snapshot = None
        self._initialize_runtime()

    def _get_focus_snapshot(self):
        try:
            import api
            from spellforge_runtime import snapshot_from_focus_object

            focus = api.getFocusObject()
            return snapshot_from_focus_object(focus)
        except Exception:
            return None

    def _refresh_context_from_focus(self):
        if self._context is None:
            return

        snapshot = self._get_focus_snapshot()
        self._current_snapshot = snapshot
        if snapshot is None:
            return

        self._context.app_id = snapshot.app_id
        self._context.window_id = snapshot.window_id or self._context.window_id
        self._context.control_id = snapshot.control_id or self._context.control_id
        self._context.buffer = snapshot.text or ""
        self._context.caret = snapshot.caret

    def _initialize_runtime(self):
        repo_root = Path(__file__).resolve().parents[2]
        src_path = repo_root / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))

        try:
            from spellforge_runtime import (
                AppAdapter,
                AppContext,
                BrowserLiveAdapter,
                GlobalHotkeyService,
                PaletteEngine,
                OutlookLiveAdapter,
                RuntimeDispatcher,
                SettingsStore,
                SpellforgeRuntime,
                WordLiveAdapter,
                load_runtime_config,
            )
            from spellforge_settings import register_settings_panel

            storage_dir = Path(os.getenv("APPDATA", str(repo_root))) / "Spellforge"
            storage_dir.mkdir(parents=True, exist_ok=True)
            storage_path = storage_dir / "clip-slots.json"
            settings_path = storage_dir / "settings.json"
            palette_history_path = storage_dir / "palette-history.json"

            self._settings_store = SettingsStore(settings_path)
            self._settings = self._settings_store.load()

            def snapshot_provider():
                return self._get_focus_snapshot()

            adapters = {
                "nvda": AppAdapter("nvda", supports_selection=True),
                "outlook": OutlookLiveAdapter(snapshot_provider=snapshot_provider),
                "word": WordLiveAdapter(snapshot_provider=snapshot_provider),
                "edge": BrowserLiveAdapter("edge", snapshot_provider=snapshot_provider),
                "chrome": BrowserLiveAdapter("chrome", snapshot_provider=snapshot_provider),
                "firefox": BrowserLiveAdapter("firefox", snapshot_provider=snapshot_provider),
            }
            self._runtime = SpellforgeRuntime(adapters=adapters, storage_path=storage_path)
            self._config = load_runtime_config(repo_root)
            self._dispatcher = RuntimeDispatcher(
                runtime=self._runtime,
                config=self._config,
                profile_id=self._settings.profile_id,
            )
            self._dispatcher.multi_press_enabled_override = self._settings.enable_multi_press_gestures
            self._palette = PaletteEngine(config=self._config, history_path=palette_history_path)
            self._hotkeys = GlobalHotkeyService(
                on_command=self._on_os_hotkey_command,
                emulate_capslock_prefix=self._settings.emulate_capslock_prefix_for_os_hotkeys,
            )
            self._restart_hotkeys()

            focus_snapshot = self._get_focus_snapshot()
            app_id = "nvda"
            window_id = "nvda-window"
            control_id = "focus"
            buffer = ""
            caret = 0
            if focus_snapshot is not None:
                app_id = focus_snapshot.app_id or app_id
                window_id = focus_snapshot.window_id or window_id
                control_id = focus_snapshot.control_id or control_id
                buffer = focus_snapshot.text or ""
                caret = focus_snapshot.caret

            self._context = AppContext(
                app_id=app_id,
                window_id=window_id,
                control_id=control_id,
                buffer=buffer,
                caret=caret,
                clipboard_text="",
            )

            self._settings_panel_class = register_settings_panel(
                settings_store=self._settings_store,
                get_settings=self._get_settings,
                set_settings=self._set_settings,
            )
            ui.message("Spellforge loaded")
        except Exception as exc:
            self._runtime = None
            self._dispatcher = None
            self._config = None
            self._settings = None
            self._settings_store = None
            self._settings_panel_class = None
            self._palette = None
            self._hotkeys = None
            self._context = None
            ui.message(f"Spellforge failed to load: {exc}")

    def _on_os_hotkey_command(self, command_id: str):
        def _run():
            self._dispatch(command_id)

        try:
            import queueHandler

            queueHandler.queueFunction(queueHandler.eventQueue, _run)
        except Exception:
            _run()

    def _restart_hotkeys(self):
        if self._hotkeys is None or self._config is None:
            return

        self._hotkeys.stop()
        if self._settings and self._settings.enable_global_hotkeys:
            self._hotkeys = type(self._hotkeys)(
                on_command=self._on_os_hotkey_command,
                emulate_capslock_prefix=self._settings.emulate_capslock_prefix_for_os_hotkeys,
            )
            self._hotkeys.start(self._config.keymap_bindings)

    def terminate(self):
        try:
            if self._hotkeys is not None:
                self._hotkeys.stop()
            from spellforge_settings import unregister_settings_panel

            unregister_settings_panel(self._settings_panel_class)
        except Exception:
            pass
        super().terminate()

    def _get_settings(self):
        return self._settings

    def _set_settings(self, settings):
        self._settings = settings
        if self._dispatcher is not None:
            self._dispatcher.profile_id = settings.profile_id
            self._dispatcher.multi_press_enabled_override = settings.enable_multi_press_gestures
        self._restart_hotkeys()

    def _surface_mode(self):
        if self._current_snapshot is None:
            return "generic"
        from spellforge_runtime import classify_surface

        surface = classify_surface(
            app_id=self._current_snapshot.app_id,
            role=self._current_snapshot.role,
            control_id=self._current_snapshot.control_id,
        )
        return surface.mode

    def _contextual_fallbacks(self, command_id: str):
        if not self._settings or not self._settings.enable_contextual_fallbacks:
            return []

        from spellforge_runtime import fallback_steps_for

        return fallback_steps_for(self._surface_mode(), command_id)

    def _dispatch(self, command_id: str, **kwargs):
        if self._dispatcher is None or self._context is None:
            ui.message("Spellforge runtime unavailable")
            return

        self._refresh_context_from_focus()

        if self._settings and self._settings.announce_surface_mode:
            ui.message(f"Surface: {self._surface_mode()}")

        out = self._dispatcher.dispatch_command(self._context, command_id, **kwargs)
        if out.result.ok:
            if self._palette is not None:
                self._palette_tick += 1
                self._palette.record_execution(command_id, int(time.time()) + self._palette_tick)
            ui.message(out.result.message)
        else:
            extra_steps = self._contextual_fallbacks(command_id)
            steps = out.result.next_steps + extra_steps
            ui.message(f"{out.result.message}. {' '.join(steps)}")

    @scriptHandler.script(description="Spellforge command palette")
    def script_openCommandPalette(self, gesture):
        if self._dispatcher is None or self._context is None or self._config is None or self._palette is None:
            ui.message("Spellforge runtime unavailable")
            return
        if self._settings and not self._settings.enable_command_palette:
            ui.message("Spellforge command palette is disabled in settings")
            return

        try:
            import wx
            import gui
        except Exception:
            ui.message("Command palette UI is unavailable")
            return

        query_dlg = wx.TextEntryDialog(gui.mainFrame, "Search commands", "Spellforge Command Palette", "")
        query = ""
        try:
            if query_dlg.ShowModal() == wx.ID_OK:
                query = query_dlg.GetValue()
        finally:
            query_dlg.Destroy()

        ranked = self._palette.search(query=query, app_id=self._context.app_id, limit=30)
        if not ranked:
            ui.message("No commands are registered")
            return

        choices = [f"{item.name} [{item.command_id}] score={item.score:.2f}" for item in ranked]
        id_by_index = {idx: item.command_id for idx, item in enumerate(ranked)}

        dlg = wx.SingleChoiceDialog(gui.mainFrame, "Choose Spellforge command", "Spellforge Command Palette", choices)
        try:
            if dlg.ShowModal() != wx.ID_OK:
                return
            command_id = id_by_index.get(dlg.GetSelection(), "")
            if not command_id:
                ui.message("No command selected")
                return
            self._dispatch(command_id)
        finally:
            dlg.Destroy()

    @scriptHandler.script(description="Spellforge mark selection start")
    def script_markSelectionStart(self, gesture):
        self._dispatch("cmd.selection.markStart")

    @scriptHandler.script(description="Spellforge mark selection end")
    def script_markSelectionEnd(self, gesture):
        self._dispatch("cmd.selection.markEnd")

    @scriptHandler.script(description="Spellforge read selection context")
    def script_readSelectionContext(self, gesture):
        self._dispatch("cmd.selection.readContext")

    @scriptHandler.script(description="Spellforge copy to clip slot 1")
    def script_copyToSlotOne(self, gesture):
        self._dispatch("cmd.clip.copyToSlot", slot=1)

    @scriptHandler.script(description="Spellforge paste from clip slot 1")
    def script_pasteFromSlotOne(self, gesture):
        self._dispatch("cmd.clip.pasteFromSlot", slot=1)

    __gestures = {
        "kb:NVDA+[": "markSelectionStart",
        "kb:NVDA+]": "markSelectionEnd",
        "kb:NVDA+'": "readSelectionContext",
        "kb:NVDA+1": "copyToSlotOne",
        "kb:NVDA+2": "pasteFromSlotOne",
        "kb:NVDA+shift+p": "openCommandPalette",
    }
