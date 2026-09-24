---
description: Sweep Gmail and update the application tracker
argument-hint: '[window, e.g. "last 14 days"]'
---

# /update-sheet - Sweep Gmail and update the tracker

Invoke the `job-hunting` skill and follow its **Update the tracker** section. Read
`references/tracker-schema.md` for classification rules.

`$ARGUMENTS` may set the window, for example `last 3 days`. Default is 7 days.

Steps:
1. Search Gmail for application receipts, rejections, interview invitations, and
   employer messages.
2. Read anything ambiguous before classifying. Rejection subject lines rarely
   say "rejection".
3. Update via `tracker.py set-status`, one call per change.
4. Report what changed, and state plainly what did not. "No rejections this
   week" is information worth giving.

Flag any employer message sent through a job board as action-needed with its
date, since those are invisible until the candidate logs in.
