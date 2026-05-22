from __future__ import annotations

from pathlib import Path
import re
from typing import Any, Dict, List

from .engine import RuntimeResult


class AuthoringEngine:
    def __init__(self) -> None:
        self._undo_stack: List[Dict[str, str]] = []

    def _push_undo(self, *, source: str, output: str, flow: str) -> str:
        token = f"author-undo-{len(self._undo_stack) + 1:04d}"
        self._undo_stack.append({"token": token, "source": source, "output": output, "flow": flow})
        return token

    def _normalize_markdown(self, text: str) -> str:
        rows = [line.rstrip() for line in text.replace("\r", "").split("\n")]
        return "\n".join(rows).strip("\n")

    def markdown_polish_pipeline(self, text: str) -> RuntimeResult:
        source = text or ""
        if not source.strip():
            return RuntimeResult(ok=False, message="Source text is required.")

        stages: List[Dict[str, Any]] = []
        transformed = self._normalize_markdown(source)
        stages.append(
            {
                "stage": "transform",
                "changed": transformed != source,
                "summary": "Normalized spacing and trailing whitespace.",
            }
        )

        structured = transformed
        if not structured.lstrip().startswith("# "):
            structured = f"# Draft\n\n{structured}".strip()
        stages.append(
            {
                "stage": "structure-check",
                "changed": structured != transformed,
                "summary": "Ensured top-level heading exists.",
            }
        )

        styled = structured.replace("[click here]", "[open the detailed guide]")
        stages.append(
            {
                "stage": "style-pass",
                "changed": styled != structured,
                "summary": "Upgraded ambiguous link text to descriptive wording.",
            }
        )

        undo_token = self._push_undo(source=source, output=styled, flow="markdown-polish")
        return RuntimeResult(
            ok=True,
            message="Markdown polish flow ready.",
            payload={
                "source": source,
                "output": styled,
                "insertText": styled,
                "stages": stages,
                "undoToken": undo_token,
                "confidence": 0.94,
                "nextAction": "Review polished output, then apply undo if you want to restore the original draft.",
            },
        )

    def markdown_template_apply(self, template: str, topic: str) -> RuntimeResult:
        t = template.strip().lower() or "release-notes"
        subject = topic.strip() or "this update"
        if t != "release-notes":
            return RuntimeResult(ok=False, message="Unsupported template. Use release-notes.")

        output = (
            f"# Release Notes: {subject}\n\n"
            "## Highlights\n"
            "- Added:\n"
            "- Improved:\n"
            "- Fixed:\n\n"
            "## Upgrade Notes\n"
            "- Prerequisites:\n"
            "- Breaking changes:\n\n"
            "## Verification\n"
            "- Smoke test:\n"
            "- Rollback check:\n"
        )
        undo_token = self._push_undo(source="", output=output, flow="markdown-template")
        return RuntimeResult(
            ok=True,
            message="Template output ready.",
            payload={
                "template": t,
                "topic": subject,
                "output": output,
                "insertText": output,
                "guided": True,
                "undoToken": undo_token,
                "nextAction": "Fill the placeholder bullets and run polish when draft details are complete.",
            },
        )

    def pipeline_undo(self, undo_token: str) -> RuntimeResult:
        token = undo_token.strip()
        if not token:
            return RuntimeResult(ok=False, message="Undo token is required.")
        row = next((item for item in reversed(self._undo_stack) if item.get("token") == token), None)
        if row is None:
            return RuntimeResult(ok=False, message="Undo token was not found.")
        return RuntimeResult(
            ok=True,
            message="Undo content ready.",
            payload={
                "undoToken": token,
                "restored": row.get("source", ""),
                "insertText": row.get("source", ""),
                "flow": row.get("flow", ""),
            },
        )

    def markdown_insert(self, kind: str, text: str) -> RuntimeResult:
        value = text or ""
        k = kind.strip().lower()
        if k == "heading1":
            out = f"# {value.strip() or 'Heading'}"
        elif k == "bold":
            out = f"**{value}**"
        elif k == "list":
            out = "\n".join(f"- {line.strip()}" for line in value.splitlines() if line.strip()) or "- item"
        elif k == "quote":
            out = "\n".join(f"> {line}" for line in value.splitlines()) or "> quote"
        elif k == "link":
            out = f"[{value or 'link text'}](https://example.com)"
        elif k == "table":
            out = "| Column A | Column B |\n| --- | --- |\n| value | value |"
        elif k == "footnote":
            out = f"{value}[^{1}]\n\n[^1]: Footnote text"
        else:
            return RuntimeResult(ok=False, message="Unsupported markdown workflow kind.")
        return RuntimeResult(ok=True, message="Markdown insertion ready.", payload={"markdown": out})

    def html_semantic(self, title: str, items: List[str]) -> RuntimeResult:
        heading = title.strip() or "Untitled"
        lis = "".join(f"<li>{x}</li>" for x in items)
        html = f"<article><header><h1>{heading}</h1></header><section><ul>{lis}</ul></section></article>"
        return RuntimeResult(ok=True, message="Semantic HTML generated.", payload={"html": html})

    def html_validate(self, html: str) -> RuntimeResult:
        text = html or ""
        issues = []
        if "<h3" in text and "<h2" not in text:
            issues.append("Heading level jumps from h1 to h3 without h2.")
        if re.search(r">\s*click here\s*<", text, re.IGNORECASE):
            issues.append("Link text 'click here' is ambiguous.")
        return RuntimeResult(ok=True, message="HTML validation complete.", payload={"issues": issues, "count": len(issues)})

    def export_html(self, markdown: str, out_path: Path | str) -> RuntimeResult:
        # Lightweight markdown conversion preserving headings and lists.
        lines = markdown.splitlines()
        html_lines = ["<article>"]
        for line in lines:
            if line.startswith("# "):
                html_lines.append(f"<h1>{line[2:].strip()}</h1>")
            elif line.startswith("- "):
                html_lines.append(f"<li>{line[2:].strip()}</li>")
            else:
                html_lines.append(f"<p>{line}</p>")
        html_lines.append("</article>")
        path = Path(out_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(html_lines), encoding="utf-8")
        return RuntimeResult(ok=True, message="HTML export complete.", payload={"path": str(path)})

    def export_word_stub(self, markdown: str, out_path: Path | str) -> RuntimeResult:
        # Project currently emits a structured txt stub with .docx extension for adapter parity tests.
        path = Path(out_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown, encoding="utf-8")
        return RuntimeResult(ok=True, message="Word export bridge complete.", payload={"path": str(path), "format": "docx-stub"})

    def accessibility_lint(self, markdown: str) -> RuntimeResult:
        issues: List[Dict[str, str]] = []
        for i, line in enumerate(markdown.splitlines(), start=1):
            if "click here" in line.lower():
                issues.append({"line": str(i), "issue": "Ambiguous link text.", "remediation": "Use descriptive link text."})
            if line.startswith("### ") and "## " not in markdown:
                issues.append({"line": str(i), "issue": "Heading order skip.", "remediation": "Insert intermediate heading level."})
        return RuntimeResult(ok=True, message="Accessibility lint complete.", payload={"issues": issues, "count": len(issues)})

    def accessibility_fix_preview(self, markdown: str) -> RuntimeResult:
        preview = markdown.replace("click here", "open the detailed guide")
        return RuntimeResult(ok=True, message="Accessibility fix preview ready.", payload={"preview": preview})

    def html_fix_preview(self, html: str) -> RuntimeResult:
        source = html or ""
        preview = source
        changes: List[Dict[str, str]] = []
        if "click here" in preview.lower():
            preview = re.sub(r"click here", "open the detailed guide", preview, flags=re.IGNORECASE)
            changes.append(
                {
                    "rule": "link-purpose",
                    "before": "click here",
                    "after": "open the detailed guide",
                }
            )
        if "<main" not in preview.lower() and "<article" in preview.lower():
            preview = preview.replace("<article", "<main><article", 1)
            preview = preview.replace("</article>", "</article></main>", 1)
            changes.append(
                {
                    "rule": "landmark-main",
                    "before": "article without main",
                    "after": "wrapped article in main landmark",
                }
            )
        return RuntimeResult(
            ok=True,
            message="HTML fix preview ready.",
            payload={
                "original": source,
                "preview": preview,
                "changes": changes,
                "count": len(changes),
                "nonDestructive": True,
                "nextAction": "Apply the preview when changes look correct, or keep original HTML unchanged.",
            },
        )

    def html_fix_apply(self, html: str) -> RuntimeResult:
        pre = self.html_fix_preview(html)
        if not pre.ok:
            return pre
        payload = pre.payload or {}
        output = str(payload.get("preview", ""))
        undo_token = self._push_undo(source=html or "", output=output, flow="html-fix")
        payload["undoToken"] = undo_token
        payload["insertText"] = output
        return RuntimeResult(ok=True, message="HTML fixes prepared for apply.", payload=payload)
