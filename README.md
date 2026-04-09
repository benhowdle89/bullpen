<p align="center">
  <img src="logo.svg?v=2" alt="Bullpen" width="600">
</p>

<p align="center">
  <em>The self-publishing pipeline for authors who'd rather write than wrestle with tools.</em>
</p>

---

Write your book in markdown. Bullpen turns it into PDF, EPUB, MOBI, HTML, a KDP-ready paperback interior, a full cover wrap, and tiered digital packages  - ready to sell.

Built by [Ben Howdle](https://benhowdle.im).

## What this gives you

- **Write in markdown**  - one file per chapter, organised by part
- **Build to every format**  - PDF, EPUB, MOBI, HTML, and a KDP paperback interior
- **Two-tier packaging**  - a "book only" and a "book + extras" package for different price points
- **Free chapter lead magnet**  - generates a standalone PDF of one chapter for email signups
- **KDP paperback + cover**  - print-ready interior PDF and full cover wrap with spine
- **Prose linting**  - Vale integration with sensible defaults for narrative non-fiction
- **Output verification**  - spot-checks generated PDFs against source to catch dropped words
- **Quality audit framework**  - a scoring rubric for assessing your book before launch
- **Voice codification**  - a template for defining your writing voice to maintain consistency
- **Promotion content**  - templates for extracting social media posts from your chapters

## Quickstart

Clone the repo, open [Claude Code](https://docs.anthropic.com/en/docs/claude-code), and tell it about your book:

> "Install any missing dependencies, then set up this repo for my book called [title] by [name]. It has [n] parts with [n] chapters each."

Claude Code reads the `CLAUDE.md` in this repo automatically  - it knows the full project structure and will update `config.json`, create your chapter files, and install dependencies in one go.

When you're ready to build:

> "Run the full build pipeline."

## Getting started (manual)

If you're not using Claude Code, here's how to set up the repo yourself.

### 1. Install dependencies

```bash
brew install pandoc vale
brew install --cask calibre  # optional  - needed for MOBI generation
pip install -r requirements.txt
vale sync
```

### 2. Configure your book

Edit `config.json` with your book's title, author, subtitle, and chapter structure. All scripts read from this file automatically. See [Customisation](#customisation) below for per-script settings like CSS and cover colours.

### 3. Write your chapters

Edit the markdown files in `manuscript/`. One file per chapter, organised by part.

### 4. Build everything

```bash
./scripts/build-final.sh
```

This runs the full pipeline: markdown to HTML, EPUB, PDF, MOBI, output packages, and verification. On first run, it automatically installs Python dependencies and syncs Vale style packages if you haven't already.

Or run individual steps:

```bash
./scripts/build.sh                     # markdown → styled HTML
./scripts/check-prose.sh               # lint your prose
python3 scripts/generate_final.py      # HTML → EPUB + PDF
./scripts/package.sh                   # create output packages
./scripts/check-outputs.sh             # verify outputs match source
python3 scripts/generate_paperback.py  # KDP interior PDF
python3 scripts/generate_cover.py      # KDP cover wrap PDF
```

## Using with Claude Code

This repo is optimised for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). The `CLAUDE.md` file gives Claude full context on the pipeline, so you can ask it to:

- **Set up your book**  - update the title, author, and metadata across all config files at once
- **Add or reorder chapters**  - create new chapter files and update the file lists in all 5 scripts that need them
- **Run and debug builds**  - execute the pipeline, diagnose errors, and fix issues
- **Lint your prose**  - run Vale checks and fix warnings
- **Structure voice note transcriptions**  - turn raw dictation into formatted chapter drafts
- **Tweak styling**  - adjust CSS across the three output targets (HTML/PDF, EPUB, paperback)
- **Manage promotion content**  - extract social posts from your chapters
- **Pre-launch quality checks**  - run output verification and review the quality audit

## Directory structure

```
.
├── manuscript/           # Your book content (markdown)
│   ├── front-cover.md
│   ├── copyright.md
│   ├── dedications.md
│   ├── epigraph.md
│   ├── intro.md
│   ├── part-1/
│   │   ├── part-intro.md
│   │   ├── 01-chapter-title.md
│   │   ├── 02-chapter-title.md
│   │   └── 03-chapter-title.md
│   ├── part-2/
│   ├── part-3/
│   ├── outro.md
│   ├── appendix.md
│   └── about-the-author.md
├── styles/
│   └── epub.css          # EPUB stylesheet
├── images/
│   └── cover/
│       └── cover.jpg     # Front cover image (300 DPI)
├── output/               # Generated files (gitignored)
│   ├── book-only/
│   ├── book-plus-extras/
│   └── *.pdf
├── templates/            # Extra PDFs (if using tiered pricing)
├── promotion/            # Social media content
├── scripts/
│   ├── build.sh              # Markdown → HTML
│   ├── build-final.sh        # Full build pipeline
│   ├── package.sh            # Create output packages
│   ├── check-prose.sh        # Prose linting
│   ├── check-outputs.sh      # Output verification
│   ├── generate_final.py     # EPUB + PDF generation
│   ├── generate_paperback.py # KDP paperback interior
│   └── generate_cover.py     # KDP cover wrap
├── docs/
│   ├── PROGRESS.md           # Manuscript tracking
│   ├── QUALITY-AUDIT.md      # Pre-launch quality rubric
│   ├── writing-voice.md      # Your voice definition (fill in)
│   └── beta-reader-note.md   # Note for beta readers
├── config.json           # Book metadata  - single source of truth
├── requirements.txt      # Python dependencies
└── .vale.ini             # Prose linter config
```

## The pipeline

### Writing

Write your chapters in `manuscript/` as markdown files. One file per chapter. Organise by part.

Each chapter can follow whatever structure works for you. The pipeline doesn't enforce a structure  - it just concatenates your files in order and converts them.

### Building

`scripts/build.sh` assembles all markdown files into a single styled HTML document. Edit the file list and CSS to match your book.

`scripts/generate_final.py` takes that HTML and produces:
- EPUB (via pandoc)
- PDF (via weasyprint)
- A free chapter PDF with cover page and CTA (for email lead magnets)

### Packaging

`scripts/package.sh` creates output directories for each pricing tier:
- `output/book-only/`  - the book in all formats + a README
- `output/book-plus-extras/`  - the book + any extra PDFs (templates, worksheets, etc.)

Each directory is ready to upload to Google Drive, Gumroad, or wherever you deliver files.

### Quality control

- `scripts/check-prose.sh`  - runs Vale linting + custom grammar checks
- `scripts/check-outputs.sh`  - extracts sentences from your markdown and verifies they appear in the generated PDFs (catches conversion errors, dropped words, encoding issues)

### KDP paperback

`scripts/generate_paperback.py` produces a print-ready 6×9 inch interior PDF with:
- Proper KDP margins (including gutter calculation based on page count)
- Front matter (half title, title page, copyright, dedication, epigraph, TOC)
- Chapter and part page breaks
- Page numbering (suppressed on front matter and chapter openings)

`scripts/generate_cover.py` produces a full cover wrap PDF (back + spine + front) sized for KDP.

### Promotion

The `promotion/` directory holds ready-to-post social content extracted from your chapters. See `promotion/README.md` for the content calendar template.

## Customisation

### Book metadata

Edit `config.json`  - this is the single source of truth for your book's title, author, subtitle, chapter structure, and other metadata. All scripts read from it automatically.

### Styling

- Edit the CSS in `scripts/build.sh` for the HTML/PDF output
- Edit `styles/epub.css` for the EPUB
- Edit the CSS in `scripts/generate_paperback.py` for the paperback

### Per-script settings

Some settings stay in individual scripts (marked with `# CUSTOMISE`):
- `scripts/generate_cover.py`  - cover colours, back cover copy, page count
- `scripts/package.sh`  - README text for each pricing tier
- `scripts/generate_final.py`  - free chapter HTML template

## Credits

Created by [Ben Howdle](https://benhowdle.im).

## License

MIT  - use it for your own book, modify it, share it.