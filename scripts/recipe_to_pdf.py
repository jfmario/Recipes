#!/usr/bin/env python3
"""
Convert a recipe Markdown file (optional YAML frontmatter) to a PDF.

Dependencies (see requirements-recipe-pdf.txt):
  pip install -r scripts/requirements-recipe-pdf.txt

On macOS, WeasyPrint may need: brew install pango cairo gdk-pixbuf libffi
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import markdown
import yaml
from weasyprint import HTML

DEFAULT_OUTPUT_DIR = Path("output")

FRONTMATTER_RE = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n",
    re.DOTALL | re.MULTILINE,
)

EXTENSIONS = [
    "markdown.extensions.extra",
    "markdown.extensions.nl2br",
    "markdown.extensions.sane_lists",
]

CSS = """
@page { size: letter; margin: 2cm; }
html { font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif; font-size: 11pt; line-height: 1.45; color: #222; }
body { max-width: 100%; }
h1 { font-size: 1.75rem; margin: 0 0 0.5em; font-weight: 600; }
h2 { font-size: 1.15rem; margin: 1.25em 0 0.4em; border-bottom: 1px solid #ccc; padding-bottom: 0.15em; }
p { margin: 0.5em 0; }
ul { margin: 0.35em 0 0.75em 1.2em; padding: 0; }
li { margin: 0.25em 0; }
.meta { font-size: 0.9rem; color: #555; margin-bottom: 1em; }
.meta-desc { font-size: 0.95rem; color: #444; margin: 0 0 1em; }
.meta-desc p { margin: 0.35em 0; }
.meta span { margin-right: 1em; }
strong { font-weight: 600; }
"""


def split_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    raw = m.group(1)
    body = text[m.end() :]
    try:
        data = yaml.safe_load(raw) or {}
    except yaml.YAMLError as e:
        raise SystemExit(f"Invalid YAML frontmatter: {e}") from e
    if not isinstance(data, dict):
        raise SystemExit("YAML frontmatter must be a mapping (key: value).")
    return data, body


def build_html(title: str, meta: dict, body_html: str) -> str:
    parts = []
    if meta.get("description"):
        desc_md = markdown.markdown(str(meta["description"]), extensions=EXTENSIONS)
        parts.append(f'<div class="meta-desc">{desc_md}</div>')
    spans = []
    if meta.get("time") is not None:
        spans.append(f"<span><strong>Time</strong>: {meta['time']} min</span>")
    tags = meta.get("tags")
    if tags:
        if isinstance(tags, list):
            tag_str = ", ".join(str(t) for t in tags)
        else:
            tag_str = str(tags)
        spans.append(f"<span><strong>Tags</strong>: {tag_str}</span>")
    meta_html = f'<div class="meta">{"".join(spans)}</div>' if spans else ""
    desc_html = parts[0] if parts else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{_escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<h1>{_escape(title)}</h1>
{desc_html}
{meta_html}
{body_html}
</body>
</html>"""


def _escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def title_from(meta: dict, body: str, path: Path) -> str:
    if meta.get("name"):
        return str(meta["name"])
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ").title()


def main() -> None:
    ap = argparse.ArgumentParser(description="Convert a recipe .md file to PDF.")
    ap.add_argument("recipe", type=Path, help="Path to the recipe Markdown file")
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output PDF path (default: output/<recipe-stem>.pdf under cwd)",
    )
    args = ap.parse_args()
    src = args.recipe.expanduser().resolve()
    if not src.is_file():
        print(f"Not a file: {src}", file=sys.stderr)
        sys.exit(1)
    text = src.read_text(encoding="utf-8")
    meta, body = split_frontmatter(text)
    title = title_from(meta, body, src)

    # Body: skip leading duplicate H1 if it matches title (common in recipes)
    body_stripped = body.lstrip()
    if body_stripped.startswith("# "):
        first_line = body_stripped.split("\n", 1)[0]
        h1_text = first_line[2:].strip()
        if h1_text.casefold() == title.casefold():
            body = body_stripped.split("\n", 1)[1] if "\n" in body_stripped else ""

    body_html = markdown.markdown(body, extensions=EXTENSIONS)
    html_doc = build_html(title, meta, body_html)

    out = args.output
    if out is None:
        out_dir = Path.cwd() / DEFAULT_OUTPUT_DIR
        out_dir.mkdir(parents=True, exist_ok=True)
        out = (out_dir / f"{src.stem}.pdf").resolve()
    else:
        out = out.expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)

    HTML(string=html_doc, base_url=str(src.parent)).write_pdf(out)
    print(out)


if __name__ == "__main__":
    main()
