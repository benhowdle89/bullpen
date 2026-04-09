#!/bin/bash
set -e

# ──────────────────────────────────────────────
# Build script for your book manuscript
# Assembles all markdown files into a styled HTML
#
# Reads metadata and chapter list from config.json.
# CUSTOMISE: Edit the CSS below to match your design.
#
# Usage:  ./scripts/build.sh
# Output: output/<title>.html
# ──────────────────────────────────────────────

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANUSCRIPT="$ROOT/manuscript"
CONFIG="$ROOT/config.json"
COMBINED="$ROOT/.manuscript-combined.md"

# --- Read config ---
BOOK_TITLE=$(python3 -c "import json; print(json.load(open('$CONFIG'))['title'])")
OUTPUT_NAME=$(python3 -c "import json; print(json.load(open('$CONFIG'))['title'].replace(' ', '-'))")

if ! command -v pandoc &> /dev/null; then
  echo "Error: pandoc is not installed."
  echo "Install it with:  brew install pandoc"
  exit 1
fi

echo "Assembling manuscript..."

cat /dev/null > "$COMBINED"

append_file() {
  cat "$1" >> "$COMBINED"
  printf '\n\n' >> "$COMBINED"
}

append_part_title() {
  local part_num="$1"
  local part_name="$2"
  local part_intro_file="$3"
  if [ -n "$part_intro_file" ] && [ -f "$part_intro_file" ]; then
    local subtitle
    subtitle="$(cat "$part_intro_file" | tr '\n' ' ' | sed 's/  */ /g;s/ *$//')"
    printf '\\newpage\n\n<div class="part-title" id="part-%s"><span class="part-label">Part %s</span><br/>%s<p class="part-subtitle">%s</p></div>\n\n' "$part_num" "$part_num" "$part_name" "$subtitle" >> "$COMBINED"
  else
    printf '\\newpage\n\n<div class="part-title" id="part-%s"><span class="part-label">Part %s</span><br/>%s</div>\n\n' "$part_num" "$part_num" "$part_name" >> "$COMBINED"
  fi
}

append_chapter_break() {
  printf '\\newpage\n\n' >> "$COMBINED"
}

append_page_break() {
  printf '\n\n<div class="page-break"></div>\n\n' >> "$COMBINED"
}

# ── Assemble from config.json ────────────────

python3 -c "
import json
c = json.load(open('$CONFIG'))
m = c['manuscript']
for f in m['front_matter']:
    print(f'file|{f}')
    print('page_break')
print('chapter_break')
print(f'file|{m[\"intro\"]}')
for part in m['parts']:
    intro = part.get('intro', '')
    print(f'part|{part[\"number\"]}|{part[\"title\"]}|{intro}')
    for i, ch in enumerate(part['chapters']):
        if i > 0: print('chapter_break')
        print(f'file|{ch}')
print('chapter_break')
print(f'file|{m[\"outro\"]}')
if m.get('appendix'):
    print('chapter_break')
    print(f'file|{m[\"appendix\"]}')
for f in m['back_matter']:
    print('chapter_break')
    print(f'file|{f}')
" | while IFS='|' read -r type arg1 arg2 arg3; do
    case "$type" in
        file) append_file "$ROOT/$arg1" ;;
        page_break) append_page_break ;;
        chapter_break) append_chapter_break ;;
        part) append_part_title "$arg1" "$arg2" "$ROOT/$arg3" ;;
    esac
done

# ── Convert to styled HTML ──────────────────
# CUSTOMISE: Edit the CSS below to match your book's design

echo "Converting to HTML..."
mkdir -p "$ROOT/output"

pandoc "$COMBINED" \
  --standalone \
  --from markdown+smart+raw_html \
  --to html5 \
  --css /dev/null \
  --metadata title="$BOOK_TITLE" \
  --variable header-includes="<style>
    @page {
      size: A5;
      margin: 2cm 2cm 2.5cm 2cm;
      @bottom-center {
        content: counter(page);
        font-family: Georgia, 'Times New Roman', serif;
        font-size: 9pt;
        color: #888;
      }
    }
    .front-cover, .dedications, .epigraph, .part-title, .copyright-page {
      page: no-number;
    }
    @page no-number { @bottom-center { content: none; } }
    @media print {
      .page-break { page-break-after: always; }
      .part-title { page-break-before: always; }
    }
    html { font-size: 16px; }
    body {
      font-family: Georgia, 'Times New Roman', serif;
      max-width: 38em;
      margin: 0 auto;
      padding: 2em 1.5em;
      line-height: 1.7;
      color: #1a1a1a;
      background: #fff;
    }
    .front-cover {
      text-align: center;
      padding: 8em 0 6em;
      page-break-after: always;
      min-height: 80vh;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
    }
    .cover-title { font-size: 3em; font-weight: bold; margin-bottom: 0.3em; line-height: 1.1; }
    .cover-subtitle { font-size: 1.3em; font-style: italic; color: #555; margin-bottom: 2em; }
    .cover-author { font-size: 1.1em; color: #777; text-transform: uppercase; letter-spacing: 0.1em; }
    .dedications {
      text-align: center; padding: 10em 2em; page-break-after: always;
      display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 3em;
    }
    .dedication { display: flex; flex-direction: column; align-items: center; gap: 0.4em; }
    .dedication-to { font-style: italic; font-size: 1.15em; }
    .dedication-reason { font-style: italic; font-size: 0.9em; color: #888; }
    .epigraph {
      text-align: center; padding: 10em 3em; page-break-after: always;
      display: flex; flex-direction: column; justify-content: center; align-items: center;
    }
    .epigraph blockquote { border-left: none; font-size: 1.2em; color: #333; font-style: italic; text-align: center; }
    .epigraph-attribution { margin-top: 1.5em; font-style: normal; font-size: 0.9em; color: #777; }
    .copyright-page { page-break-after: always; padding: 12em 2em 6em; font-size: 0.85em; color: #555; line-height: 1.8; }
    .part-title {
      text-align: center; padding: 6em 0;
      page-break-before: always; page-break-after: always;
      font-size: 1.8em; font-weight: bold; line-height: 1.4;
    }
    .part-title .part-label { font-size: 0.55em; text-transform: uppercase; letter-spacing: 0.15em; color: #888; font-weight: normal; }
    .part-subtitle { font-size: 0.5em; font-weight: normal; font-style: italic; color: #555; max-width: 20em; margin: 1.5em auto 0; line-height: 1.6; }
    .page-break { page-break-after: always; height: 0; }
    header { display: none; }
    h1 { font-size: 1.6em; margin-top: 2.5em; margin-bottom: 0.6em; line-height: 1.3; page-break-before: always; }
    h1:first-of-type { page-break-before: avoid; }
    h2 { font-size: 1.1em; margin-top: 2em; margin-bottom: 0.5em; text-transform: uppercase; letter-spacing: 0.05em; color: #444; }
    p { margin-bottom: 1em; text-align: left; orphans: 3; widows: 3; }
    blockquote { border-left: 3px solid #ccc; margin: 1.5em 0; padding: 0.5em 1.2em; color: #555; font-style: italic; }
    .pull-quote {
      border-left: none; border-top: 2px solid #333; border-bottom: 2px solid #333;
      margin: 2em 1.5em; padding: 1.2em 0; text-align: center;
      font-size: 1.15em; font-style: italic; color: #222;
    }
    hr { border: none; border-top: 1px solid #ddd; margin: 3em 0; }
    ul, ol { margin: 1em 0; padding-left: 1.8em; }
    li { margin-bottom: 0.4em; }
    .about-author { page-break-before: always; padding: 4em 0; }
    .about-author h2 { text-align: center; margin-bottom: 2em; }
    .back-cover { page-break-before: always; padding: 6em 2em; }
  </style>" \
  -o "$ROOT/output/$OUTPUT_NAME.html"

rm -f "$COMBINED"

echo ""
echo "Done! Output: output/$OUTPUT_NAME.html"