from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Dict

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from spellforge_runtime import AppAdapter, AppContext, RuntimeDispatcher, SpellforgeRuntime, load_runtime_config


def _parse_inline_kv(parts: list[str]) -> Dict[str, str]:
    kwargs: Dict[str, str] = {}
    for part in parts:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        kwargs[key] = value
    return kwargs


def _emit(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=True))


def _build_runtime(storage_path: Path) -> SpellforgeRuntime:
    adapters = {
        "edge": AppAdapter("edge", supports_selection=True),
        "chrome": AppAdapter("chrome", supports_selection=True),
        "firefox": AppAdapter("firefox", supports_selection=True),
        "outlook": AppAdapter("outlook", supports_selection=False),
        "word": AppAdapter("word", supports_selection=True),
        "notepad": AppAdapter("notepad", supports_selection=True),
        "vscode": AppAdapter("vscode", supports_selection=True),
    }
    return SpellforgeRuntime(adapters=adapters, storage_path=storage_path)


def _run_single_press(dispatcher: RuntimeDispatcher, context: AppContext, key_chord: str, slot: int, text: str, content: str) -> None:
    outcome = dispatcher.dispatch_key_chord(
        context,
        key_chord,
        slot=slot,
        text=text,
        content=content,
    )
    _emit(
        {
            "ok": outcome.result.ok,
            "commandId": outcome.plan.command_id,
            "message": outcome.result.message,
            "payload": outcome.result.payload,
            "nextSteps": outcome.result.next_steps,
        }
    )


def _run_repl(dispatcher: RuntimeDispatcher, context: AppContext) -> int:
    print("Spellforge hotkey session REPL. Commands: press <KeyChord> [slot=1] [text=...] [content=...], set caret=<n>, set clipboard=..., set buffer=..., show, quit")
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            print("")
            break

        if not line:
            continue
        if line in ("quit", "exit"):
            break
        if line == "show":
            _emit(
                {
                    "context": {
                        "appId": context.app_id,
                        "windowId": context.window_id,
                        "controlId": context.control_id,
                        "caret": context.caret,
                        "bufferLength": len(context.buffer),
                        "clipboardLength": len(context.clipboard_text),
                    }
                }
            )
            continue

        if line.startswith("set "):
            kv = _parse_inline_kv(line.split()[1:])
            if "caret" in kv:
                context.caret = int(kv["caret"])
            if "clipboard" in kv:
                context.clipboard_text = kv["clipboard"]
            if "buffer" in kv:
                context.buffer = kv["buffer"]
            _emit({"ok": True, "message": "Context updated."})
            continue

        if line.startswith("press "):
            parts = line.split()
            if len(parts) < 2:
                _emit({"ok": False, "message": "Missing key chord."})
                continue

            key_chord = parts[1]
            kv = _parse_inline_kv(parts[2:])
            slot = int(kv.get("slot", "1"))
            text = kv.get("text", "")
            content = kv.get("content", "")
            _run_single_press(dispatcher, context, key_chord, slot=slot, text=text, content=content)
            continue

        _emit({"ok": False, "message": "Unknown command."})

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Simulate Spellforge hotkey sessions using repo keymap and profile configs.")
    parser.add_argument("--profile", default="balanced", choices=["beginner", "balanced", "expert"])
    parser.add_argument("--app", default="vscode")
    parser.add_argument("--window", default="win-default")
    parser.add_argument("--control", default="main-editor")
    parser.add_argument("--buffer", default="")
    parser.add_argument("--caret", type=int, default=0)
    parser.add_argument("--clipboard", default="")
    parser.add_argument("--storage", default=str(REPO_ROOT / ".spellforge" / "clip-slots.json"))
    parser.add_argument("--press", default=None, help="Single key chord press to execute once.")
    parser.add_argument("--slot", type=int, default=1)
    parser.add_argument("--text", default="")
    parser.add_argument("--content", default="")
    parser.add_argument("--repl", action="store_true")
    args = parser.parse_args()

    config = load_runtime_config(REPO_ROOT)
    runtime = _build_runtime(Path(args.storage))
    dispatcher = RuntimeDispatcher(runtime=runtime, config=config, profile_id=args.profile)

    context = AppContext(
        app_id=args.app,
        window_id=args.window,
        control_id=args.control,
        buffer=args.buffer,
        caret=args.caret,
        clipboard_text=args.clipboard,
    )

    if args.press:
        _run_single_press(
            dispatcher,
            context,
            key_chord=args.press,
            slot=args.slot,
            text=args.text,
            content=args.content,
        )
        return 0

    if args.repl:
        return _run_repl(dispatcher, context)

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
