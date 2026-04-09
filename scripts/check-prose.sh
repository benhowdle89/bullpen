#!/usr/bin/env bash
#
# check-prose.sh — Run spelling, grammar & style checks on the manuscript
#
# Uses Vale (https://vale.sh) plus custom grammar spot-checks.
#
# Usage:
#   ./check-prose.sh                                    — check all chapters
#   ./check-prose.sh manuscript/part-1/01-chapter.md    — check a specific file
#
# CUSTOMISE: Update BOOK_FILES with your chapter file list.

set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v vale &> /dev/null; then
    echo "ERROR: vale is not installed."
    echo "Install with: brew install vale"
    exit 1
fi

# Read prose files from config.json
mapfile -t BOOK_FILES < <(python3 -c "
import json
c = json.load(open('config.json'))
m = c['manuscript']
print(m['intro'])
for part in m['parts']:
    for ch in part['chapters']:
        print(ch)
print(m['outro'])
if m.get('appendix'):
    print(m['appendix'])
")

if [ $# -gt 0 ]; then
    FILES=("$@")
else
    FILES=("${BOOK_FILES[@]}")
fi

echo "==========================================="
echo "  Prose Check"
echo "==========================================="
echo ""
echo "Checking ${#FILES[@]} file(s)..."
echo ""

vale "${FILES[@]}" || true

echo ""
echo "-------------------------------------------"
echo "  Grammar spot-checks (missing words, etc.)"
echo "-------------------------------------------"
echo ""

GRAMMAR_ISSUES=0

for f in "${FILES[@]}"; do
  # Check for repeated words ("the the", "is is", etc.)
  REPEATS=$(sed 's/<[^>]*>//g' "$f" | grep -niE '\b(\w+)\s+\1\b' || true)
  if [ -n "$REPEATS" ]; then
    while IFS= read -r line; do
      echo "  $f:$line  [repeated word]"
      GRAMMAR_ISSUES=$((GRAMMAR_ISSUES + 1))
    done <<< "$REPEATS"
  fi
done

if [ "$GRAMMAR_ISSUES" -eq 0 ]; then
  echo "  No grammar issues found."
else
  echo ""
  echo "  $GRAMMAR_ISSUES potential grammar issue(s) found above."
fi