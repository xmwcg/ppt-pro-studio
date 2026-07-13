#!/usr/bin/env bash
# PPT Pro Studio — one-click installer (MIT-0).
# Copies this skill folder into the first detected agent "skills" directory,
# or into a path you pass as the first argument.
#
# Usage:
#   ./install.sh                 # auto-detect target skills dir
#   ./install.sh /path/to/skills # explicit target dir
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="ppt-pro-studio"

TARGET="${1:-}"
if [ -z "$TARGET" ]; then
  for d in \
    "$HOME/.workbuddy/skills" \
    "$HOME/.claude/skills" \
    "$HOME/.cursor/skills" \
    "$HOME/.codex/skills" ; do
    if [ -d "$d" ]; then TARGET="$d"; break; fi
  done
fi
if [ -z "$TARGET" ]; then
  TARGET="$HOME/.workbuddy/skills"
  mkdir -p "$TARGET"
fi

mkdir -p "$TARGET"
cp -r "$SCRIPT_DIR" "$TARGET/$SKILL_NAME"

echo "✅ Installed PPT Pro Studio -> $TARGET/$SKILL_NAME"
echo ""
echo "Requirements:"
echo "  - python3 + python-pptx   (pip install python-pptx)   [primary renderer + ⑥-B]"
echo "  - node >= 18              (for the optional MCP server)"
echo ""
echo "Premium path ⑥-B (SVG->PPTX) is self-contained: vendor/ppt-master-scripts is bundled,"
echo "no extra install needed. To use a system ppt-master instead, set PPT_MASTER_DIR."
echo ""
echo "Quick start:"
echo "  python3 $TARGET/$SKILL_NAME/scripts/ppt_studio_generate.py \\"
echo "      $TARGET/$SKILL_NAME/examples/sample-brief.json --out deck.pptx"
