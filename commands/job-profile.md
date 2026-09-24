---
description: Build master profile, claims boundary, base resumes, and voice rules
argument-hint: '[materials dir]'
---

# /job-profile - Build the candidate profile from their materials

Invoke the `job-hunting` skill and follow its **Build the profile** section. Read
`references/voice-rules.md`.

`$ARGUMENTS` may point at a folder of existing materials.

Ask for a current resume, any past cover letters, and what they are looking for.

Produce three things:

1. **`resume/MASTER.md`** - every truthfully claimable bullet, tagged by track,
   ending in a **claims boundary**. Build the boundary by asking uncomfortable
   questions directly: did you have direct reports, did you configure that or
   only use it, what exactly was your scope. Do this once, properly. Everything
   downstream depends on it, and a boundary nobody interrogated is not a
   boundary.

2. **`resume/base/*.md`** - one filtered resume per career track.

3. **`cover-letters/TEMPLATE.md`** - voice rules **measured** from their real
   letters. Count average word length and em-dash usage before writing anything.
   Pull their actual openers and closers verbatim. Write the measured numbers
   into the config so `check_letter.py` enforces their baseline rather than a
   generic one.
