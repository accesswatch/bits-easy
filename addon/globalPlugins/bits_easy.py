from __future__ import annotations

from pathlib import Path
import os
import sys
import time
import json
import importlib

import addonHandler
import globalPluginHandler
import scriptHandler
import ui

addonHandler.initTranslation()

if "_" not in globals():
    def _(message: str) -> str:
        return message


def _format_message(template: str, **kwargs) -> str:
    return str(template).format(**kwargs)

try:
    from logHandler import log
except Exception:  # pragma: no cover - logHandler is always present inside NVDA
    import logging

    log = logging.getLogger("bits_easy.addon")


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    # Translators: Category name shown in NVDA's Input Gestures dialog.
    scriptCategory = _("BITS-EASY")

    _GLOW_FILE_COMMANDS = {
        "cmd.integration.glow.audit",
        "cmd.integration.glow.fix",
        "cmd.integration.glow.convert",
        "cmd.integration.glow.report",
    }

    _GLOW_COMMANDS = {
        "cmd.integration.glow.health",
        "cmd.integration.glow.audit",
        "cmd.integration.glow.fix",
        "cmd.integration.glow.convert",
        "cmd.integration.glow.report",
    }

    def __init__(self):
        super().__init__()
        log.info("BITS-EASY: GlobalPlugin __init__ start")
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
        self._base_keymap_bindings = []
        self._tools_menu_id = None
        self._quick_select_armed = False
        self._typed_word_buffer = ""
        self._trigger_expand_enabled = True
        self._initialize_runtime()
        log.info("BITS-EASY: GlobalPlugin __init__ complete")

    def _read_clipboard_text(self) -> str:
        try:
            import wx
        except Exception:
            return ""

        text = ""
        if wx.TheClipboard.Open():
            try:
                data = wx.TextDataObject()
                if wx.TheClipboard.GetData(data):
                    text = data.GetText() or ""
            finally:
                wx.TheClipboard.Close()
        return str(text)

    def _write_clipboard_text(self, text: str) -> bool:
        try:
            import wx
        except Exception:
            return False

        ok = False
        if wx.TheClipboard.Open():
            try:
                ok = wx.TheClipboard.SetData(wx.TextDataObject(str(text or "")))
            finally:
                wx.TheClipboard.Close()
        return bool(ok)

    def _apply_payload_clipboard_side_effects(self, payload) -> str:
        if not isinstance(payload, dict):
            return ""

        if "clipboardWriteText" not in payload:
            return ""

        target = str(payload.get("clipboardWriteText", ""))
        if not self._write_clipboard_text(target):
            return _("Clipboard unavailable")

        if self._context is not None:
            self._context.clipboard_text = target
        return ""

    def _get_focus_snapshot(self):
        try:
            import api
            from bits_easy_runtime import snapshot_from_focus_object

            focus = api.getFocusObject()
            return snapshot_from_focus_object(focus)
        except Exception:
            log.exception("BITS-EASY: _get_focus_snapshot failed")
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
        self._context.clipboard_text = self._read_clipboard_text()

    def _initialize_runtime(self):
        # The addon root sits at different depths depending on layout:
        # - Production (installed .nvda-addon): globalPlugins/bits_easy.py — addon root is parents[1].
        # - Source repo: addon/globalPlugins/bits_easy.py — repo root is parents[2], runtime is under src/.
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
                    has_runtime = (candidate / "bits_easy_runtime").is_dir()
                    has_settings = (candidate / "bits_easy_settings.py").is_file()
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
            "BITS-EASY: _initialize_runtime start — __file__=%s, repo_root=%s, sys.path additions=%s",
            here,
            repo_root,
            added,
        )

        try:
            from bits_easy_runtime import (
                AppAdapter,
                AppContext,
                BrowserLiveAdapter,
                GlobalHotkeyService,
                PaletteEngine,
                OutlookLiveAdapter,
                RuntimeDispatcher,
                SettingsStore,
                BitsEasyRuntime,
                apply_active_mode,
                effective_keymap_bindings,
                WordLiveAdapter,
                load_runtime_config,
            )
            from bits_easy_settings import register_settings_panel

            storage_root = Path(os.getenv("APPDATA", str(repo_root)))
            storage_dir = storage_root / "BITS-EASY"
            legacy_storage_dir = storage_root / "BITS-EASY"
            if not storage_dir.exists() and legacy_storage_dir.exists():
                storage_dir = legacy_storage_dir
            storage_dir.mkdir(parents=True, exist_ok=True)
            log.info("BITS-EASY: storage dir ready at %s", storage_dir)
            storage_path = storage_dir / "clip-slots.json"
            settings_path = storage_dir / "settings.json"
            palette_history_path = storage_dir / "palette-history.json"
            self._hotkey_overrides_path = storage_dir / "hotkey-overrides.json"

            self._settings_store = SettingsStore(settings_path)
            self._settings = self._settings_store.load()
            log.info(
                "BITS-EASY: settings loaded — profile=%s, global_hotkeys=%s",
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
                "notepad": BrowserLiveAdapter("notepad", snapshot_provider=snapshot_provider),
                "vscode": BrowserLiveAdapter("vscode", snapshot_provider=snapshot_provider),
            }
            self._runtime = BitsEasyRuntime(adapters=adapters, storage_path=storage_path)
            log.info("BITS-EASY: runtime constructed with %d adapters", len(adapters))
            self._config = load_runtime_config(repo_root)
            log.info(
                "BITS-EASY: runtime config loaded — %d commands, %d bindings",
                len(self._config.command_catalog),
                len(self._config.keymap_bindings),
            )
            self._load_hotkey_overrides()
            self._base_keymap_bindings = [dict(row) for row in self._config.keymap_bindings if isinstance(row, dict)]
            mode_hotkey_bindings = apply_active_mode(self._settings)
            self._config.keymap_bindings = effective_keymap_bindings(self._base_keymap_bindings, mode_hotkey_bindings)
            self._dispatcher = RuntimeDispatcher(
                runtime=self._runtime,
                config=self._config,
                profile_id=self._settings.profile_id,
            )
            self._dispatcher.multi_press_enabled_override = self._settings.enable_multi_press_gestures
            self._dispatcher.set_beta_features_enabled(bool(getattr(self._settings, "enable_beta_features", False)))
            self._maybe_offer_feature_flag_updates(self._dispatcher.latest_feature_flag_refresh())
            log.info("BITS-EASY: dispatcher constructed for profile=%s", self._settings.profile_id)
            self._palette = PaletteEngine(config=self._config, history_path=palette_history_path)
            self._hotkeys = GlobalHotkeyService(
                on_command=self._on_os_hotkey_command,
                emulate_capslock_prefix=self._settings.emulate_capslock_prefix_for_os_hotkeys,
                on_key_chord=self._on_os_hotkey_chord,
                enable_raw_sequences=True,
                raw_sequence_timeout_ms=self._settings.raw_easy_sequence_timeout_ms,
            )
            self._restart_hotkeys()
            log.info("BITS-EASY: OS hotkey service started")

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
                clipboard_text=self._read_clipboard_text(),
            )

            self._settings_panel_class = register_settings_panel(
                settings_store=self._settings_store,
                get_settings=self._get_settings,
                set_settings=self._set_settings,
                open_hotkey_editor=self._open_hotkey_editor,
                open_control_panel=self._open_control_panel,
            )
            log.info(
                "BITS-EASY: settings panel registered=%s",
                self._settings_panel_class is not None,
            )
            self._register_tools_menu_item()
            log.info(
                "BITS-EASY: tools menu registered=%s",
                self._tools_menu_id is not None,
            )
            log.info("BITS-EASY: runtime ready, announcing load")
            self._announce_text(_("BITS-EASY loaded"))
        except Exception as exc:
            log.exception("BITS-EASY: failed to load runtime")
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
            self._announce_text(
                _format_message(
                    # Translators: Announced if the add-on fails to initialize.
                    _("BITS-EASY failed to load: {error}"),
                    error=exc,
                )
            )

    def _announce_text(self, speech_text: str, braille_text: str | None = None):
        speech_value = str(speech_text or "").strip()
        braille_value = str(braille_text or "").strip()
        if not speech_value and not braille_value:
            return
        if not speech_value:
            speech_value = braille_value
        if not braille_value:
            braille_value = speech_value

        try:
            if braille_value != speech_value:
                try:
                    ui.message(speech_value, None, braille_value)
                    return
                except TypeError:
                    pass
            ui.message(speech_value)
        except Exception:
            log.exception("BITS-EASY: ui.message failed")

    def _announce_result_message(self, default_message: str, payload):
        narration = payload.get("narration") if isinstance(payload, dict) else None
        if not isinstance(narration, dict):
            self._announce_text(default_message)
            return

        speech_text = str(narration.get("speechMessage") or default_message or "").strip()
        braille_text = str(narration.get("brailleMessage") or speech_text or "").strip()
        self._announce_text(speech_text, braille_text)

    def _show_browseable_text(self, title: str, text: str):
        try:
            ui.browseableMessage(text, title)
            return
        except Exception:
            log.exception("BITS-EASY: browseableMessage failed, falling back to dialog")

        try:
            import wx

            wx.CallAfter(self._show_text_dialog, title, text)
        except Exception:
            log.exception("BITS-EASY: unable to schedule fallback text dialog")

    def _present_virtual_view(self, payload):
        if not isinstance(payload, dict):
            return False
        virtual = payload.get("virtualView")
        if not isinstance(virtual, dict):
            return False

        title = str(virtual.get("title", "")).strip() or _("BITS-EASY")
        lines = virtual.get("lines", [])
        if not isinstance(lines, list):
            return False
        text = "\n".join(str(line) for line in lines).strip()
        if not text:
            return False
        self._show_browseable_text(title, text)
        return True

    def _load_hotkey_overrides(self):
        if self._config is None or self._hotkey_overrides_path is None:
            return
        try:
            if not self._hotkey_overrides_path.exists():
                log.info("BITS-EASY: no hotkey overrides file present, using shipped keymap")
                return
            payload = json.loads(self._hotkey_overrides_path.read_text(encoding="utf-8"))
            bindings = payload.get("bindings", []) if isinstance(payload, dict) else []
            if isinstance(bindings, list) and bindings:
                self._config.keymap_bindings = [dict(row) for row in bindings if isinstance(row, dict)]
                log.info("BITS-EASY: applied %d hotkey overrides", len(self._config.keymap_bindings))
        except Exception:
            log.exception("BITS-EASY: loading hotkey overrides failed")

    def _save_hotkey_overrides(self, bindings: list[dict]):
        if self._hotkey_overrides_path is None:
            return
        try:
            self._hotkey_overrides_path.parent.mkdir(parents=True, exist_ok=True)
            payload = {"version": "v1", "bindings": bindings}
            self._hotkey_overrides_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            log.info("BITS-EASY: saved %d hotkey overrides", len(bindings))
        except Exception:
            log.exception("BITS-EASY: saving hotkey overrides failed")

    def _register_tools_menu_item(self):
        try:
            import gui
            import wx
        except Exception:
            log.exception("BITS-EASY: tools menu gui/wx import failed")
            return

        try:
            menu = gui.mainFrame.sysTrayIcon.toolsMenu
            item = menu.Append(
                wx.ID_ANY,
                # Translators: Tools menu label that opens the keyboard mapping editor.
                _("BITS-EASY keyboard mappings..."),
            )
            self._tools_menu_id = int(item.GetId())
            gui.mainFrame.Bind(wx.EVT_MENU, self._on_tools_menu_open_hotkeys, id=self._tools_menu_id)
        except Exception:
            log.exception("BITS-EASY: tools menu append failed")
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
            log.exception("BITS-EASY: tools menu unregister failed")
        finally:
            self._tools_menu_id = None

    def _on_tools_menu_open_hotkeys(self, _evt):
        self._open_hotkey_editor()

    def _open_hotkey_editor(self):
        if self._config is None:
            self._announce_text(_("BITS-EASY runtime unavailable"))
            return
        try:
            import gui
            from bits_easy_settings import open_hotkey_editor_dialog
        except Exception:
            log.exception("BITS-EASY: hotkey editor import failed")
            self._announce_text(_("Hotkey editor is unavailable"))
            return

        def _on_save(bindings: list[dict]):
            if self._config is None:
                return
            self._base_keymap_bindings = [dict(row) for row in bindings if isinstance(row, dict)]
            self._save_hotkey_overrides(self._base_keymap_bindings)
            self._apply_active_mode_resolution()
            self._restart_hotkeys()

        changed = open_hotkey_editor_dialog(
            parent=gui.mainFrame,
            keymap_bindings=self._config.keymap_bindings,
            command_catalog=self._config.command_catalog,
            on_save=_on_save,
        )
        if changed:
            self._announce_text(_("Keyboard mappings updated."))

    def _open_control_panel(self):
        try:
            import gui
            from bits_easy_settings import open_control_panel_dialog
        except Exception:
            log.exception("BITS-EASY: control panel import failed")
            self._announce_text(_("Control panel is unavailable"))
            return

        changed = open_control_panel_dialog(
            parent=gui.mainFrame,
            settings_store=self._settings_store,
            get_settings=self._get_settings,
            set_settings=self._set_settings,
            open_hotkey_editor=self._open_hotkey_editor,
            get_hotkey_editor_context=lambda: (
                [dict(row) for row in (self._base_keymap_bindings or self._config.keymap_bindings) if isinstance(row, dict)],
                dict(self._config.command_catalog or {}),
            ),
        )
        if changed:
            self._restart_hotkeys()
            self._announce_text(_("Control panel settings applied."))

    def _on_os_hotkey_command(self, command_id: str, command_args: dict | None = None):
        args = dict(command_args) if isinstance(command_args, dict) else {}

        def _run():
            self._dispatch(command_id, **args)

        try:
            import queueHandler

            queueHandler.queueFunction(queueHandler.eventQueue, _run)
        except Exception:
            log.exception("BITS-EASY: queueHandler import failed; running OS hotkey inline")
            _run()

    def _on_os_hotkey_chord(self, key_chord: str, command_args: dict | None = None):
        args = dict(command_args) if isinstance(command_args, dict) else {}

        def _run():
            if self._dispatcher is None or self._context is None:
                return
            self._refresh_context_from_focus()
            out = self._dispatcher.dispatch_key_chord(self._context, key_chord, **args)
            if out.result.ok:
                if out.plan.command_id == "cmd.selection.markStart":
                    self._quick_select_armed = True
                elif out.plan.command_id in ("cmd.selection.markEnd", "cmd.selection.cancel", "cmd.selection.markEndAppendClipboard"):
                    self._quick_select_armed = False

                clip_error = self._apply_payload_clipboard_side_effects(out.result.payload)
                if clip_error:
                    self._announce_text(clip_error)
                    return

                integration_error = self._run_integration_action(out.result.payload)
                if integration_error:
                    self._announce_text(integration_error)
                    return
                self._present_glow_result_if_needed(out.plan.command_id, out.result.message, out.result.payload)
                self._present_hotkey_help_if_needed(out.plan.command_id, out.result.payload)
                self._present_virtual_view_if_needed(out.plan.command_id, out.result.payload)
                self._announce_result_message(out.result.message, out.result.payload)
            else:
                self._announce_result_message(out.result.message, out.result.payload)

        try:
            import queueHandler

            queueHandler.queueFunction(queueHandler.eventQueue, _run)
        except Exception:
            log.exception("BITS-EASY: queueHandler import failed; running OS hotkey chord inline")
            _run()

    def _restart_hotkeys(self):
        if self._hotkeys is None or self._config is None:
            return

        self._hotkeys.stop()
        if self._settings and self._settings.enable_global_hotkeys:
            self._hotkeys = type(self._hotkeys)(
                on_command=self._on_os_hotkey_command,
                emulate_capslock_prefix=self._settings.emulate_capslock_prefix_for_os_hotkeys,
                on_key_chord=self._on_os_hotkey_chord,
                enable_raw_sequences=True,
                raw_sequence_timeout_ms=self._settings.raw_easy_sequence_timeout_ms,
            )
            bindings = self._config.keymap_bindings
            if self._dispatcher is not None:
                try:
                    bindings = self._dispatcher.enabled_keymap_bindings(bindings)
                except Exception:
                    log.exception("BITS-EASY: feature flag hotkey filtering failed")
            self._hotkeys.start(bindings)

    def terminate(self):
        log.info("BITS-EASY: terminate start")
        try:
            self._unregister_tools_menu_item()
            if self._hotkeys is not None:
                self._hotkeys.stop()
            from bits_easy_settings import unregister_settings_panel

            unregister_settings_panel(self._settings_panel_class)
        except Exception:
            log.exception("BITS-EASY: terminate cleanup failed")
        super().terminate()
        log.info("BITS-EASY: terminate complete")

    def _get_settings(self):
        return self._settings

    def _apply_active_mode_resolution(self):
        if self._settings is None:
            return

        mode_hotkey_bindings = None
        try:
            from bits_easy_runtime import apply_active_mode, effective_keymap_bindings

            mode_hotkey_bindings = apply_active_mode(self._settings)
            if self._config is not None:
                base = self._base_keymap_bindings or self._config.keymap_bindings
                self._config.keymap_bindings = effective_keymap_bindings(base, mode_hotkey_bindings)
        except Exception:
            log.exception("BITS-EASY: active mode resolution failed")

        if self._dispatcher is not None:
            self._dispatcher.profile_id = self._settings.profile_id
            self._dispatcher.multi_press_enabled_override = self._settings.enable_multi_press_gestures
            self._dispatcher.set_beta_features_enabled(bool(getattr(self._settings, "enable_beta_features", False)))

    def _set_settings(self, settings):
        old_settings = self._settings
        self._settings = settings
        self._apply_active_mode_resolution()
        self._restart_hotkeys()

        was_beta_enabled = bool(getattr(old_settings, "enable_beta_features", False))
        now_beta_enabled = bool(getattr(self._settings, "enable_beta_features", False))
        had_alerts = bool(getattr(old_settings, "enable_feature_flag_update_alerts", True))
        has_alerts = bool(getattr(self._settings, "enable_feature_flag_update_alerts", True))
        if self._dispatcher is not None and now_beta_enabled and has_alerts and (not was_beta_enabled or not had_alerts):
            refresh = self._dispatcher.refresh_feature_flags(timeout_seconds=1.0)
            self._maybe_offer_feature_flag_updates(refresh)

    def _maybe_offer_feature_flag_updates(self, refresh_result):
        if self._dispatcher is None or self._settings is None or refresh_result is None:
            return
        if not bool(getattr(self._settings, "enable_beta_features", False)):
            return
        if not bool(getattr(self._settings, "enable_feature_flag_update_alerts", True)):
            return

        payload = refresh_result.payload or {}
        if not bool(payload.get("updatesAvailable", False)):
            return

        changes = payload.get("changes", {}) if isinstance(payload.get("changes", {}), dict) else {}
        new_flags = changes.get("newFlags", []) if isinstance(changes.get("newFlags", []), list) else []
        changed_flags = changes.get("changedFlags", []) if isinstance(changes.get("changedFlags", []), list) else []
        candidate_ids = sorted(
            {
                str(row.get("id", "")).strip()
                for row in (new_flags + changed_flags)
                if isinstance(row, dict) and str(row.get("id", "")).strip()
            }
        )
        if not candidate_ids:
            return

        source = str(payload.get("source", "remote"))
        prompt = _format_message(
            _(
                "BITS-EASY found {newCount} new and {changedCount} updated feature flags from {source}. "
                "Enable these updated flags now?"
            ),
            newCount=len(new_flags),
            changedCount=len(changed_flags),
            source=source,
        )

        try:
            import wx

            response = wx.MessageBox(
                prompt,
                _("BITS-EASY Feature Flag Updates"),
                style=wx.YES_NO | wx.ICON_QUESTION | wx.YES_DEFAULT,
            )
            if response != wx.YES:
                self._announce_text(_("Feature flag updates left disabled."))
                return
        except Exception:
            log.exception("BITS-EASY: failed to show feature flag update prompt")
            return

        apply_result = self._dispatcher.set_feature_flags_enabled(candidate_ids, enabled=True)
        if not apply_result.ok:
            self._announce_text(_("Could not enable updated feature flags."))
            return

        self._restart_hotkeys()
        self._announce_text(
            _format_message(
                _("Enabled {count} updated feature flags."),
                count=len(candidate_ids),
            )
        )

    def _surface_mode(self):
        if self._current_snapshot is None:
            return "generic"
        from bits_easy_runtime import classify_surface

        surface = classify_surface(
            app_id=self._current_snapshot.app_id,
            role=self._current_snapshot.role,
            control_id=self._current_snapshot.control_id,
        )
        return surface.mode

    def _contextual_fallbacks(self, command_id: str):
        if not self._settings or not self._settings.enable_contextual_fallbacks:
            return []

        from bits_easy_runtime import fallback_steps_for

        return fallback_steps_for(self._surface_mode(), command_id)

    def _secure_store_spoken_message(self, payload):
        if not isinstance(payload, dict):
            return _("AI key store status is available.")

        backend = str(payload.get("backend") or "unknown")
        secure = bool(payload.get("secure", False))
        persistent = bool(payload.get("persistent", False))
        provider_count_raw = payload.get("providerCount", 0)
        try:
            provider_count = int(provider_count_raw)
        except Exception:
            provider_count = 0

        backend_labels = {
            "windows-credential-manager": _("Windows Credential Manager"),
            "in-memory": _("temporary memory"),
            "unknown": _("an unknown store"),
        }
        backend_label = backend_labels.get(backend, backend.replace("-", " "))

        if secure and persistent:
            storage_phrase = _("secure and saved between sessions")
            reassurance = _("Your keys stay protected after restart.")
        elif secure:
            storage_phrase = _("secure but temporary")
            reassurance = _("Your keys are protected, but may not persist after restart.")
        elif persistent:
            storage_phrase = _("saved between sessions but not secure")
            reassurance = _("Consider using a secure credential backend for provider keys.")
        else:
            storage_phrase = _("temporary and not secure")
            reassurance = _("Keys are only kept for this run and should be treated as temporary.")

        provider_label = _("provider") if provider_count == 1 else _("providers")
        return _format_message(
            _("AI key store is {backend}. Storage is {storage}. {count} {providerLabel} configured. {reassurance}"),
            backend=backend_label,
            storage=storage_phrase,
            count=provider_count,
            providerLabel=provider_label,
            reassurance=reassurance,
        )

    def _dispatch(self, command_id: str, **kwargs):
        if self._dispatcher is None or self._context is None:
            self._announce_text(_("BITS-EASY runtime unavailable"))
            return

        if self._prompt_glow_file_if_needed(command_id, kwargs):
            return

        self._refresh_context_from_focus()

        if self._settings and self._settings.announce_surface_mode:
            self._announce_text(
                _format_message(
                    # Translators: Announces the detected interaction surface before a command runs.
                    _("Surface: {surfaceMode}"),
                    surfaceMode=self._surface_mode(),
                )
            )

        out = self._dispatcher.dispatch_command(self._context, command_id, **kwargs)
        if out.result.ok:
            if command_id == "cmd.selection.markStart":
                self._quick_select_armed = True
            elif command_id in ("cmd.selection.markEnd", "cmd.selection.cancel", "cmd.selection.markEndAppendClipboard"):
                self._quick_select_armed = False

            clip_error = self._apply_payload_clipboard_side_effects(out.result.payload)
            if clip_error:
                self._announce_text(clip_error)
                return

            integration_error = self._run_integration_action(out.result.payload)
            if integration_error:
                self._announce_text(integration_error)
                return
            self._present_glow_result_if_needed(command_id, out.result.message, out.result.payload)
            self._present_hotkey_help_if_needed(command_id, out.result.payload)
            self._present_virtual_view_if_needed(command_id, out.result.payload)
            if self._palette is not None:
                self._palette_tick += 1
                self._palette.record_execution(command_id, int(time.time()) + self._palette_tick)
            if command_id == "cmd.ai.key.storeStatus":
                self._announce_text(self._secure_store_spoken_message(out.result.payload))
            else:
                self._announce_result_message(out.result.message, out.result.payload)
        else:
            extra_steps = self._contextual_fallbacks(command_id)
            steps = out.result.next_steps + extra_steps
            if steps:
                self._announce_text(
                    _format_message(
                        # Translators: Spoken after a failed command with suggested recovery steps.
                        _("{message}. {steps}"),
                        message=out.result.message,
                        steps=" ".join(steps),
                    )
                )
            else:
                self._announce_result_message(out.result.message, out.result.payload)

    def _present_virtual_view_if_needed(self, command_id: str, payload):
        if command_id == "cmd.help.availableHotkeys":
            return
        self._present_virtual_view(payload)

    def _present_hotkey_help_if_needed(self, command_id: str, payload):
        if command_id != "cmd.help.availableHotkeys":
            return
        self._present_virtual_view(payload)

    def _show_text_dialog(self, title: str, text: str):
        try:
            import wx
            import gui
        except Exception:
            log.exception("BITS-EASY: text dialog dependencies unavailable")
            return

        main_frame = gui.mainFrame
        main_frame.prePopup()
        try:
            dlg = wx.Dialog(
                main_frame,
                title=title,
                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
            )
            try:
                root = wx.BoxSizer(wx.VERTICAL)
                box = wx.TextCtrl(
                    dlg,
                    value=text,
                    style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL,
                )
                box.SetMinSize((860, 460))
                root.Add(box, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

                close_btn = wx.Button(dlg, id=wx.ID_OK, label=_("Close"))
                row = wx.BoxSizer(wx.HORIZONTAL)
                row.Add(close_btn, flag=wx.RIGHT, border=8)
                root.Add(row, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
                dlg.SetSizer(root)
                dlg.CentreOnScreen()
                dlg.ShowModal()
            finally:
                dlg.Destroy()
        except Exception:
            log.exception("BITS-EASY: text dialog failed")
        finally:
            main_frame.postPopup()

    def _present_glow_result_if_needed(self, command_id: str, message: str, payload):
        if command_id not in self._GLOW_COMMANDS:
            return
        if not isinstance(payload, dict):
            return

        summary = self._glow_summary_message(command_id, message, payload)
        if summary:
            self._announce_text(summary)

        try:
            import wx

            wx.CallAfter(self._show_glow_result_dialog, command_id, message, dict(payload))
        except Exception:
            log.exception("BITS-EASY: unable to schedule GLOW result dialog")

    @staticmethod
    def _glow_output_path(payload: dict) -> str:
        if not isinstance(payload, dict):
            return ""
        for key in ("output_file", "fixed_file", "outputFile", "fixedFile"):
            val = str(payload.get(key, "")).strip()
            if val:
                return val
        return ""

    def _glow_summary_message(self, command_id: str, message: str, payload: dict) -> str:
        summary_parts = [_format_message(_("GLOW {action} complete"), action=command_id.split(".")[-1])]

        if command_id == "cmd.integration.glow.health":
            status = str(payload.get("status", "")).strip()
            if status:
                summary_parts.append(_format_message(_("status {status}"), status=status))
            return ". ".join(summary_parts) + "."

        total_fixes = payload.get("total_fixes")
        if isinstance(total_fixes, int):
            summary_parts.append(_format_message(_("{count} fixes"), count=total_fixes))

        out_path = self._glow_output_path(payload)
        if out_path:
            try:
                out_name = Path(out_path).name
            except Exception:
                out_name = out_path
            if out_name:
                summary_parts.append(_format_message(_("output {name}"), name=out_name))

        report_text = payload.get("report")
        if isinstance(report_text, str) and report_text.strip():
            summary_parts.append(
                _format_message(_("report length {count} characters"), count=len(report_text))
            )

        if len(summary_parts) == 1 and message:
            summary_parts.append(message)

        return ". ".join(summary_parts) + "."

    def _show_glow_result_dialog(self, command_id: str, message: str, payload: dict):
        try:
            import wx
            import gui
        except Exception:
            log.exception("BITS-EASY: GLOW result dialog dependencies unavailable")
            return

        main_frame = gui.mainFrame
        main_frame.prePopup()
        try:
            output_path = self._glow_output_path(payload)
            pretty_json = json.dumps(payload, ensure_ascii=False, indent=2)
            summary_lines = [
                _format_message(_("Command: {commandId}"), commandId=command_id),
                _format_message(_("Status: {status}"), status=message),
            ]
            if output_path:
                summary_lines.append(_format_message(_("Output file: {path}"), path=output_path))
            if "report" in payload and isinstance(payload.get("report"), str):
                summary_lines.append(_("Report text returned by GLOW."))

            dialog_text = "\n".join(summary_lines) + "\n\n" + _("JSON payload:") + "\n" + pretty_json

            dlg = wx.Dialog(
                main_frame,
                title=_("BITS-EASY GLOW Result"),
                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
            )
            try:
                root = wx.BoxSizer(wx.VERTICAL)
                text = wx.TextCtrl(
                    dlg,
                    value=dialog_text,
                    style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL,
                )
                text.SetMinSize((820, 420))
                root.Add(text, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

                button_row = wx.BoxSizer(wx.HORIZONTAL)
                copy_btn = wx.Button(dlg, label=_("Copy JSON"))
                open_btn = wx.Button(dlg, label=_("Open output file"))
                save_btn = wx.Button(dlg, label=_("Save report"))
                close_btn = wx.Button(dlg, id=wx.ID_OK, label=_("Close"))

                if not output_path:
                    open_btn.Enable(False)

                def on_copy(_evt):
                    data = wx.TextDataObject(pretty_json)
                    if wx.TheClipboard.Open():
                        try:
                            wx.TheClipboard.SetData(data)
                        finally:
                            wx.TheClipboard.Close()
                        self._announce_text(_("GLOW JSON copied"))
                    else:
                        self._announce_text(_("Clipboard unavailable"))

                def on_open(_evt):
                    target = output_path
                    if not target:
                        self._announce_text(_("No output file to open"))
                        return
                    try:
                        os.startfile(target)
                    except Exception:
                        log.exception("BITS-EASY: unable to open GLOW output path")
                        self._announce_text(_("Unable to open output file"))

                def on_save(_evt):
                    default_name = command_id.replace(".", "-")
                    report_text = payload.get("report")
                    is_text_report = isinstance(report_text, str)
                    wildcard = (
                        _("Text file (*.txt)|*.txt|JSON file (*.json)|*.json")
                        if is_text_report
                        else _("JSON file (*.json)|*.json")
                    )
                    save_dlg = wx.FileDialog(
                        dlg,
                        _("Save GLOW result"),
                        defaultFile=f"{default_name}.{'txt' if is_text_report else 'json'}",
                        wildcard=wildcard,
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                    )
                    try:
                        if save_dlg.ShowModal() != wx.ID_OK:
                            return
                        target = save_dlg.GetPath()
                    finally:
                        save_dlg.Destroy()

                    try:
                        if is_text_report and target.lower().endswith(".txt"):
                            Path(target).write_text(str(report_text), encoding="utf-8")
                        else:
                            Path(target).write_text(pretty_json, encoding="utf-8")
                        self._announce_text(_("GLOW result saved"))
                    except Exception:
                        log.exception("BITS-EASY: unable to save GLOW result")
                        self._announce_text(_("Unable to save GLOW result"))

                copy_btn.Bind(wx.EVT_BUTTON, on_copy)
                open_btn.Bind(wx.EVT_BUTTON, on_open)
                save_btn.Bind(wx.EVT_BUTTON, on_save)

                for btn in (copy_btn, open_btn, save_btn, close_btn):
                    button_row.Add(btn, flag=wx.RIGHT, border=8)

                root.Add(button_row, flag=wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)
                dlg.SetSizer(root)
                dlg.CentreOnScreen()
                dlg.ShowModal()
            finally:
                dlg.Destroy()
        except Exception:
            log.exception("BITS-EASY: GLOW result dialog failed")
        finally:
            main_frame.postPopup()

    def _prompt_glow_file_if_needed(self, command_id: str, kwargs: dict) -> bool:
        if command_id not in self._GLOW_FILE_COMMANDS:
            return False

        path_arg = str(kwargs.get("path", "")).strip()
        if path_arg:
            return False

        try:
            import wx

            wx.CallAfter(self._show_glow_file_dialog_and_dispatch, command_id, dict(kwargs))
            return True
        except Exception:
            log.exception("BITS-EASY: unable to open GLOW file picker")
            self._announce_text(_("GLOW command requires a file path."))
            return True

    def _show_glow_file_dialog_and_dispatch(self, command_id: str, kwargs: dict):
        try:
            import wx
            import gui
            import queueHandler
        except Exception:
            log.exception("BITS-EASY: GLOW file picker dependencies unavailable")
            try:
                self._announce_text(_("GLOW file picker is unavailable"))
            except Exception:
                pass
            return

        main_frame = gui.mainFrame
        main_frame.prePopup()
        try:
            wildcard = (
                "Supported files (*.docx;*.md;*.markdown;*.html;*.htm)|"
                "*.docx;*.md;*.markdown;*.html;*.htm|"
                "All files (*.*)|*.*"
            )
            selected_path = ""
            dlg = wx.FileDialog(
                main_frame,
                _("Select file for GLOW"),
                wildcard=wildcard,
                style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
            )
            try:
                if dlg.ShowModal() != wx.ID_OK:
                    self._announce_text(_("GLOW command canceled."))
                    return
                selected_path = dlg.GetPath()
            finally:
                dlg.Destroy()

            if not selected_path:
                self._announce_text(_("GLOW command canceled."))
                return

            dispatch_kwargs = dict(kwargs)
            dispatch_kwargs["path"] = selected_path
            queueHandler.queueFunction(queueHandler.eventQueue, self._dispatch, command_id, **dispatch_kwargs)
        except Exception:
            log.exception("BITS-EASY: GLOW file picker flow failed")
            try:
                self._announce_text(_("GLOW file picker failed"))
            except Exception:
                pass
        finally:
            main_frame.postPopup()

    def _run_integration_action(self, payload):
        if not isinstance(payload, dict):
            return ""

        integration = payload.get("integrationAction")
        if not isinstance(integration, dict):
            return ""

        provider = str(integration.get("provider", "")).strip().lower()
        action = str(integration.get("action", "")).strip().lower()
        use_ocr = bool(integration.get("ocr", False))
        if provider != "screenitemchooser" or action != "open":
            return ""

        try:
            module = importlib.import_module("globalPlugins.itemChooser")
        except Exception:
            log.exception("BITS-EASY: Screen Item Chooser module import failed")
            return _(
                "Screen Item Chooser is not installed. Install screenItemChooser-1.0.0.nvda-addon to enable this command."
            )

        plugin = getattr(module, "_pluginInstance", None)
        if plugin is None:
            return _("Screen Item Chooser is installed but not active. Restart NVDA and try again.")

        script_name = "script_openItemChooserOcr" if use_ocr else "script_openItemChooser"
        script_handler = getattr(plugin, script_name, None)
        if script_handler is None:
            return _("Screen Item Chooser integration is unavailable in the installed version.")

        try:
            script_handler(None)
        except TypeError:
            script_handler()
        except Exception:
            log.exception("BITS-EASY: Screen Item Chooser invocation failed")
            return _("Screen Item Chooser failed to open.")

        return ""

    @scriptHandler.script(description=_("BITS-EASY command palette"))
    def script_openCommandPalette(self, gesture):
        if self._dispatcher is None or self._context is None or self._config is None or self._palette is None:
            self._announce_text(_("BITS-EASY runtime unavailable"))
            return
        if self._settings and not self._settings.enable_command_palette:
            self._announce_text(_("BITS-EASY command palette is disabled in settings"))
            return

        try:
            import wx
        except Exception:
            log.exception("BITS-EASY: command palette wx import failed")
            self._announce_text(_("Command palette UI is unavailable"))
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
            log.exception("BITS-EASY: command palette wx/gui import failed")
            try:
                self._announce_text(_("Command palette UI is unavailable"))
            except Exception:
                pass
            return

        main_frame = gui.mainFrame
        main_frame.prePopup()
        try:
            query = ""
            query_dlg = wx.TextEntryDialog(main_frame, _("Search commands"), _("BITS-EASY Command Palette"), "")
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
                self._announce_text(_("No commands are registered"))
                return

            choices = [f"{item.name} [{item.command_id}] score={item.score:.2f}" for item in ranked]
            id_by_index = {idx: item.command_id for idx, item in enumerate(ranked)}

            command_id = ""
            dlg = wx.SingleChoiceDialog(main_frame, _("Choose BITS-EASY command"), _("BITS-EASY Command Palette"), choices)
            try:
                if dlg.ShowModal() != wx.ID_OK:
                    return
                command_id = id_by_index.get(dlg.GetSelection(), "")
            finally:
                dlg.Destroy()

            if not command_id:
                self._announce_text(_("No command selected"))
                return

            # Marshal the actual dispatch back to NVDA's event queue so
            # runtime side-effects (clipboard, ui.message) don't run inside
            # the wx event handler.
            try:
                import queueHandler
                queueHandler.queueFunction(queueHandler.eventQueue, self._dispatch, command_id)
            except Exception:
                log.exception("BITS-EASY: queueHandler unavailable; dispatching inline")
                self._dispatch(command_id)
        except Exception:
            log.exception("BITS-EASY: command palette UI failed")
            try:
                self._announce_text(_("Command palette failed"))
            except Exception:
                pass
        finally:
            main_frame.postPopup()

    @scriptHandler.script(description=_("BITS-EASY mark selection start"))
    def script_markSelectionStart(self, gesture):
        self._dispatch("cmd.selection.markStart")

    @scriptHandler.script(description=_("BITS-EASY mark selection end"))
    def script_markSelectionEnd(self, gesture):
        self._dispatch("cmd.selection.markEnd")

    @scriptHandler.script(description=_("BITS-EASY read selection context"))
    def script_readSelectionContext(self, gesture):
        self._dispatch("cmd.selection.readContext")

    def _try_apply_native_selection(self, start: int, end: int) -> bool:
        try:
            import api
        except Exception:
            return False

        focus = api.getFocusObject()
        if focus is None:
            return False

        lo = int(min(start, end))
        hi = int(max(start, end))
        if hi <= lo:
            return False

        providers = []
        tree = getattr(focus, "treeInterceptor", None)
        if tree is not None and not bool(getattr(tree, "passThrough", False)):
            providers.append(tree)
        providers.append(focus)

        for provider in providers:
            make_info = getattr(provider, "makeTextInfo", None)
            if not callable(make_info):
                continue
            try:
                info = make_info((lo, hi))
                updater = getattr(info, "updateSelection", None)
                if callable(updater):
                    updater()
                    return True
            except Exception:
                continue
        return False

    def _run_quick_select_action(self, action: str, gesture) -> None:
        if self._dispatcher is None or self._runtime is None or self._context is None:
            if gesture is not None:
                gesture.send()
            return

        self._refresh_context_from_focus()
        if not self._quick_select_armed or not self._runtime.has_selection_start_marker(self._context.app_id):
            if gesture is not None:
                gesture.send()
            return

        end_out = self._dispatcher.dispatch_command(self._context, "cmd.selection.markEnd")
        if not end_out.result.ok:
            self._announce_result_message(end_out.result.message, end_out.result.payload)
            return

        payload = end_out.result.payload if isinstance(end_out.result.payload, dict) else {}
        start = int(payload.get("start", self._context.caret))
        end = int(payload.get("end", self._context.caret))
        selection_text = self._runtime.selection_text_for_actions(self._context)
        self._quick_select_armed = False

        if not selection_text:
            self._announce_text(_("No text was captured for quick select."))
            return

        if action in ("copy", "cut"):
            existing = self._read_clipboard_text()
            settings = self._runtime.merge_settings()
            force_append = str(settings.get("mode", "replace")).lower() == "append"
            composed = self._runtime.compose_clipboard_text(existing, selection_text, force_append=force_append)
            if not self._write_clipboard_text(str(composed.get("content", ""))):
                self._announce_text(_("Clipboard unavailable"))
                return
            if self._context is not None:
                self._context.clipboard_text = str(composed.get("content", ""))

            if action == "cut":
                if self._try_apply_native_selection(start, end):
                    try:
                        import keyboardHandler

                        keyboardHandler.KeyboardInputGesture.fromName("delete").send()
                    except Exception:
                        log.exception("BITS-EASY: quick-select cut delete fallback failed")
                else:
                    self._announce_text(_("Selection copied, but text could not be removed in this surface."))
            else:
                self._announce_text(_("Selection appended to clipboard.") if force_append else _("Selection copied to clipboard."))
            return

        applied = self._try_apply_native_selection(start, end)
        if not applied:
            self._announce_text(_("Quick select could not apply a native selection in this surface."))
            return

        if gesture is not None:
            gesture.send()

    def _paste_text_preserving_clipboard(self, text: str) -> bool:
        payload = str(text or "")
        if not payload:
            return False

        old_clip = self._read_clipboard_text()
        if not self._write_clipboard_text(payload):
            return False

        try:
            import keyboardHandler

            keyboardHandler.KeyboardInputGesture.fromName("control+v").send()
        except Exception:
            log.exception("BITS-EASY: unable to paste expanded EASYText")
            self._write_clipboard_text(old_clip)
            return False

        try:
            import wx

            wx.CallLater(120, self._write_clipboard_text, old_clip)
        except Exception:
            self._write_clipboard_text(old_clip)
        return True

    def _try_expand_trigger_token(self, token: str) -> bool:
        if not self._trigger_expand_enabled:
            return False
        if self._dispatcher is None or self._context is None:
            return False

        value = str(token or "").strip()
        if not value:
            return False

        out = self._dispatcher.dispatch_command(
            self._context,
            "cmd.text.expansion.resolveTrigger",
            trigger=value,
        )
        if not out.result.ok:
            return False

        payload = out.result.payload if isinstance(out.result.payload, dict) else {}
        insert_text = str(payload.get("insertText") or payload.get("content") or "")
        if not insert_text:
            return False

        try:
            import keyboardHandler

            keyboardHandler.KeyboardInputGesture.fromName("control+backspace").send()
        except Exception:
            log.exception("BITS-EASY: unable to remove trigger token before expansion paste")
            return False

        suffix = str(payload.get("insertTextSuffix", " "))
        if not self._paste_text_preserving_clipboard(insert_text + suffix):
            return False

        self._announce_text(_format_message(_("Expanded {token}"), token=value))
        return True

    def event_typedCharacter(self, ch, nextHandler):
        # Preserve NVDA and app default behavior first.
        nextHandler()

        try:
            if self._dispatcher is None or self._context is None:
                return

            c = str(ch or "")
            if not c:
                return

            if c.isalnum() or c in ("_", "-", "."):
                if len(self._typed_word_buffer) < 80:
                    self._typed_word_buffer += c
                else:
                    self._typed_word_buffer = self._typed_word_buffer[-40:] + c
                return

            if c.isspace():
                token = self._typed_word_buffer.strip()
                self._typed_word_buffer = ""
                if not token:
                    return

                self._refresh_context_from_focus()
                self._try_expand_trigger_token(token)
                return

            # Any punctuation boundary resets token accumulation.
            self._typed_word_buffer = ""
        except Exception:
            log.exception("BITS-EASY: typed character trigger expansion failed")

    @scriptHandler.script(description=_("BITS-EASY quick select copy"))
    def script_quickSelectCopy(self, gesture):
        self._run_quick_select_action("copy", gesture)

    @scriptHandler.script(description=_("BITS-EASY quick select cut"))
    def script_quickSelectCut(self, gesture):
        self._run_quick_select_action("cut", gesture)

    @scriptHandler.script(description=_("BITS-EASY quick select paste"))
    def script_quickSelectPaste(self, gesture):
        self._run_quick_select_action("paste", gesture)

    @scriptHandler.script(description=_("BITS-EASY quick select delete"))
    def script_quickSelectDelete(self, gesture):
        self._run_quick_select_action("delete", gesture)

    @scriptHandler.script(description=_("BITS-EASY quick select format"))
    def script_quickSelectFormat(self, gesture):
        self._run_quick_select_action("format", gesture)

    @scriptHandler.script(description=_("BITS-EASY quick select cancel"))
    def script_quickSelectCancel(self, gesture):
        if self._runtime is None or self._context is None:
            if gesture is not None:
                gesture.send()
            return
        if self._quick_select_armed and self._runtime.has_selection_start_marker(self._context.app_id):
            self._quick_select_armed = False
            self._announce_text(_("Quick selection canceled."))
            return
        if gesture is not None:
            gesture.send()

    @scriptHandler.script(description=_("BITS-EASY append selection to clipboard"))
    def script_markEndAppendClipboard(self, gesture):
        self._dispatch("cmd.selection.markEndAppendClipboard")

    @scriptHandler.script(description=_("BITS-EASY speak clipboard"))
    def script_speakClipboard(self, gesture):
        self._dispatch("cmd.clipboard.speak")

    @scriptHandler.script(description=_("BITS-EASY clear clipboard"))
    def script_clearClipboard(self, gesture):
        self._dispatch("cmd.clipboard.clear")

    @scriptHandler.script(description=_("BITS-EASY copy to clip slot 1"))
    def script_copyToSlotOne(self, gesture):
        self._dispatch("cmd.clip.copyToSlot", slot=1)

    @scriptHandler.script(description=_("BITS-EASY paste from clip slot 1"))
    def script_pasteFromSlotOne(self, gesture):
        self._dispatch("cmd.clip.pasteFromSlot", slot=1)

    __gestures = {
        "kb:control+alt+[": "markSelectionStart",
        "kb:control+alt+]": "markSelectionEnd",
        "kb:control+alt+shift+]": "markEndAppendClipboard",
        "kb:control+alt+'": "readSelectionContext",
        "kb:control+alt+shift+'": "speakClipboard",
        "kb:control+alt+backspace": "clearClipboard",
        "kb:control+c": "quickSelectCopy",
        "kb:control+x": "quickSelectCut",
        "kb:control+v": "quickSelectPaste",
        "kb:delete": "quickSelectDelete",
        "kb:escape": "quickSelectCancel",
        "kb:control+b": "quickSelectFormat",
        "kb:control+i": "quickSelectFormat",
        "kb:control+u": "quickSelectFormat",
        "kb:control+l": "quickSelectFormat",
        "kb:control+r": "quickSelectFormat",
        "kb:control+j": "quickSelectFormat",
        "kb:control+e": "quickSelectFormat",
        "kb:control+alt+1": "copyToSlotOne",
        "kb:control+alt+2": "pasteFromSlotOne",
        "kb:control+alt+space": "openCommandPalette",
        "kb:NVDA+shift+p": "openCommandPalette",
    }

