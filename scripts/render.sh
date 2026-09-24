#!/bin/bash
# Render a packet's .md files to .docx/.pdf, verify page counts, and remove
# any rendered JOB.* files.
#
# That last part matters. JOB.md holds interview-odds estimates and candid
# warnings written for the candidate, not the employer. If it renders to PDF it
# ends up sitting in the same folder as the files being uploaded, one
# mis-click away from going out. Rendering it has no upside.
#
# Usage: render.sh <packet-dir> [latex-header.tex]
#
# Needs pandoc + xelatex. Font defaults to Helvetica Neue (macOS); set
# JOBHUNT_FONT to any installed font elsewhere, e.g. JOBHUNT_FONT="DejaVu Sans".
set -euo pipefail

DIR="${1:?usage: render.sh <packet-dir> [latex-header.tex]}"
TEX="${2:-}"
[ -d "$DIR" ] || { echo "no such directory: $DIR" >&2; exit 1; }

# Find the workspace root by walking up looking for resume/compact.tex.
ROOT=""
P="$(cd "$DIR" && pwd)"
while [ "$P" != "/" ]; do
  [ -f "$P/resume/compact.tex" ] && ROOT="$P" && break
  P="$(dirname "$P")"
done

# A resume and a cover letter want opposite typography. compact.tex crushes
# parskip to 1.5pt so two pages of bullets fit; run a letter through it and the
# paragraphs fuse into one block. Pick per file, not per packet.
RESUME_TEX="$TEX"; LETTER_TEX=""
if [ -z "$RESUME_TEX" ] && [ -n "$ROOT" ]; then
  RESUME_TEX="$ROOT/resume/compact.tex"
  [ -f "$ROOT/cover-letters/letter.tex" ] && LETTER_TEX="$ROOT/cover-letters/letter.tex"
fi

SCRIPTS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

pages() {
  # Read the PDF directly. mdls only answers for Spotlight-indexed paths, so it
  # returns "(null)" in /tmp and on files written seconds ago.
  local n
  n="$(python3 "$SCRIPTS/pdf_pages.py" "$1" 2>/dev/null)"
  [ -n "$n" ] && [ "$n" != "?" ] && { echo "$n"; return; }
  mdimport -r "$1" 2>/dev/null || true
  sleep 2
  n="$(mdls -raw -name kMDItemNumberOfPages "$1" 2>/dev/null)"
  [ -n "$n" ] && [ "$n" != "(null)" ] && { echo "$n"; return; }
  echo "?"
}

shopt -s nullglob
for f in "$DIR"/*.md; do
  base="$(basename "$f" .md)"
  case "$base" in
    JOB|Interview_Prep*|Test_Interview*) continue ;;   # internal, never rendered
  esac
  out="${f%.md}"

  case "$base" in
    *CoverLetter*) USE_TEX="$LETTER_TEX"; MARGIN=0.9in; FSIZE=11pt ;;
    *)             USE_TEX="$RESUME_TEX"; MARGIN=0.5in; FSIZE=10pt ;;
  esac
  TEXARG=(); [ -n "$USE_TEX" ] && [ -f "$USE_TEX" ] && TEXARG=(-H "$USE_TEX")

  pandoc "$f" -o "$out.docx" --standalone 2>/dev/null
  # Do not swallow xelatex failures. A silently stale PDF is worse than a loud one.
  if ! err="$(pandoc "$f" -o "$out.pdf" --pdf-engine=xelatex "${TEXARG[@]}" \
      -V geometry:margin=$MARGIN -V fontsize=$FSIZE -V mainfont="${JOBHUNT_FONT:-Helvetica Neue}" 2>&1)"; then
    printf "  %-26s PDF RENDER FAILED\n" "$base"
    echo "$err" | tail -5 | sed 's/^/      /'
    continue
  fi
  n="$(pages "$out.pdf")"
  want=""
  case "$base" in
    *Resume*)      want=2 ;;
    *CoverLetter*) want=1 ;;
  esac
  flag=""
  if [ -n "$want" ] && [ "$n" != "?" ] && [ "$n" != "$want" ]; then
    flag="  <-- expected $want, TRIM IT"
  fi
  printf "  %-26s %s page(s)%s\n" "$base" "$n" "$flag"
  # surface unfilled [TOKEN] placeholders
  grep -o '\[[A-Z_]\{3,\}\]' "$f" 2>/dev/null | sort -u | sed 's/^/      UNFILLED: /' || true
done

# JOB.md is for the candidate only. Never let a rendered copy survive.
removed=0
for junk in "$DIR"/JOB.pdf "$DIR"/JOB.docx; do
  [ -f "$junk" ] && rm -f "$junk" && removed=1
done
[ "$removed" = 1 ] && echo "  removed rendered JOB.* (internal notes, not for employers)"
exit 0
