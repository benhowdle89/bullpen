#!/usr/bin/env bash
#
# build-final.sh — Full build pipeline
#
# Steps:
#   1. build.sh           — Markdown → styled HTML
#   2. generate_final.py  — EPUB + PDF + free chapter
#   3. package.sh         — Output packages
#   4. check-outputs.sh   — Verify outputs match source
#
# Usage: ./build-final.sh
# Output: ./output/

set -euo pipefail
SCRIPTS="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPTS/.."

echo "==========================================="
echo "  Bullpen — Full Build"
echo "==========================================="
echo ""

# --- Setup: Python venv + dependencies ---
VENV_DIR="/tmp/book-publishing-venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
pip install -r requirements.txt --quiet 2>/dev/null

# --- Setup: Vale styles ---
if [ ! -d "styles/Google" ] || [ ! -d "styles/proselint" ]; then
    echo "Syncing Vale style packages..."
    vale sync --quiet 2>/dev/null || vale sync 2>/dev/null
fi
echo ""

# --- 1. Build the manuscript HTML ---
echo "[1/4] Building manuscript HTML..."
"$SCRIPTS/build.sh"
echo ""

# --- 2. Assemble final deliverables ---
echo "[2/4] Assembling final deliverables..."
python3 "$SCRIPTS/generate_final.py"
echo ""

# --- 3. Package into tiers ---
echo "[3/4] Packaging output tiers..."
"$SCRIPTS/package.sh"
echo ""

# --- 4. Verify outputs match manuscript ---
echo "[4/4] Verifying outputs against source..."
"$SCRIPTS/check-outputs.sh"