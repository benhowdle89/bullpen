#!/usr/bin/env bash
#
# package.sh — Create output packages for different pricing tiers
#
# Reads from ./output/ and creates:
#   output/book-only/         — Basic tier (book in all formats)
#   output/book-plus-extras/  — Premium tier (book + extra PDFs)
#
# CUSTOMISE: Update file paths, README text, and tier contents.
#
# Usage: ./package.sh
# Prerequisite: run generate_final.py first

set -euo pipefail
cd "$(dirname "$0")/.."

BOOK_NAME=$(python3 -c "import json; print(json.load(open('config.json'))['title'].replace(' ', '-'))")
OUTPUT_DIR="./output"
BOOK_ONLY="$OUTPUT_DIR/book-only"
PREMIUM="$OUTPUT_DIR/book-plus-extras"

echo "==========================================="
echo "  Packaging"
echo "==========================================="
echo ""

# ── Verify build output exists ──────────────
for f in "$BOOK_NAME.pdf" "$BOOK_NAME.epub"; do
  if [ ! -f "$OUTPUT_DIR/$f" ]; then
    echo "ERROR: $OUTPUT_DIR/$f not found. Run generate_final.py first."
    exit 1
  fi
done

# ── Generate Mobi from EPUB (if Calibre available) ──
MOBI_FILE="$OUTPUT_DIR/$BOOK_NAME.mobi"
if [ ! -f "$MOBI_FILE" ]; then
  if command -v ebook-convert &> /dev/null; then
    echo "Generating Mobi from EPUB..."
    ebook-convert "$OUTPUT_DIR/$BOOK_NAME.epub" "$MOBI_FILE" --no-inline-toc > /dev/null 2>&1
    echo "  Done."
  else
    echo "WARNING: ebook-convert (Calibre) not found — Mobi will be skipped."
    echo "  Install with: brew install --cask calibre"
    MOBI_FILE=""
  fi
fi
echo ""

# ── Clean output directories ────────────────
echo "Preparing output directories..."
rm -rf "$BOOK_ONLY" "$PREMIUM"
mkdir -p "$BOOK_ONLY" "$PREMIUM"
echo ""

# ── Book Only package ───────────────────────
echo "Packaging: Book Only..."
cp "$OUTPUT_DIR/$BOOK_NAME.pdf"  "$BOOK_ONLY/"
cp "$OUTPUT_DIR/$BOOK_NAME.epub" "$BOOK_ONLY/"
if [ -f "$OUTPUT_DIR/$BOOK_NAME.html" ]; then
  cp "$OUTPUT_DIR/$BOOK_NAME.html" "$BOOK_ONLY/"
fi
if [ -n "$MOBI_FILE" ] && [ -f "$MOBI_FILE" ]; then
  cp "$MOBI_FILE" "$BOOK_ONLY/"
fi

# CUSTOMISE: Edit this README for your book
cat > "$BOOK_ONLY/README.txt" << 'EOF'
Your Book Title: Your Subtitle
By Your Name

Thank you for your purchase.

This folder contains the book in multiple formats:
- PDF (for desktop, tablets, and printing)
- ePub (for Apple Books and most e-readers)
- Mobi (for Kindle — sideload via Send to Kindle)

DRM-free. Read it anywhere.

Questions? you@yourwebsite.com
EOF
echo "  Done."
echo ""

# ── Premium package ─────────────────────────
echo "Packaging: Premium..."
cp "$OUTPUT_DIR/$BOOK_NAME.pdf"  "$PREMIUM/"
cp "$OUTPUT_DIR/$BOOK_NAME.epub" "$PREMIUM/"
if [ -f "$OUTPUT_DIR/$BOOK_NAME.html" ]; then
  cp "$OUTPUT_DIR/$BOOK_NAME.html" "$PREMIUM/"
fi
if [ -n "$MOBI_FILE" ] && [ -f "$MOBI_FILE" ]; then
  cp "$MOBI_FILE" "$PREMIUM/"
fi

# CUSTOMISE: Copy any extra files (templates, worksheets, etc.)
# if [ -d "./templates" ]; then
#   mkdir -p "$PREMIUM/templates"
#   cp ./templates/*.pdf "$PREMIUM/templates/"
# fi

# CUSTOMISE: Edit this README for your premium tier
cat > "$PREMIUM/README.txt" << 'EOF'
Your Book Title: Your Subtitle — Premium Edition
By Your Name

Thank you for your purchase.

This folder contains the book plus bonus materials.

DRM-free.

Questions? you@yourwebsite.com
EOF
echo "  Done."
echo ""

# ── Free chapter ────────────────────────────
if [ -f "$OUTPUT_DIR/free-chapter.pdf" ]; then
  echo "Free chapter PDF ready at: $OUTPUT_DIR/free-chapter.pdf"
fi
echo ""

# ── Summary ─────────────────────────────────
echo "==========================================="
echo "  Packaging complete!"
echo ""
echo "  Book Only ($BOOK_ONLY/):"
for f in "$BOOK_ONLY"/*; do [ -f "$f" ] && echo "    $(basename "$f")"; done
echo ""
echo "  Premium ($PREMIUM/):"
for f in "$PREMIUM"/*; do [ -f "$f" ] && echo "    $(basename "$f")"; done
echo "==========================================="