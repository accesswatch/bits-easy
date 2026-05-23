from __future__ import annotations

from pathlib import Path
import os
import sys
import time
import json

import globalPluginHandler
import scriptHandler
import ui

try:
    from logHandler import log
except Exception:  # pragma: no cover - logHandler is always present inside NVDA
    import logging

    log = logging.getLogger("spellforge.addon")


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = "Spellforge"

    def __init__(self):
        super().__init__()
        log.info("Spellforge: GlobalPlugin __init__ start")
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
        self._hotkey_overrides_path = None
        self._tools_menu_id = None
        self._initialize_runtime()
        log.info("Spellforge: GlobalPlugin __init__ complete")

    def _get_focus_snapshot(self):
        try:
            import api
            from spellforge_runtime import snapshot_from_focus_object

            focus = api.getFocusObject()
            return snapshot_from_focus_object(focus)
        except Exception:
            log.exception("Spellforge: _get_focus_snapshot failed")
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
        # The addon root sits at different depths depending on layout:
        # - Production (installed .nvda-addon): globalPlugins/spellforge.py — addon root is parents[1].
        # - Source repo: addon/globalPlugins/spellforge.py — repo root is parents[2], runtime is under src/.
        # Walk up and add any ancestor (or its src/) that contains the runtime package
        # or the settings helper, so both imports resolve in either layout.
        here = Path(__file__).resolve()
        added: list[str] = []
        seen: set[str] = set()
        for ancestor in here.parents[:4]:
            for candidate in (ancestor, ancestor / "src"):
                try:
                    if not candidate.is_dir():
                        continue
                    has_runtime = (candidate / "spellforge_runtime").is_dir()
                    has_settings = (candidate / "spellforge_settings.py").is_file()
                    if not (has_runtime or has_settings):
                        continue
                    p = str(candidate)
                    if p in seen or p in sys.path:
                        seen.add(p)
                        continue
                    sys.path.insert(0, p)
                    seen.add(p)
                    added.append(p)
                except Exception:
                    pass

        # repo_root is the directory that holds config/hotkeys/ — addon root in
        # production, project root in the source repo. Fall back to parents[1].
        repo_root = next(
            (a for a in here.parents[:4] if (a / "config" / "hotkeys").is_dir()),
            here.parents[1],
        )
        log.info(
            "Spellforge: _initialize_runtime start — __file__=%s, repo_root=%s, sys.path additions=%s",
            here,
            repo_root,
            added,
        )

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
            log.info("Spellforge: storage dir ready at %s", storage_dir)
            storage_path = storage_dir / "clip-slots.json"
            settings_path = storage_dir / "settings.json"
            palette_history_path = storage_dir / "palette-history.json"
            self._hotkey_overrides_path = storage_dir / "hotkey-overrides.json"

            self._settings_store = SettingsStore(settings_path)
            self._settings = self._settings_store.load()
            log.info(
                "Spellforge: settings loaded — profile=%s, global_hotkeys=%s",
                self._settings.profile_id,
                self._settings.enable_global_hotkeys,
            )

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
            log.info("Spellforge: runtime constructed with %d adapters", len(adapters))
            self._config = load_runtime_config(repo_root)
            log.info(
                "Spellforge: runtime config loaded — %d commands, %d bindings",
                len(self._config.command_catalog),
                len(self._config.keymap_bindings),
            )
            self._load_hotkey_overrides()
            self._dispatcher = RuntimeDispatcher(
                runtime=self._runtime,
                config=self._config,
                profile_id=self._settings.profile_id,
            )
            self._dispatcher.multi_press_enabled_override = self._settings.enable_multi_press_gestures
            log.info("Spellforge: dispatcher constructed for profile=%s", self._settings.profile_id)
            self._palette = PaletteEngine(config=self._config, history_path=palette_history_path)
            self._hotkeys = GlobalHotkeyService(
                on_command=self._on_os_hotkey_command,
                emulate_capslock_prefix=self._settings.emulate_capslock_prefix_for_os_hotkeys,
            )
            self._restart_hotkeys()
            log.info("Spellforge: OS hotkey service started")

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
                open_hotkey_editor=self._open_hotkey_editor,
            )
            log.info(
                "Spellforge: settings panel registered=%s",
                self._settings_panel_class is not None,
            )
            self._register_tools_menu_item()
            log.info(
                "Spellforge: tools menu registered=%s",
                self._tools_menu_id is not None,
            )
            log.info("Spellforge: runtime ready, announcing load")
            ui.message("Spellforge loaded")
        except Exception as exc:
            log.exception("Spellforge: failed to load runtime")
            self._runtime = None
            self._dispatcher = None
            self._config = None
            self._settings = None
            self._settings_store = None
            self._settings_panel_class = None
            self._palette = None
            self._hotkeys = None
            self._context = None
            self._tools_menu_id = None
            ui.message(f"Spellforge failed to load: {exc}")

    def _load_hotkey_overrides(self):
        if self._config is None or self._hotkey_overrides_path is None:
            return
        try:
            if not self._hotkey_overrides_path.exists():
                log.info("Spellforge: no hotkey overrides file present, using shipped keymap")
                return
            payload = json.loads(self._hotkey_overrides_path.read_text(encoding="utf-8"))
            bindings = payload.get("bindings", []) if isinstance(payload, dict) else []
            if isinstance(bindings, list) and bindings:
                self._config.keymap_bindings = [dict(row) for row in bindings if isinstance(row, dict)]
                log.info("Spellforge: applied %d hotkey overrides", len(self._config.keymap_bindings))
        except Exception:
            log.exception("Spellforge: loading hotkey overrides failed")

    def _save_hotkey_overrides(self, bindings: list[dict]):
        if self._hotkey_overrides_path is None:
            return
        try:
            self._hotkey_overrides_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {"version": "v1", "bindings": bindings}
            self._hotkey_overrides_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            log.info("Spellforge: saved %d hotkey overrides", len(bindings))
        except Exception:
            log.exception("Spellforge: saving hotkey overrides failed")

    def _register_tools_menu_item(self):
        try:
            import gui
            import wx
        except Exception:
            log.exception("Spellforge: tools menu gui/wx import failed")
            return

        try:
            menu = gui.mainFrame.sysTrayIcon.toolsMenu
            item = menu.Append(wx.ID_ANY, "Spellforge keyboard mappings...")
            self._tools_menu_id = int(item.GetId())
            gui.mainFrame.Bind(wx.EVT_MENU, self._on_tools_menu_open_hotkeys, id=self._tools_menu_id)
        except Exception:
            log.exception("Spellforge: tools menu append failed")
            self._tools_menu_id = None

    def _unregister_tools_menu_item(self):
        if self._tools_menu_id is None:
            return
        try:
            import gui
            import wx

            gui.mainFrame.Unbind(wx.EVT_MENU, handler=self._on_tools_menu_open_hotkeys, id=self._tools_menu_id)
            menu = gui.mainFrame.sysTrayIcon.toolsMenu
            menu.Delete(self._tools_menu_id)
        except Exception:
            log.exception("Spellforge: tools menu unregister failed")
        finally:
            self._tools_menu_id = None

    def _on_tools_menu_open_hotkeys(self, _evt):
        self._open_hotkey_editor()

    def _open_hotkey_editor(self):
        if self._config is None:
            ui.message("Spellforge runtime unavailable")
            return
        try:
            import gui
            from spellforge_settings import open_hotkey_editor_dialog
        except Exception:
            log.exception("Spellforge: hotkey editor import failed")
            ui.message("Hotkey editor is unavailable")
            return

        def _on_save(bindings: list[dict]):
            if self._config is None:
                return
            self._config.keymap_bindings = [dict(row) for row in bindings]
            self._save_hotkey_overrides(self._config.keymap_bindings)
            self._restart_hotkeys()

        changed = open_hotkey_editor_dialog(
            parent=gui.mainFrame,
            keymap_bindings=self._config.keymap_bindings,
            command_catalog=self._config.command_catalog,
            on_save=_on_save,
        )
        if changed:
            ui.message("Keyboard mappings updated.")

    def _on_os_hotkey_command(self, command_id: str, command_args: dict | None = None):
        args = dict(command_args) if isinstance(command_args, dict) else {}

        def _run():
            self._dispatch(command_id, **args)

        try:
            import queueHandler

            queueHandler.queueFunction(queueHandler.eventQueue, _run)
        except Exception:
            log.exception("Spellforge: queueHandler import failed; running OS hotkey inline")
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
        log.info("Spellforge: terminate start")
        try:
            self._unregister_tools_menu_item()
            if self._hotkeys is not None:
                self._hotkeys.stop()
            from spellforge_settings import unregister_settings_panel

            unregister_settings_panel(self._settings_panel_class)
        except Exception:
            log.exception("Spellforge: terminate cleanup failed")
        super().terminate()
        log.info("Spellforge: terminate complete")

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

    def _secure_store_spoken_message(self, payload):
        if not isinstance(payload, dict):
            return "AI key store status is available."

        backend = str(payload.get("backend") or "unknown")
        secure = bool(payload.get("secure", False))
        persistent = bool(payload.get("persistent", False))
        provider_count_raw = payload.get("providerCount", 0)
        try:
            provider_count = int(provider_count_raw)
        except Exception:
            provider_count = 0

        backend_labels = {
            "windows-credential-manager": "Windows Credential Manager",
            "in-memory": "temporary memory",
            "unknown": "an unknown store",
        }
        backend_label = backend_labels.get(backend, backend.replace("-", " "))

        if secure and persistent:
            storage_phrase = "secure and saved between sessions"
            reassurance = "Your keys stay protected after restart."
        elif secure:
            storage_phrase = "secure but temporary"
            reassurance = "Your keys are protected, but may not persist after restart."
        elif persistent:
            storage_phrase = "saved between sessions but not secure"
            reassurance = "Consider using a secure credential backend for provider keys."
        else:
            storage_phrase = "temporary and not secure"
            reassurance = "Keys are only kept for this run and should be treated as temporary."

        provider_label = "provider" if provider_count == 1 else "providers"
        return (
            f"AI key store is {backend_label}. "
            f"Storage is {storage_phrase}. "
            f"{provider_count} {provider_label} configured. "
            f"{reassurance}"
        )

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
            if command_id == "cmd.ai.key.storeStatus":
                ui.message(self._secure_store_spoken_message(out.result.payload))
            else:
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
        except Exception:
            log.exception("Spellforge: command palette wx import failed")
            ui.message("Command palette UI is unavailable")
            return

        ai_key_enabled = False
        key_status = self._dispatcher.dispatch_command(self._context, "cmd.ai.key.status")
        if key_status.result.ok:
            ai_key_enabled = bool((key_status.result.payload or {}).get("hasAnyKey", False))
        has_selection_activity = bool((self._context.clipboard_text or "").strip())

        # wx dialogs must be created and shown on the GUI thread, not NVDA's
        # core thread. Hop over via wx.CallAfter so the script returns
        # immediately and the dialog lifecycle runs where wx requires it.
        wx.CallAfter(self._show_command_palette_ui, ai_key_enabled, has_selection_activity)

    def _show_command_palette_ui(self, ai_key_enabled: bool, has_selection_activity: bool):
        try:
            import wx
            import gui
        except Exception:
            log.exception("Spellforge: command palette wx/gui import failed")
            try:
                ui.message("Command palette UI is unavailable")
            except Exception:
                pass
            return

        main_frame = gui.mainFrame
        main_frame.prePopup()
        try:
            query = ""
            query_dlg = wx.TextEntryDialog(main_frame, "Search commands", "Spellforge Command Palette", "")
            try:
                if query_dlg.ShowModal() == wx.ID_OK:
                    query = query_dlg.GetValue()
                else:
                    return
            finally:
                query_dlg.Destroy()

            ranked = self._palette.search(
                query=query,
                app_id=self._context.app_id,
                limit=30,
                ai_key_enabled=ai_key_enabled,
                has_selection_activity=has_selection_activity,
            )
            if not ranked:
                ui.message("No commands are registered")
                return

            choices = [f"{item.name} [{item.command_id}] score={item.score:.2f}" for item in ranked]
            id_by_index = {idx: item.command_id for idx, item in enumerate(ranked)}

            command_id = ""
            dlg = wx.SingleChoiceDialog(main_frame, "Choose Spellforge command", "Spellforge Command Palette", choices)
            try:
                if dlg.ShowModal() != wx.ID_OK:
                    return
                command_id = id_by_index.get(dlg.GetSelection(), "")
            finally:
                dlg.Destroy()

            if not command_id:
                ui.message("No command selected")
                return

            # Marshal the actual dispatch back to NVDA's event queue so
            # runtime side-effects (clipboard, ui.message) don't run inside
            # the wx event handler.
            try:
                import queueHandler
                queueHandler.queueFunction(queueHandler.eventQueue, self._dispatch, command_id)
            except Exception:
                log.exception("Spellforge: queueHandler unavailable; dispatching inline")
                self._dispatch(command_id)
        except Exception:
            log.exception("Spellforge: command palette UI failed")
            try:
                ui.message("Command palette failed")
            except Exception:
                pass
        finally:
            main_frame.postPopup()

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
        "kb:control+alt+[": "markSelectionStart",
        "kb:control+alt+]": "markSelectionEnd",
        "kb:control+alt+'": "readSelectionContext",
        "kb:control+alt+1": "copyToSlotOne",
        "kb:control+alt+2": "pasteFromSlotOne",
        "kb:control+alt+space": "openCommandPalette",
        "kb:NVDA+shift+p": "openCommandPalette",
    }
