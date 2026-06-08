# AGENTS.md

Guidance for AI agents working in this repository.

## Project overview

This is a **personal/family cookbook** stored as Markdown with YAML frontmatter under `recipes/`. Python scripts compile recipes into PDFs:

- `scripts/cookbook_to_pdf.py` — combined cookbook with table of contents
- `scripts/recipe_to_pdf.py` — single-recipe PDF

There are no long-running services, databases, or web servers. Local development is an offline build pipeline.

## Cursor Cloud specific instructions

### Prerequisites (one-time on a fresh Linux VM)

WeasyPrint needs system libraries. If PDF generation fails with missing-library errors, install:

```bash
sudo apt-get update
sudo apt-get install -y \
  libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
  libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info
```

Python **3.12** is required (matches `.github/workflows/build-release.yml`).

### Dependency refresh

Python packages are refreshed on VM startup via the update script (`pip install -r scripts/requirements-recipe-pdf.txt`). System packages are not reinstalled each session.

### Build commands (the “application”)

From the repo root:

```bash
# Combined cookbook (primary smoke test)
python3 scripts/cookbook_to_pdf.py -o output/cookbook.pdf

# Single recipe
python3 scripts/recipe_to_pdf.py recipes/main/burgers.md -o output/burgers.pdf
```

Success means `output/cookbook.pdf` exists and contains a TOC plus all recipes. The `output/` directory is gitignored.

### Lint and tests

There is no dedicated linter or test suite in this repo. CI (`.github/workflows/build-release.yml`) validates changes by building the cookbook PDF. Use that build as the local smoke test.

### CI / releases

GitHub Actions workflows (`dev.yml`, `tst.yml`, `prd.yml`) call `build-release.yml` to build PDFs and publish GitHub Release assets. That is optional for local development.

### Recipe authoring

Claude skills under `.claude/skills/` help normalize and add recipes; they are not part of the PDF build pipeline.
