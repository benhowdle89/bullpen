# Bullpen

A markdown-to-multi-format book publishing pipeline. Produces PDF, EPUB, MOBI, HTML, KDP paperback interior, and KDP cover wrap from markdown source files.

## Quick reference

```bash
./scripts/build.sh                    # Markdown → styled HTML
./scripts/check-prose.sh              # Vale linting + grammar checks
python3 scripts/generate_final.py     # HTML → EPUB + PDF + free chapter
./scripts/package.sh                  # Create output packages (book-only + premium)
./scripts/check-outputs.sh            # Verify outputs match source markdown
python3 scripts/generate_paperback.py # KDP 6×9 paperback interior PDF
python3 scripts/generate_cover.py     # KDP full cover wrap PDF
./scripts/build-final.sh              # Run the full pipeline end-to-end
```

## Project structure

- `manuscript/` — Book content as markdown. One file per chapter, organised by part (`part-1/`, `part-2/`, etc.). Front matter (cover, copyright, dedications, epigraph) and back matter (about-the-author, back-cover) are top-level in `manuscript/`.
- `scripts/` — All build, generation, packaging, and quality-check scripts.
- `docs/` — Writing support files: manuscript progress tracker, quality audit rubric, writing voice template, beta reader note.
- `styles/epub.css` — EPUB stylesheet. HTML/PDF styles live inline in `scripts/build.sh`. Paperback styles live in `scripts/generate_paperback.py`.
- `images/cover/` — Front cover image (300 DPI JPEG).
- `fonts/` — Custom fonts if needed.
- `output/` — All generated files (gitignored).
- `templates/` — Extra PDFs for premium tier (worksheets, frameworks, etc.).
- `promotion/` — Social media content extracted from chapters.

## config.json

`config.json` is the single source of truth for all book metadata: title, subtitle, author, language, website, year, buy URL, free chapter details, and the full manuscript structure (front matter, parts, chapters, back matter). All scripts read from it — no metadata is hardcoded in scripts.

When adding or removing chapters, update only `config.json`. When changing the title or author, update only `config.json`.

Per-script settings (CSS, cover colours, back cover copy, package READMEs) stay in individual scripts and are marked with `# CUSTOMISE` comments.

## Manuscript conventions

- Each chapter file starts with `# Chapter N: Title` followed by `*Subtitle in italics*`
- Use `##` for section headings within chapters (no page breaks)
- Use `<div class="pull-quote">...</div>` for pull quotes
- Use standard markdown blockquotes for regular quotes
- Horizontal rules (`---`) render as `* * *` section breaks in paperback
- Part intro files (`part-intro.md`) contain a short italic blurb shown on the part title page

## How to help

Claude Code assists with **formatting, structure, and build pipeline** tasks:
- Adding/reordering chapters in `config.json` and creating the corresponding markdown files
- Editing CSS styles across the three output targets (HTML/PDF, EPUB, paperback)
- Running and debugging the build pipeline
- Prose linting and fixing Vale warnings
- Transcribing and structuring voice note dictations into chapter drafts
- Updating metadata in `config.json`
- Managing the promotion content calendar
- Checking output quality with `scripts/check-outputs.sh`

All book prose is written by the author. Claude Code does not write or generate book content.

## File dependencies

All metadata and chapter structure lives in `config.json`. When adding chapters, removing chapters, or changing the title/author, update only `config.json` — all scripts read from it automatically.

When adding a new chapter:
1. Create the markdown file in `manuscript/part-N/`
2. Add it to the `parts[].chapters` array in `config.json`

## Prerequisites

```bash
brew install pandoc vale
brew install --cask calibre  # optional, for MOBI
pip install -r requirements.txt
vale sync
```

`scripts/build-final.sh` handles Python deps and Vale sync automatically on first run (creates a venv at `/tmp/book-publishing-venv`).

## Vale config

Vale is configured in `.vale.ini` with Google and proselint packages. Most technical-writing rules are disabled to suit narrative non-fiction. Custom vocabulary lives in `styles/config/vocabularies/Book/accept.txt`.
