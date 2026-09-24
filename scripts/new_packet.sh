#!/bin/bash
# Scaffold one application packet folder with the three files it always has.
#
# Naming convention is "<Title> - <Company> - <City>". Keep it, because
# /job-status, /update-sheet and the tracker all locate packets by matching
# the company segment.
#
# Usage:
#   new_packet.sh <applications-dir> "<Title>" "<Company>" "<City>" [file-prefix]
#
# file-prefix is the candidate surname (config: candidate.file_prefix).
# Falls back to $JOBHUNT_PREFIX, then "Candidate".
set -euo pipefail

APPS="${1:?usage: new_packet.sh <applications-dir> <title> <company> <city>}"
TITLE="${2:?missing title}"
COMPANY="${3:?missing company}"
CITY="${4:?missing city}"
PREFIX="${5:-${JOBHUNT_PREFIX:-Candidate}}"

# Strip characters that break directory names or shell globs.
san() { printf '%s' "$1" | tr '/' '-' | tr -d ':*?"<>|'; }
DIR="$APPS/$(san "$TITLE") - $(san "$COMPANY") - $(san "$CITY")"

if [ -d "$DIR" ]; then
  echo "already exists: $DIR"
  exit 0
fi
mkdir -p "$DIR"

cat > "$DIR/JOB.md" <<EOF
# $TITLE — $COMPANY

**Listing:** <URL>
**Apply at:** <portal or email>

| | |
|---|---|
| **Company** | $COMPANY |
| **Location** | $CITY |
| **Pay** | |
| **Posted** | |
| **Deadline** | |
| **Resume base** | |
| **Interview odds** | **~XX%** |

## Why it fits

## Watch

## Requirements

## Key duties
EOF

: > "$DIR/${PREFIX}_Resume.md"
: > "$DIR/${PREFIX}_CoverLetter.md"

echo "$DIR"
