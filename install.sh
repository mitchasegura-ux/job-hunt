#!/bin/bash
# Install this skill and its slash commands for Claude Code and/or Codex CLI.
#
# Usage:  ./install.sh [claude|codex|all]      (default: all)
#
# Symlinks, so `git pull` in this folder updates every install.
#   Claude Code: ~/.claude/skills/job-hunting  +  ~/.claude/commands/<cmd>.md
#   Codex CLI:   ~/.codex/skills/job-hunting   +  ~/.codex/prompts/<cmd>.md
#                (Codex runs prompts as /prompts:<cmd>, e.g. /prompts:job-status)
set -euo pipefail

SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="${1:-all}"

link() {  # link <home-dir> <commands-subdir>
  local home="$1" cmds="$2"
  mkdir -p "$home/skills" "$home/$cmds"
  ln -sfn "$SRC" "$home/skills/job-hunting"
  for f in "$SRC"/commands/*.md; do
    ln -sf "$f" "$home/$cmds/$(basename "$f")"
  done
  echo "installed -> $home/skills/job-hunting and $home/$cmds/"
}

case "$TARGET" in
  claude) link "$HOME/.claude" commands ;;
  codex)  link "${CODEX_HOME:-$HOME/.codex}" prompts ;;
  all)    link "$HOME/.claude" commands; link "${CODEX_HOME:-$HOME/.codex}" prompts ;;
  *)      echo "usage: $0 [claude|codex|all]" >&2; exit 1 ;;
esac

bash "$SRC/scripts/ensure_venv.sh" >/dev/null && echo "python venv ready"
