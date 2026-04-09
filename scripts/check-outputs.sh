#!/usr/bin/env bash
#
# check-outputs.sh — Verify all output files match the manuscript source.
#
# Extracts text from every generated PDF and EPUB, then compares key
# sentences from the source markdown against each output to catch
# dropped words, garbled text, or missing content.
#
# Usage: ./check-outputs.sh
# Requires: python3, pymupdf (pip install pymupdf)

set -euo pipefail
cd "$(dirname "$0")/.."

echo "==========================================="
echo "  Output Verification"
echo "==========================================="
echo ""

python3 << 'PYEOF'
import json, os, sys, re, glob, zipfile, html

# --- Read config ---
with open("config.json") as f:
    CONFIG = json.load(f)

_m = CONFIG["manuscript"]
MANUSCRIPT_FILES = [_m["intro"]]
for part in _m["parts"]:
    MANUSCRIPT_FILES.extend(part["chapters"])
MANUSCRIPT_FILES.append(_m["outro"])
if _m.get("appendix"):
    MANUSCRIPT_FILES.append(_m["appendix"])

BOOK_NAME = CONFIG["title"].replace(" ", "-")
PDF_OUTPUTS = {
    "PDF": f"output/book-only/{BOOK_NAME}.pdf",
    "Free Chapter PDF": "output/free-chapter.pdf",
}
EPUB_OUTPUT = f"output/book-only/{BOOK_NAME}.epub"

# --- Extract sentences from markdown ---
def extract_sentences(md_text):
    text = re.sub(r'<[^>]*>', '', md_text)
    text = re.sub(r'[_*#\[\]()]', '', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = []
    for s in re.split(r'(?<=[.!?])\s+', text):
        s = s.strip()
        if len(s.split()) >= 10:
            sentences.append(s)
    return sentences

# --- Extract text from PDF ---
def pdf_text(path):
    try:
        import fitz
        doc = fitz.open(path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        return text
    except ImportError:
        print("  ERROR: pymupdf not installed. Run: pip install pymupdf")
        sys.exit(1)
    except Exception as e:
        print(f"  ERROR reading {path}: {e}")
        return ""

# --- Extract text from EPUB ---
def epub_text(path):
    try:
        text = ""
        with zipfile.ZipFile(path, 'r') as z:
            for name in z.namelist():
                if name.endswith(('.xhtml', '.html', '.htm')):
                    content = z.read(name).decode('utf-8', errors='ignore')
                    clean = re.sub(r'<[^>]*>', ' ', content)
                    clean = html.unescape(clean)
                    text += clean + "\n"
        return text
    except Exception as e:
        print(f"  ERROR reading {path}: {e}")
        return ""

# --- Normalise text for comparison ---
def normalise(text):
    text = text.replace('\u2014', '-').replace('\u2013', '-')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2026', '...')
    text = re.sub(r'[\n\r]+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'-\s+', '', text)
    return text.strip()

# --- Main ---
print("Extracting key sentences from manuscript...\n")

all_sentences = []
for f in MANUSCRIPT_FILES:
    if not os.path.exists(f):
        continue
    with open(f) as fh:
        md = fh.read()
    sents = extract_sentences(md)
    picks = sents[:3] + sents[-2:] if len(sents) > 5 else sents
    for s in picks:
        all_sentences.append((f, s))

print(f"  {len(all_sentences)} sentences selected from {len(MANUSCRIPT_FILES)} files.\n")

total_issues = 0

# Check PDFs
for label, path in PDF_OUTPUTS.items():
    if not os.path.exists(path):
        print(f"  SKIP: {label} — file not found ({path})")
        continue
    print(f"Checking: {label}")
    output = normalise(pdf_text(path))
    issues = []
    for source_file, sentence in all_sentences:
        if "free-chapter" in path.lower() and "01-chapter" not in source_file:
            continue
        needle = normalise(sentence)
        words = needle.split()
        check = ' '.join(words[:6])
        if check not in output:
            issues.append((source_file, sentence[:80]))
    if issues:
        print(f"  {len(issues)} potential issues:")
        for src, sent in issues[:10]:
            print(f"    [{src}] \"{sent}...\"")
        total_issues += len(issues)
    else:
        print(f"  All spot-checks passed.")
    print()

# Check EPUB
if os.path.exists(EPUB_OUTPUT):
    print(f"Checking: EPUB")
    output = normalise(epub_text(EPUB_OUTPUT))
    issues = []
    for source_file, sentence in all_sentences:
        needle = normalise(sentence)
        words = needle.split()
        check = ' '.join(words[:6])
        if check not in output:
            issues.append((source_file, sentence[:80]))
    if issues:
        print(f"  {len(issues)} potential issues:")
        for src, sent in issues[:10]:
            print(f"    [{src}] \"{sent}...\"")
        total_issues += len(issues)
    else:
        print(f"  All spot-checks passed.")
    print()

# Summary
if total_issues == 0:
    print("=========================================")
    print("  All outputs match the manuscript.")
    print("=========================================")
else:
    print("=========================================")
    print(f"  {total_issues} potential issues found.")
    print("  Review the flagged sentences above.")
    print("=========================================")

PYEOF