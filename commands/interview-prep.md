---
description: Build a mock-interview prompt and 2-page reference card
argument-hint: '<company or role>'
---

# /interview-prep - Build mock interview and reference card

Invoke the `job-hunting` skill and follow its **Interview prep** section. Read
`references/interview-materials.md` in full.

`$ARGUMENTS` names the company or role. Find the matching packet folder under
the applications directory.

Before writing anything, establish who is actually conducting the interview.
Check the invitation email if it is available: an outsourced HR firm running a
30-minute screen and a hiring manager running a technical round need completely
different question sets. Getting this wrong produces a mock that rehearses the
wrong conversation.

Produce both artifacts in the packet folder:
- `Interview_Prep.md` - the mock interviewer prompt
- `Interview_Reference_Card.md` plus a rendered 2-page PDF

Neither goes through `render.sh`; render the card directly with pandoc.
