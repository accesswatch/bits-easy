from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
from threading import Event, Thread
from typing import Any, Callable, Dict, Optional


@dataclass
class HotkeySpec:
    original: str
    modifiers: int
    vk: int
    supported: bool


MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
WM_HOTKEY = 0x0312


def _vk_for_key(key: str) -> Optional[int]:
    key = key.upper()
    if len(key) == 1 and "A" <= key <= "Z":
        return ord(key)
    if len(key) == 1 and "0" <= key <= "9":
        return ord(key)
    if key.startswith("F") and key[1:].isdigit():
        num = int(key[1:])
        if 1 <= num <= 24:
            return 0x6F + num
    table = {
        "GRAVE": 0xC0,
        "GRAVEACCENT": 0xC0,
        "SPELLFORGE": 0xC0,
        "SPACE": 0x20,
        "BACKSPACE": 0x08,
        "ESCAPE": 0x1B,
        "LEFTARROW": 0x25,
        "RIGHTARROW": 0x27,
        "SLASH": 0xBF,
        "QUOTE": 0xDE,
        "OPENBRACKET": 0xDB,
        "CLOSEBRACKET": 0xDD,
    }
    return table.get(key)


def parse_key_chord_for_os(chord: str, emulate_capslock_prefix: bool = True) -> HotkeySpec:
    parts = [p.strip() for p in chord.split("+") if p.strip()]
    if not parts:
        return HotkeySpec(original=chord, modifiers=0, vk=0, supported=False)

    modifiers = 0
    key_part = None
    total_parts = len(parts)
    for p in parts:
        pl = p.lower()
        if pl in ("control", "ctrl"):
            modifiers |= MOD_CONTROL
        elif pl == "alt":
            modifiers |= MOD_ALT
        elif pl == "shift":
            modifiers |= MOD_SHIFT
        elif pl in ("win", "windows"):
            modifiers |= MOD_WIN
        elif pl == "capslock":
            if emulate_capslock_prefix:
                modifiers |= MOD_CONTROL | MOD_ALT
            else:
                return HotkeySpec(original=chord, modifiers=0, vk=0, supported=False)
        elif pl in ("grave", "graveaccent", "spellforge"):
            if total_parts == 1:
                key_part = "GRAVE"
            elif emulate_capslock_prefix:
                modifiers |= MOD_CONTROL | MOD_ALT
            else:
                return HotkeySpec(original=chord, modifiers=0, vk=0, supported=False)
        else:
            key_part = p

    if key_part is None:
        return HotkeySpec(original=chord, modifiers=0, vk=0, supported=False)

    vk = _vk_for_key(key_part)
    if vk is None:
        return HotkeySpec(original=chord, modifiers=0, vk=0, supported=False)

    return HotkeySpec(original=chord, modifiers=modifiers, vk=vk, supported=True)


class GlobalHotkeyService:
    def __init__(self, on_command: Callable[[str, Optional[Dict[str, Any]]], None], emulate_capslock_prefix: bool = True):
        self._on_command = on_command
        self._emulate_capslock_prefix = emulate_capslock_prefix
        self._bindings: Dict[int, Dict[str, Any]] = {}
        self._running = Event()
        self._thread: Optional[Thread] = None

    def start(self, bindings: list[dict]) -> None:
        if self._thread and self._thread.is_alive():
            return

        self._bindings.clear()
        self._running.set()
        self._thread = Thread(target=self._loop, args=(bindings,), daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running.clear()

    def _loop(self, bindings: list[dict]) -> None:
        user32 = ctypes.windll.user32
        msg = wintypes.MSG()

        hotkey_id = 1
        for binding in bindings:
            if not binding.get("enabled", True):
                continue
            trigger = binding.get("trigger") or {"kind": "single-press"}
            if trigger.get("kind", "single-press") != "single-press":
                continue
            spec = parse_key_chord_for_os(
                str(binding.get("keyChord", "")),
                emulate_capslock_prefix=self._emulate_capslock_prefix,
            )
            if not spec.supported:
                continue

            ok = user32.RegisterHotKey(None, hotkey_id, spec.modifiers, spec.vk)
            if ok:
                raw_args = binding.get("args", {})
                self._bindings[hotkey_id] = {
                    "commandId": str(binding.get("commandId", "")),
                    "args": dict(raw_args) if isinstance(raw_args, dict) else {},
                }
                hotkey_id += 1

        try:
            while self._running.is_set():
                has_msg = user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1)
                if not has_msg:
                    ctypes.windll.kernel32.Sleep(25)
                    continue

                if msg.message == WM_HOTKEY:
                    spec = self._bindings.get(int(msg.wParam), {})
                    command_id = str(spec.get("commandId", ""))
                    if command_id:
                        args = spec.get("args", {})
                        self._on_command(command_id, dict(args) if isinstance(args, dict) else {})

                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            for hotkey_id in list(self._bindings.keys()):
                user32.UnregisterHotKey(None, hotkey_id)
            self._bindings.clear()
