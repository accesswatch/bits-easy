from __future__ import annotations

import ctypes
from ctypes import wintypes
from dataclasses import dataclass
import time
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
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SYSKEYDOWN = 0x0104
WM_SYSKEYUP = 0x0105
WH_KEYBOARD_LL = 13
HC_ACTION = 0

VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12
VK_LWIN = 0x5B
VK_RWIN = 0x5C


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_void_p),
    ]


LowLevelKeyboardProc = ctypes.WINFUNCTYPE(ctypes.c_long, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)


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
        "BITSEASY": 0xC0,
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


def raw_vk_to_key_token(vk: int, shift_pressed: bool = False) -> Optional[str]:
    if 0x41 <= int(vk) <= 0x5A:
        return chr(int(vk))
    if 0x30 <= int(vk) <= 0x39:
        return chr(int(vk))

    table = {
        0xBF: "Slash",  # / ?
        0xDB: "OpenBracket",  # [ {
        0xDD: "CloseBracket",  # ] }
        0xDE: "Quote",  # ' "
        0xBA: "Semicolon",  # ; :
        0x08: "Backspace",
        0x1B: "Escape",
        0x20: "Space",
        0x25: "LeftArrow",
        0x27: "RightArrow",
    }
    return table.get(int(vk))


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
        elif pl in ("grave", "graveaccent", "bits_easy"):
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
    def __init__(
        self,
        on_command: Callable[[str, Optional[Dict[str, Any]]], None],
        emulate_capslock_prefix: bool = True,
        on_key_chord: Optional[Callable[[str, Optional[Dict[str, Any]]], None]] = None,
        enable_raw_sequences: bool = True,
        raw_sequence_timeout_ms: int = 900,
    ):
        self._on_command = on_command
        self._on_key_chord = on_key_chord
        self._emulate_capslock_prefix = emulate_capslock_prefix
        self._enable_raw_sequences = bool(enable_raw_sequences)
        self._raw_sequence_timeout_seconds = max(0.25, float(raw_sequence_timeout_ms) / 1000.0)
        self._bindings: Dict[int, Dict[str, Any]] = {}
        self._running = Event()
        self._thread: Optional[Thread] = None
        self._leader_active = False
        self._leader_mode = ""
        self._leader_expires_at = 0.0
        self._leader_pending_fallback: Optional[Dict[str, Any]] = None
        self._suppressed_vk: Optional[int] = None
        self._kb_hook = None
        self._kb_proc = None

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

        def _reset_leader_state() -> None:
            self._leader_active = False
            self._leader_mode = ""
            self._leader_expires_at = 0.0
            self._leader_pending_fallback = None

        def _dispatch_chord(chord: str, args: Optional[Dict[str, Any]] = None) -> None:
            payload = dict(args) if isinstance(args, dict) else {}
            if self._on_key_chord is not None:
                self._on_key_chord(chord, payload)
                return
            # Fallback behavior: direct command callback is still available when no chord callback is set.
            binding = next((b for b in bindings if str(b.get("keyChord", "")) == chord and b.get("enabled", True)), None)
            if binding is None:
                return
            self._on_command(str(binding.get("commandId", "")), payload)

        def _dispatch_pending_fallback() -> None:
            if not self._leader_pending_fallback:
                return
            fallback = dict(self._leader_pending_fallback)
            _reset_leader_state()
            command_id = str(fallback.get("commandId", ""))
            if command_id:
                args = fallback.get("args", {})
                self._on_command(command_id, dict(args) if isinstance(args, dict) else {})

        def _modifiers_down() -> bool:
            return any(
                bool(user32.GetAsyncKeyState(vk) & 0x8000)
                for vk in (VK_SHIFT, VK_CONTROL, VK_MENU, VK_LWIN, VK_RWIN)
            )

        def _keyboard_proc(nCode: int, wParam: int, lParam: int):
            if nCode != HC_ACTION or not self._leader_active:
                return user32.CallNextHookEx(None, nCode, wParam, lParam)

            kb = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
            vk = int(kb.vkCode)

            if wParam in (WM_KEYUP, WM_SYSKEYUP):
                if self._suppressed_vk is not None and vk == self._suppressed_vk:
                    self._suppressed_vk = None
                    return 1
                return user32.CallNextHookEx(None, nCode, wParam, lParam)

            if wParam not in (WM_KEYDOWN, WM_SYSKEYDOWN):
                return user32.CallNextHookEx(None, nCode, wParam, lParam)

            if _modifiers_down():
                _reset_leader_state()
                return user32.CallNextHookEx(None, nCode, wParam, lParam)

            shift_pressed = bool(user32.GetAsyncKeyState(VK_SHIFT) & 0x8000)
            token = raw_vk_to_key_token(vk, shift_pressed=shift_pressed)
            if token is None:
                _reset_leader_state()
                return user32.CallNextHookEx(None, nCode, wParam, lParam)

            self._suppressed_vk = vk
            chord = f"Grave+{token}"

            if self._leader_mode == "glow":
                _dispatch_chord(chord)
                _reset_leader_state()
                return 1

            if token.upper() == "G":
                _dispatch_chord(chord)
                self._leader_mode = "glow"
                self._leader_expires_at = time.monotonic() + self._raw_sequence_timeout_seconds
                self._leader_pending_fallback = None
                return 1

            _dispatch_chord(chord)
            _reset_leader_state()
            return 1

        self._kb_proc = LowLevelKeyboardProc(_keyboard_proc)
        self._kb_hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, self._kb_proc, ctypes.windll.kernel32.GetModuleHandleW(None), 0)

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
                    "keyChord": str(binding.get("keyChord", "")),
                }
                hotkey_id += 1

        try:
            while self._running.is_set():
                if self._leader_active and time.monotonic() > self._leader_expires_at:
                    _dispatch_pending_fallback()

                has_msg = user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1)
                if not has_msg:
                    ctypes.windll.kernel32.Sleep(25)
                    continue

                if msg.message == WM_HOTKEY:
                    spec = self._bindings.get(int(msg.wParam), {})
                    command_id = str(spec.get("commandId", ""))
                    if command_id:
                        args = spec.get("args", {})
                        key_chord = str(spec.get("keyChord", "")).strip()
                        if self._enable_raw_sequences and key_chord == "Grave":
                            self._leader_active = True
                            self._leader_mode = ""
                            self._leader_expires_at = time.monotonic() + self._raw_sequence_timeout_seconds
                            self._leader_pending_fallback = {
                                "commandId": command_id,
                                "args": dict(args) if isinstance(args, dict) else {},
                            }
                        else:
                            self._on_command(command_id, dict(args) if isinstance(args, dict) else {})

                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            if self._kb_hook is not None:
                user32.UnhookWindowsHookEx(self._kb_hook)
                self._kb_hook = None
            for hotkey_id in list(self._bindings.keys()):
                user32.UnregisterHotKey(None, hotkey_id)
            self._bindings.clear()
            self._leader_active = False
            self._leader_mode = ""
            self._leader_pending_fallback = None

