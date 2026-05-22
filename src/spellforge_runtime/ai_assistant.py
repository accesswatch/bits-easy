from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from .engine import RuntimeResult


class AiAssistantService:
    def __init__(self, storage_path: Path | str | None = None):
        self._storage_path = Path(storage_path) if storage_path else None
        self._keys: Dict[str, str] = {}
        self._sessions: Dict[str, List[Dict[str, str]]] = {}
        self._prompts: Dict[str, str] = {}
        self._documents: Dict[str, Dict[str, str]] = {}
        self._active_session = ""
        self._session_counter = 0
        self._doc_counter = 0
        self._load()

    def _save(self) -> None:
        if not self._storage_path:
            return
        self._storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "keys": self._keys,
            "sessions": self._sessions,
            "prompts": self._prompts,
            "documents": self._documents,
            "activeSession": self._active_session,
            "sessionCounter": self._session_counter,
            "docCounter": self._doc_counter,
        }
        self._storage_path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    def _load(self) -> None:
        if not self._storage_path or not self._storage_path.exists():
            return
        try:
            payload = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except Exception:
            return
        self._keys = payload.get("keys", {}) if isinstance(payload.get("keys", {}), dict) else {}
        self._sessions = payload.get("sessions", {}) if isinstance(payload.get("sessions", {}), dict) else {}
        self._prompts = payload.get("prompts", {}) if isinstance(payload.get("prompts", {}), dict) else {}
        self._documents = payload.get("documents", {}) if isinstance(payload.get("documents", {}), dict) else {}
        self._active_session = str(payload.get("activeSession", ""))
        self._session_counter = int(payload.get("sessionCounter", 0))
        self._doc_counter = int(payload.get("docCounter", 0))

    @staticmethod
    def _provider_key(name: str) -> str:
        return name.strip().lower()

    def key_set(self, provider: str, key: str) -> RuntimeResult:
        p = self._provider_key(provider)
        v = key.strip()
        if not p:
            return RuntimeResult(ok=False, message="Provider is required.")
        if not v:
            return RuntimeResult(ok=False, message="API key is required.")
        self._keys[p] = v
        self._save()
        return RuntimeResult(ok=True, message="AI provider key saved.", payload={"provider": p})

    def key_delete(self, provider: str) -> RuntimeResult:
        p = self._provider_key(provider)
        if not p:
            return RuntimeResult(ok=False, message="Provider is required.")
        if p in self._keys:
            del self._keys[p]
            self._save()
        return RuntimeResult(ok=True, message="AI provider key deleted.", payload={"provider": p})

    def billing_status(self, provider: str) -> RuntimeResult:
        p = self._provider_key(provider)
        if not p:
            return RuntimeResult(ok=False, message="Provider is required.")
        url = f"https://{p}.com/billing"
        return RuntimeResult(ok=True, message="Billing status endpoint ready.", payload={"provider": p, "url": url})

    def session_new(self, title: str = "") -> RuntimeResult:
        self._session_counter += 1
        sid = f"ai-session-{self._session_counter:04d}"
        self._sessions[sid] = []
        self._active_session = sid
        if title.strip():
            self._sessions[sid].append({"role": "system", "text": title.strip()})
        self._save()
        return RuntimeResult(ok=True, message="AI session created.", payload={"sessionId": sid})

    def session_clear(self) -> RuntimeResult:
        sid = self._active_session.strip()
        if not sid or sid not in self._sessions:
            return RuntimeResult(ok=False, message="No active AI session.")
        self._sessions[sid] = []
        self._save()
        return RuntimeResult(ok=True, message="AI session cleared.", payload={"sessionId": sid})

    def session_save(self, session_id: str = "") -> RuntimeResult:
        sid = (session_id.strip() or self._active_session).strip()
        if not sid or sid not in self._sessions:
            return RuntimeResult(ok=False, message="Session was not found.")
        self._save()
        return RuntimeResult(ok=True, message="AI session saved.", payload={"sessionId": sid, "turnCount": len(self._sessions[sid])})

    def session_load(self, session_id: str) -> RuntimeResult:
        sid = session_id.strip()
        if not sid or sid not in self._sessions:
            return RuntimeResult(ok=False, message="Session was not found.")
        self._active_session = sid
        self._save()
        return RuntimeResult(ok=True, message="AI session loaded.", payload={"sessionId": sid, "turnCount": len(self._sessions[sid])})

    def session_list(self) -> RuntimeResult:
        items = []
        for sid in sorted(self._sessions.keys()):
            items.append({"sessionId": sid, "turnCount": len(self._sessions[sid]), "active": sid == self._active_session})
        return RuntimeResult(ok=True, message="AI sessions listed.", payload={"items": items, "count": len(items)})

    def session_delete(self, session_id: str) -> RuntimeResult:
        sid = session_id.strip()
        if not sid or sid not in self._sessions:
            return RuntimeResult(ok=False, message="Session was not found.")
        del self._sessions[sid]
        if self._active_session == sid:
            self._active_session = ""
        self._save()
        return RuntimeResult(ok=True, message="AI session deleted.", payload={"sessionId": sid})

    def tool_run(self, tool: str, text: str, *, replace: bool = False) -> RuntimeResult:
        t = tool.strip().lower()
        src = text.strip()
        if not t:
            return RuntimeResult(ok=False, message="Tool is required.")
        if not src:
            return RuntimeResult(ok=False, message="Input text is required.")

        if t == "summarize":
            out = src.split(".")[0].strip() or src[:120]
        elif t == "rewrite":
            out = f"Plain rewrite: {src}"
        elif t == "extract-actions":
            parts = [p.strip() for p in src.replace("\r", "\n").split("\n") if p.strip()]
            out = "\n".join(f"- {p}" for p in parts[:10])
        elif t == "dictionary":
            out = f"Definition lookup prepared for: {src}"
        elif t == "thesaurus":
            out = f"Synonym lookup prepared for: {src}"
        elif t == "a11y-rewrite":
            out = f"Accessibility-friendly rewrite: {src}"
        elif t == "spellcheck":
            out = src.replace(" teh ", " the ")
        else:
            return RuntimeResult(ok=False, message="Unsupported AI tool.")

        sid = self._active_session.strip()
        if sid and sid in self._sessions:
            self._sessions[sid].append({"role": "user", "text": src})
            self._sessions[sid].append({"role": "assistant", "text": out})
            self._save()
        return RuntimeResult(
            ok=True,
            message="AI tool output ready.",
            payload={"tool": t, "text": out, "insertText": out if replace else "", "replaceSuggested": bool(replace)},
        )

    def prompt_create(self, name: str, text: str) -> RuntimeResult:
        n = name.strip().lower()
        v = text.strip()
        if not n:
            return RuntimeResult(ok=False, message="Prompt name is required.")
        if not v:
            return RuntimeResult(ok=False, message="Prompt text is required.")
        self._prompts[n] = v
        self._save()
        return RuntimeResult(ok=True, message="Prompt saved.", payload={"name": n})

    def prompt_delete(self, name: str) -> RuntimeResult:
        n = name.strip().lower()
        if n in self._prompts:
            del self._prompts[n]
            self._save()
        return RuntimeResult(ok=True, message="Prompt deleted.", payload={"name": n})

    def prompt_list(self, query: str = "") -> RuntimeResult:
        q = query.strip().lower()
        items = []
        for name in sorted(self._prompts.keys()):
            if q and q not in name and q not in self._prompts[name].lower():
                continue
            items.append({"name": name, "text": self._prompts[name]})
        return RuntimeResult(ok=True, message="Prompt list ready.", payload={"items": items, "count": len(items)})

    def prompt_insert(self, name: str) -> RuntimeResult:
        n = name.strip().lower()
        val = self._prompts.get(n)
        if val is None:
            return RuntimeResult(ok=False, message="Prompt not found.")
        return RuntimeResult(ok=True, message="Prompt insert text ready.", payload={"name": n, "insertText": val, "text": val})

    def document_upload(self, path: Path | str, *, title: str = "") -> RuntimeResult:
        src = Path(path)
        if not src.exists():
            return RuntimeResult(ok=False, message="Document file was not found.")
        text = src.read_text(encoding="utf-8", errors="ignore")
        self._doc_counter += 1
        doc_id = f"doc-{self._doc_counter:04d}"
        self._documents[doc_id] = {"title": title.strip() or src.name, "content": text}
        self._save()
        return RuntimeResult(ok=True, message="Document uploaded for Q and A.", payload={"documentId": doc_id, "title": self._documents[doc_id]["title"]})

    def document_ask(self, document_id: str, question: str) -> RuntimeResult:
        did = document_id.strip()
        q = question.strip()
        doc = self._documents.get(did)
        if doc is None:
            return RuntimeResult(ok=False, message="Document was not found.")
        if not q:
            return RuntimeResult(ok=False, message="Question is required.")
        content = str(doc.get("content", ""))
        snippet = content[:400].strip()
        answer = f"Answer based on {doc.get('title', 'document')}: {snippet}" if snippet else "No content available."

        sid = self._active_session.strip()
        if sid and sid in self._sessions:
            self._sessions[sid].append({"role": "user", "text": q})
            self._sessions[sid].append({"role": "assistant", "text": answer})
            self._save()

        return RuntimeResult(ok=True, message="Document answer ready.", payload={"documentId": did, "question": q, "answer": answer, "insertText": answer})

    def image_generate(self, prompt: str, out_path: Path | str) -> RuntimeResult:
        p = prompt.strip()
        if not p:
            return RuntimeResult(ok=False, message="Image prompt is required.")
        out = Path(out_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(f"Generated image placeholder for prompt:\n{p}\n", encoding="utf-8")
        return RuntimeResult(ok=True, message="Generated image saved.", payload={"path": str(out), "prompt": p})

    def transcribe(self, in_path: Path | str, *, speaker_separation: bool = False, translate_to: str = "") -> RuntimeResult:
        src = Path(in_path)
        if not src.exists():
            return RuntimeResult(ok=False, message="Audio source file was not found.")
        raw = src.read_text(encoding="utf-8", errors="ignore")
        text = raw.strip() or f"Transcription generated for {src.name}."
        if speaker_separation:
            text = f"[Speaker 1] {text}"
        if translate_to.strip():
            text = f"{text}\n[Translated:{translate_to.strip().lower()}]"
        return RuntimeResult(ok=True, message="Transcription ready.", payload={"text": text, "insertText": text, "source": str(src)})
