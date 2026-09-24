#!/bin/bash
# Create (once) a persistent venv for this skill and print its python path.
#
# Why this exists: system python3 on macOS usually has no openpyxl, and
# `pip install` fails under PEP 668 ("externally-managed-environment").
# Putting the venv in a session scratchpad does not survive - scratchpads get
# wiped mid-session. This lives inside the skill folder so it persists.
#
# Usage:  PY=$(bash ensure_venv.sh) && "$PY" tracker.py report ...
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="$SKILL_DIR/.venv"
PY="$VENV/bin/python"

if [ ! -x "$PY" ]; then
  python3 -m venv "$VENV" >&2
fi

if ! "$PY" -c "import openpyxl" 2>/dev/null; then
  "$VENV/bin/pip" install --quiet --upgrade pip >&2 2>/dev/null || true
  "$VENV/bin/pip" install --quiet openpyxl >&2
fi

echo "$PY"
