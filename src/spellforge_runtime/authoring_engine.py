from __future__ import annotations

from pathlib import Path
import re
from typing import Dict, List

from .engine import RuntimeResult


class AuthoringEngine:
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
