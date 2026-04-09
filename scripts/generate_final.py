#!/usr/bin/env python3
"""
Assembles the final deliverable folder.

Generates:
  - EPUB via pandoc
  - PDF via weasyprint (from the HTML produced by build.sh)
  - Free chapter PDF (standalone lead magnet)

Reads metadata and chapter list from config.json.

Output: ./output/
"""

import json
import os
import re
import shutil
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# --- Read config ---
with open(os.path.join(BASE_DIR, "config.json")) as f:
    CONFIG = json.load(f)

BOOK_TITLE = CONFIG["title"]
BOOK_SUBTITLE = CONFIG["subtitle"]
BOOK_AUTHOR = CONFIG["author"]
BOOK_LANG = CONFIG["language"]
BUY_URL = CONFIG["buy_url"]

OUTPUT_NAME = BOOK_TITLE.replace(" ", "-")
HTML_FILE = os.path.join(OUTPUT_DIR, f"{OUTPUT_NAME}.html")

FREE_CHAPTER_FILE = CONFIG["free_chapter"]["file"]
FREE_CHAPTER_TITLE = CONFIG["free_chapter"]["title"]

# Build ordered chapter list from manuscript structure
_m = CONFIG["manuscript"]
CHAPTERS = list(_m["front_matter"])
CHAPTERS.append(_m["intro"])
for part in _m["parts"]:
    CHAPTERS.extend(part["chapters"])
CHAPTERS.append(_m["outro"])
if _m.get("appendix"):
    CHAPTERS.append(_m["appendix"])
CHAPTERS.extend(_m["back_matter"])

EPUB_CSS = os.path.join(BASE_DIR, "styles", "epub.css")


def check_dependency(cmd, name, install_hint):
    if shutil.which(cmd) is None:
        print(f"  WARNING: {name} not found. Install with: {install_hint}")
        return False
    return True


def generate_epub():
    """Generate EPUB using pandoc."""
    print("  Building EPUB...")

    if not check_dependency("pandoc", "pandoc", "brew install pandoc"):
        return False

    epub_path = os.path.join(OUTPUT_DIR, f"{BOOK_TITLE.replace(' ', '-')}.epub")
    input_files = [os.path.join(BASE_DIR, f) for f in CHAPTERS]

    missing = [f for f in input_files if not os.path.exists(f)]
    if missing:
        print(f"  ERROR: Missing files: {missing}")
        return False

    cmd = [
        "pandoc",
        "--from", "markdown+smart+raw_html",
        "--to", "epub3",
        "--output", epub_path,
        "--metadata", f"title={BOOK_TITLE}: {BOOK_SUBTITLE}",
        "--metadata", f"author={BOOK_AUTHOR}",
        "--metadata", f"lang={BOOK_LANG}",
        "--toc",
        "--toc-depth=1",
    ]
    if os.path.exists(EPUB_CSS):
        cmd += ["--css", EPUB_CSS]
    cmd += input_files

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: pandoc failed:\n{result.stderr}")
        return False

    print(f"  Done.")
    return True


def generate_pdf():
    """Generate PDF from the HTML file using weasyprint."""
    print("  Building PDF...")

    if not os.path.exists(HTML_FILE):
        print(f"  ERROR: {HTML_FILE} not found. Run build.sh first.")
        return False

    try:
        from weasyprint import HTML
        pdf_path = os.path.join(OUTPUT_DIR, f"{BOOK_TITLE.replace(' ', '-')}.pdf")
        HTML(filename=HTML_FILE).write_pdf(pdf_path)
        print(f"  Done.")
        return True
    except ImportError:
        print("  WARNING: weasyprint not available — skipping PDF.")
        return False


def copy_html():
    """Verify the styled HTML version exists in output/."""
    print("  Checking HTML version...")
    if not os.path.exists(HTML_FILE):
        print(f"  ERROR: {HTML_FILE} not found. Run build.sh first.")
        return False
    print(f"  Done.")
    return True


def generate_free_chapter():
    """Generate a standalone PDF of one chapter for use as a lead magnet."""
    if FREE_CHAPTER_FILE is None:
        return True

    print("  Building free chapter PDF...")

    chapter_path = os.path.join(BASE_DIR, FREE_CHAPTER_FILE)
    if not os.path.exists(chapter_path):
        print(f"  ERROR: {chapter_path} not found.")
        return False

    if not check_dependency("pandoc", "pandoc", "brew install pandoc"):
        return False

    with open(chapter_path, "r") as f:
        chapter_md = f.read()

    # Convert chapter markdown to HTML body via pandoc
    result = subprocess.run(
        ["pandoc", "--from", "markdown+smart+raw_html", "--to", "html5"],
        input=chapter_md, capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"  ERROR: pandoc failed:\n{result.stderr}")
        return False

    chapter_body = result.stdout

    # CUSTOMISE: Edit the HTML template to match your branding
    html_content = f"""<!DOCTYPE html>
<html lang="{BOOK_LANG}">
<head><meta charset="utf-8"/>
<style>
  @page {{ size: A5; margin: 2cm; @bottom-center {{ content: none; }} }}
  body {{ font-family: Georgia, serif; max-width: 38em; margin: 0 auto; padding: 2em; line-height: 1.6; color: #1a1a1a; }}
  .cover {{ text-align: center; padding: 6em 0 4em; page-break-after: always; min-height: 80vh;
    display: flex; flex-direction: column; justify-content: center; align-items: center; }}
  .cover-label {{ font-size: 0.85em; text-transform: uppercase; letter-spacing: 0.12em; color: #888; margin-bottom: 2em; }}
  .cover-title {{ font-size: 2.4em; font-weight: bold; margin-bottom: 0.3em; line-height: 1.1; }}
  .cover-subtitle {{ font-size: 1.1em; font-style: italic; color: #555; margin-bottom: 2em; }}
  .cover-author {{ font-size: 1em; color: #777; text-transform: uppercase; letter-spacing: 0.1em; }}
  .cover-chapter {{ margin-top: 3em; font-size: 1.1em; color: #333; border-top: 1px solid #ccc; padding-top: 1.5em; }}
  h1 {{ font-size: 1.6em; margin-top: 2em; margin-bottom: 0.6em; }}
  h2 {{ font-size: 1.1em; margin-top: 2em; color: #444; text-transform: uppercase; letter-spacing: 0.05em; }}
  p {{ margin-bottom: 1em; text-align: left; }}
  blockquote {{ border-left: 3px solid #ccc; margin: 1.5em 0; padding: 0.5em 1.2em; color: #555; font-style: italic; }}
  .pull-quote {{ border-left: none; border-top: 2px solid #333; border-bottom: 2px solid #333;
    margin: 2em 1.5em; padding: 1em 0; text-align: center; font-style: italic; font-size: 1.1em; }}
  .cta {{ page-break-before: always; text-align: center; padding: 8em 2em; }}
  .cta h2 {{ font-size: 1.3em; text-transform: none; letter-spacing: normal; color: #1a1a1a; margin-bottom: 1em; }}
  .cta p {{ font-size: 1em; color: #333; text-align: center; max-width: 28em; margin: 0 auto; }}
  .cta a {{ color: #1a1a1a; font-weight: bold; }}
</style>
</head>
<body>
<div class="cover">
  <div class="cover-label">Free Sample Chapter</div>
  <div class="cover-title">{BOOK_TITLE}</div>
  <div class="cover-subtitle">{BOOK_SUBTITLE}</div>
  <div class="cover-author">{BOOK_AUTHOR}</div>
  <div class="cover-chapter">{FREE_CHAPTER_TITLE}</div>
</div>
{chapter_body}
<div class="cta">
  <h2>Enjoyed this chapter?</h2>
  <p>This is one chapter from <em>{BOOK_TITLE}: {BOOK_SUBTITLE}</em>.</p>
  <p style="margin-top: 1.5em;"><a href="{BUY_URL}">Get the full book &rarr;</a></p>
</div>
</body></html>"""

    tmp_html = os.path.join(BASE_DIR, ".free-chapter.html")
    pdf_path = os.path.join(OUTPUT_DIR, "free-chapter.pdf")

    try:
        with open(tmp_html, "w") as f:
            f.write(html_content)
        from weasyprint import HTML as WeasyprintHTML
        WeasyprintHTML(filename=tmp_html).write_pdf(pdf_path)
        print(f"  Done.")
        return True
    except ImportError:
        print("  WARNING: weasyprint not available — skipping free chapter PDF.")
        return False
    finally:
        if os.path.exists(tmp_html):
            os.remove(tmp_html)


def main():
    print(f"\nAssembling final deliverables to: {OUTPUT_DIR}\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    results = {}
    results["epub"] = generate_epub()
    results["pdf"] = generate_pdf()
    results["html"] = copy_html()
    results["free_chapter"] = generate_free_chapter()

    failures = [k for k, v in results.items() if not v]
    if failures:
        print(f"\n  Some steps had issues: {', '.join(failures)}\n")
    else:
        print("\n  All done!\n")


if __name__ == "__main__":
    main()