#!/usr/bin/env python3
"""
Generate a print-ready interior PDF for Amazon KDP paperback.

Trim size: 6 x 9 inches
Interior: Black & white on cream paper
No bleed, no crop marks

Reads metadata and chapter structure from config.json.

Usage: python3 scripts/generate_paperback.py
Output: output/<title>-paperback-interior.pdf
"""

import json
import os
import re
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
MANUSCRIPT = os.path.join(BASE_DIR, "manuscript")

# --- Read config ---
with open(os.path.join(BASE_DIR, "config.json")) as f:
    CONFIG = json.load(f)

BOOK_TITLE = CONFIG["title"]
BOOK_SUBTITLE = CONFIG["subtitle"]
BOOK_AUTHOR = CONFIG["author"]
BOOK_WEBSITE = CONFIG["website"]
BOOK_YEAR = CONFIG["year"]

_m = CONFIG["manuscript"]
INTRO = _m["intro"]
OUTRO = _m["outro"]
APPENDIX = _m.get("appendix", "")
PARTS = [{"num": p["number"], "title": p["title"], "intro": p.get("intro", ""), "chapters": p["chapters"]} for p in _m["parts"]]

# KDP specs: adjust inside margin based on page count
# Under 150 pages: 0.75in. Over 150: 0.875in.
# Set this after your first build, based on the page count reported.
INSIDE_MARGIN = "0.75in"


def read_file(relpath):
    with open(os.path.join(BASE_DIR, relpath), "r") as f:
        return f.read()


def md_to_html(md_text):
    result = subprocess.run(
        ["pandoc", "--from", "markdown+smart+raw_html", "--to", "html5"],
        input=md_text, capture_output=True, text=True,
    )
    return result.stdout if result.returncode == 0 else md_text


def strip_html_divs(html):
    # Protect pull-quote divs
    html = re.sub(r'<div class="pull-quote">(.*?)</div>', r'<!--PQ-->\1<!--/PQ-->', html, flags=re.DOTALL)
    html = re.sub(r'<div[^>]*>', '', html)
    html = html.replace('</div>', '')
    html = html.replace('<!--PQ-->', '<div class="pull-quote">')
    html = html.replace('<!--/PQ-->', '</div>')
    return html


def build_html():
    # The full CSS and HTML assembly for a 6x9 KDP paperback.
    # This is long but self-contained — edit the CSS to change styling.

    css = f"""
@page {{
    size: 6in 9in;
    margin-top: 0.5in;
    margin-bottom: 0.6in;
    margin-inside: {INSIDE_MARGIN};
    margin-outside: 0.5in;
    @bottom-center {{
        content: counter(page);
        font-family: Georgia, serif;
        font-size: 8pt;
        color: #555;
    }}
}}
@page :blank {{ @bottom-center {{ content: none; }} }}
@page frontmatter {{ @bottom-center {{ content: none; }} }}
@page chapter-opening {{ @bottom-center {{ content: none; }} }}
@page part-page {{ @bottom-center {{ content: none; }} }}
@page blank-page {{ @bottom-center {{ content: none; }} }}

body {{
    font-family: Georgia, 'Times New Roman', serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #1a1a1a;
    widows: 3;
    orphans: 3;
}}
p {{ margin: 0 0 0.6em 0; text-indent: 0; text-align: left; }}
h1 {{
    font-size: 20pt; font-weight: bold;
    margin-top: 1.8in; margin-bottom: 0.15in;
    text-align: left; line-height: 1.2;
    page: chapter-opening;
    page-break-before: right;
}}
h2 {{
    font-size: 12pt; font-weight: bold;
    text-transform: uppercase; letter-spacing: 0.06em;
    color: #333; margin-top: 2.4em; margin-bottom: 1em;
    text-align: left;
}}
.chapter-subtitle {{ font-style: italic; font-size: 10.5pt; color: #444; margin-bottom: 0.4in; text-align: left; }}
.pull-quote {{
    margin: 1.2em 0.3in; padding: 0.6em 0;
    border-top: 1pt solid #999; border-bottom: 1pt solid #999;
    text-align: center; font-style: italic; font-size: 11.5pt; color: #222;
}}
blockquote {{ margin: 1em 0 1em 0.3in; font-style: italic; font-size: 10.5pt; color: #333; border: none; }}
blockquote p {{ text-align: left; font-style: italic; margin-bottom: 0.4em; }}
ul, ol {{ margin: 0.8em 0; padding-left: 0.4in; }}
li {{ margin-bottom: 0.4em; text-align: left; }}
li p {{ text-align: left; }}
hr {{ border: none; text-align: center; margin: 1.5em 0; }}
hr::after {{ content: "* * *"; font-size: 10pt; color: #888; letter-spacing: 0.3em; }}

.half-title {{ page: frontmatter; page-break-before: right; page-break-after: always; text-align: center; padding-top: 3in; }}
.half-title h1 {{ font-size: 24pt; text-transform: uppercase; margin: 0; page-break-before: avoid; }}
.blank-verso {{ page: blank-page; page-break-before: always; page-break-after: always; height: 0; }}
.title-page {{ page: frontmatter; page-break-before: right; page-break-after: always; text-align: center; padding-top: 2.5in; }}
.title-page .book-title {{ font-size: 28pt; font-weight: bold; text-transform: uppercase; margin-bottom: 0.2in; }}
.title-page .book-subtitle {{ font-size: 14pt; font-style: italic; color: #444; margin-bottom: 0.6in; }}
.title-page .book-author {{ font-size: 13pt; color: #555; letter-spacing: 0.08em; text-transform: uppercase; }}
.copyright-page {{ page: frontmatter; page-break-after: always; padding-top: 5in; font-size: 9pt; color: #555; line-height: 1.7; }}
.copyright-page p {{ text-align: left; margin-bottom: 0.3em; }}
.dedication-page {{ page: frontmatter; page-break-before: right; page-break-after: always; text-align: center; padding-top: 3in; }}
.dedication-page p {{ text-align: center; font-style: italic; margin-bottom: 0.3em; }}
.epigraph-page {{ page: frontmatter; page-break-before: right; page-break-after: always; text-align: center; padding-top: 3in; }}
.epigraph-page blockquote {{ font-size: 11pt; font-style: italic; color: #333; max-width: 3.8in; margin: 0 auto; text-align: center; border: none; }}
.epigraph-page .attribution {{ font-style: normal; font-size: 9.5pt; color: #777; margin-top: 0.8em; }}
.toc-page {{ page: frontmatter; page-break-before: right; page-break-after: always; }}
.toc-page h2 {{ text-align: center; font-size: 14pt; text-transform: uppercase; letter-spacing: 0.12em; margin-top: 1.2in; margin-bottom: 0.5in; color: #333; }}
.toc-entry {{ font-size: 10pt; margin: 0.2em 0; padding-left: 0.2in; }}
.toc-entry-major {{ font-size: 10.5pt; font-weight: bold; margin-top: 1em; padding-left: 0; }}
.toc-part {{ margin-top: 1em; margin-bottom: 0.3em; }}
.toc-part-label {{ font-size: 8.5pt; text-transform: uppercase; letter-spacing: 0.1em; color: #888; display: block; }}
.toc-part-name {{ font-size: 11pt; font-weight: bold; }}
.part-title-page {{ page: part-page; page-break-before: right; page-break-after: always; text-align: center; padding-top: 2.8in; }}
.part-title-page .part-label {{ font-size: 10pt; text-transform: uppercase; letter-spacing: 0.15em; color: #888; margin-bottom: 0.15in; }}
.part-title-page .part-name {{ font-size: 22pt; font-weight: bold; margin-bottom: 0.4in; }}
.part-title-page .part-intro {{ font-size: 10.5pt; font-style: italic; color: #555; max-width: 4in; margin: 0 auto; text-align: center; }}
.about-page {{ page-break-before: right; page: chapter-opening; }}
.about-page h2 {{ text-align: center; margin-top: 1.8in; margin-bottom: 0.5in; }}
.about-page p {{ text-align: left; line-height: 1.6; }}
.promo-page {{ page: blank-page; page-break-before: right; text-align: center; padding-top: 3in; }}
.promo-page p {{ text-align: center; font-size: 11pt; color: #333; }}
.promo-page .promo-url {{ font-size: 12pt; font-weight: bold; margin-top: 0.3in; }}
"""

    sections = []

    # Half title
    sections.append(f'<div class="half-title"><h1>{BOOK_TITLE}</h1></div><div class="blank-verso"></div>')

    # Title page
    sections.append(f'''
<div class="title-page">
  <div class="book-title">{BOOK_TITLE}</div>
  <div class="book-subtitle">{BOOK_SUBTITLE}</div>
  <div class="book-author">{BOOK_AUTHOR}</div>
</div>''')

    # Copyright — CUSTOMISE
    sections.append(f'''
<div class="copyright-page">
  <p><em>{BOOK_TITLE}: {BOOK_SUBTITLE}</em></p>
  <p>&copy; {BOOK_YEAR} {BOOK_AUTHOR}. All rights reserved.</p>
  <p>No part of this book may be reproduced without written permission from the author.</p>
  <p>&nbsp;</p>
  <p>Published by {BOOK_AUTHOR}</p>
  <p>{BOOK_WEBSITE}</p>
  <p>&nbsp;</p>
  <p>First edition, {BOOK_YEAR}</p>
</div>''')

    # Dedication — CUSTOMISE or remove
    sections.append('''
<div class="dedication-page">
  <p><em>Your dedication here.</em></p>
</div>''')

    # Epigraph — CUSTOMISE or remove
    sections.append('''
<div class="epigraph-page">
  <blockquote>"Your favourite quote."</blockquote>
  <p class="attribution">&mdash; Attribution</p>
</div>''')

    # TOC
    toc = '<div class="toc-page"><h2>Contents</h2>\n'
    toc += '<p class="toc-entry-major">Intro</p>\n'
    ch_num = 1
    for part in PARTS:
        toc += f'<div class="toc-part"><span class="toc-part-label">Part {part["num"]}</span> '
        toc += f'<span class="toc-part-name">{part["title"]}</span></div>\n'
        for chap_file in part["chapters"]:
            chap_md = read_file(chap_file)
            match = re.search(r'^#\s+(.+)$', chap_md, re.MULTILINE)
            title = re.sub(r'^Chapter\s+\d+:\s*', '', match.group(1)).strip() if match else f"Chapter {ch_num}"
            toc += f'<p class="toc-entry">{ch_num}. {title}</p>\n'
            ch_num += 1
    toc += '<p class="toc-entry-major">Outro</p>\n'
    toc += '</div>\n'
    sections.append(toc)

    # Intro
    intro_html = strip_html_divs(md_to_html(read_file(INTRO)))
    sections.append(intro_html)

    # Parts and chapters
    for part in PARTS:
        part_intro = read_file(part["intro"]).strip()
        sections.append(f'''
<div class="part-title-page">
  <div class="part-label">Part {part['num']}</div>
  <div class="part-name">{part['title']}</div>
  <p class="part-intro">{part_intro}</p>
</div>''')
        for chap_file in part["chapters"]:
            chap_html = md_to_html(read_file(chap_file))
            # Extract and relocate subtitle
            sub_match = re.search(r'<p><em>(.+?)</em></p>', chap_html)
            if sub_match:
                chap_html = chap_html.replace(sub_match.group(0), '', 1)
                chap_html = re.sub(r'(</h1>)', f'\\1\n<p class="chapter-subtitle"><em>{sub_match.group(1)}</em></p>', chap_html, count=1)
            chap_html = strip_html_divs(chap_html)
            sections.append(chap_html)

    # Outro
    sections.append(strip_html_divs(md_to_html(read_file(OUTRO))))

    # Appendix (if exists)
    appendix_path = os.path.join(BASE_DIR, APPENDIX)
    if os.path.exists(appendix_path):
        sections.append(strip_html_divs(md_to_html(read_file(APPENDIX))))

    # About the author
    sections.append(f'''
<div class="about-page">
  <h2>About the Author</h2>
  <p>Your bio here.</p>
</div>''')

    # Promo page — CUSTOMISE or remove
    sections.append(f'''
<div class="promo-page">
  <p>For more, visit:</p>
  <p class="promo-url">{BOOK_WEBSITE}</p>
</div>''')

    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"/><title>{BOOK_TITLE}</title>
<style>{css}</style>
</head>
<body>{"".join(sections)}</body>
</html>"""


def main():
    print(f"\n=== KDP Paperback Interior ===\n")

    if not subprocess.run(["which", "pandoc"], capture_output=True).returncode == 0:
        print("ERROR: pandoc not found."); sys.exit(1)
    try:
        from weasyprint import HTML
    except ImportError:
        print("ERROR: weasyprint not found."); sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("  Assembling manuscript HTML...")
    html_content = build_html()

    print("  Generating PDF...")
    pdf_path = os.path.join(OUTPUT_DIR, f"{BOOK_TITLE.replace(' ', '-')}-paperback-interior.pdf")
    from weasyprint import HTML as WH
    WH(string=html_content, base_url=BASE_DIR).write_pdf(pdf_path)

    # Count pages
    try:
        import fitz
        doc = fitz.open(pdf_path)
        pages = doc.page_count
        doc.close()
        print(f"\n  Generated: {os.path.basename(pdf_path)}")
        print(f"  Pages: {pages}")
        if pages > 150:
            print(f"  Note: Over 150 pages — set INSIDE_MARGIN = '0.875in' in this script.")
        spine = pages * 0.0025
        print(f"  Estimated spine: {spine:.3f} inches")
    except ImportError:
        print(f"\n  Generated: {os.path.basename(pdf_path)}")
        print(f"  (Install pymupdf for page count)")

    print(f"  Output: {pdf_path}\n")


if __name__ == "__main__":
    main()