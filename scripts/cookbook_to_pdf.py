#!/usr/bin/env python3
"""
Build one cookbook PDF from every recipe under recipes/.

Includes a numbered table of contents (grouped by the same parts as the recipes)
with page numbers (single WeasyPrint pass), part headings by top-level folder,
and each recipe in its own section with page breaks as needed.
"""

from __future__ import annotations

import argparse
import platform
import subprocess
import sys
from pathlib import Path

import markdown
from weasyprint import HTML

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import recipe_to_pdf as rtp

COOKBOOK_EXTRA_CSS = """
.toc-block { break-after: page; }
.toc-block > h1 { font-size: 2rem; margin-top: 0; }
.toc-block > h2 {
  font-size: 1.35rem;
  margin: 1.25em 0 0.5em;
  border-bottom: none;
  padding-bottom: 0;
}
.toc-block h3.toc-section-title {
  font-size: 1.12rem;
  margin: 1.1em 0 0.35em;
  padding-bottom: 0.15em;
  border-bottom: 1px solid #bbb;
  font-weight: 600;
  color: #333;
}
.toc-block h2 + h3.toc-section-title { margin-top: 0.65em; }
.toc-block ol { margin: 0.35em 0 0.75em 1.75em; padding: 0; }
.toc-block li { margin: 0.4em 0; }
.toc-block a {
  color: #222;
  text-decoration: none;
  display: flex;
  align-items: baseline;
  gap: 0.35em;
}
.toc-block a .toc-name { flex: 0 1 auto; }
.toc-block a::after {
  content: leader(dotted) target-counter(attr(href url), page);
  flex: 1 1 auto;
  text-align: right;
}
.part + .part { break-before: always; }
.part-heading {
  font-size: 1.5rem;
  margin: 0 0 0.75em;
  padding-bottom: 0.2em;
  border-bottom: 2px solid #333;
  font-weight: 600;
}
.part .recipe ~ .recipe { break-before: always; }
section.recipe { padding-top: 0; }
section.recipe > h1 { margin-top: 0; }
"""


def _recipe_anchor(relative: Path) -> str:
    return "-".join(relative.with_suffix("").parts)


def _part_label(folder: str) -> str:
    return {
        "main": "Main dishes",
        "side": "Sides",
        "lenten": "Lenten",
        "ingredients": "Ingredients & bases",
    }.get(folder, folder.replace("-", " ").title())


def _group_by_top_folder(paths: list[Path], recipes_dir: Path) -> list[tuple[str, list[Path]]]:
    groups: list[tuple[str, list[Path]]] = []
    for p in paths:
        rel = p.relative_to(recipes_dir)
        top = rel.parts[0] if rel.parts else ""
        if not groups or groups[-1][0] != top:
            groups.append((top, []))
        groups[-1][1].append(p)
    return groups


def _build_cookbook_html(recipes_dir: Path) -> str:
    recipe_files = sorted(recipes_dir.rglob("*.md"), key=lambda p: p.as_posix())
    if not recipe_files:
        raise SystemExit("No recipe markdown files were found under recipes/.")

    toc_items: list[tuple[str, str]] = []
    recipe_sections: list[str] = []

    for path in recipe_files:
        rel = path.relative_to(recipes_dir)
        anchor = _recipe_anchor(rel)
        text = path.read_text(encoding="utf-8")
        meta, body = rtp.split_frontmatter(text)
        title = rtp.title_from(meta, body, path)
        body = rtp.strip_leading_duplicate_h1(body, title)
        body_html = markdown.markdown(body, extensions=rtp.EXTENSIONS)
        inner = rtp.recipe_fragment_html(title, meta, body_html)
        toc_items.append((anchor, title))
        recipe_sections.append(f'<section class="recipe" id="{anchor}">{inner}</section>')

    grouped = _group_by_top_folder(recipe_files, recipes_dir)

    toc_lines = [
        '<div class="toc-block">',
        "<h1>Cookbook</h1>",
        "<h2>Table of Contents</h2>",
    ]
    pos = 0
    for folder, paths in grouped:
        toc_lines.append(
            f'<h3 class="toc-section-title">{rtp._escape(_part_label(folder))}</h3>'
        )
        toc_lines.append(f'<ol start="{pos + 1}">')
        for _ in paths:
            anchor, title = toc_items[pos]
            toc_lines.append(
                f'<li><a href="#{anchor}"><span class="toc-name">{rtp._escape(title)}</span></a></li>'
            )
            pos += 1
        toc_lines.append("</ol>")
    toc_lines.append("</div>")
    idx = 0
    part_chunks: list[str] = []
    for folder, paths in grouped:
        chunks = [f'<section class="part"><h1 class="part-heading">{rtp._escape(_part_label(folder))}</h1>']
        for _ in paths:
            chunks.append(recipe_sections[idx])
            idx += 1
        chunks.append("</section>")
        part_chunks.append("".join(chunks))

    combined_css = f"{rtp.CSS}\n{COOKBOOK_EXTRA_CSS}"
    body = "".join(toc_lines) + "".join(part_chunks)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Cookbook</title>
<style>{combined_css}</style>
</head>
<body>
{body}
</body>
</html>"""


def main() -> None:
    ap = argparse.ArgumentParser(description="Build cookbook.pdf from recipes/.")
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("output") / "cookbook.pdf",
        help="Output PDF path (default: output/cookbook.pdf)",
    )
    ap.add_argument(
        "--recipes-dir",
        type=Path,
        default=Path("recipes"),
        help="Root directory of recipe markdown files",
    )
    ap.add_argument(
        "--open",
        action="store_true",
        help="After a successful build, open the PDF (macOS only: uses the open command)",
    )
    args = ap.parse_args()
    root = Path.cwd()
    recipes_dir = (root / args.recipes_dir).resolve()
    if not recipes_dir.is_dir():
        print(f"Not a directory: {recipes_dir}", file=sys.stderr)
        sys.exit(1)
    out = (root / args.output).resolve() if not args.output.is_absolute() else args.output.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    html_doc = _build_cookbook_html(recipes_dir)
    HTML(string=html_doc, base_url=str(recipes_dir)).write_pdf(out)
    print(out)
    if args.open and platform.system() == "Darwin":
        subprocess.run(["open", str(out)], check=False)


if __name__ == "__main__":
    main()
