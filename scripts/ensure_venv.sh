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
# Windows (Git Bash) venvs put python in Scripts/, everything else in bin/.
vpy() { [ -x "$VENV/Scripts/python.exe" ] && echo "$VENV/Scripts/python.exe" || echo "$VENV/bin/python"; }
PY="$(vpy)"

if [ ! -x "$PY" ]; then
  SYS_PY="$(command -v python3 || command -v python)"
  "$SYS_PY" -m venv "$VENV" >&2
  PY="$(vpy)"
fi

if ! "$PY" -c "import openpyxl" 2>/dev/null; then
  "$PY" -m pip install --quiet --upgrade pip >&2 2>/dev/null || true
  "$PY" -m pip install --quiet openpyxl >&2
fi

echo "$PY"
