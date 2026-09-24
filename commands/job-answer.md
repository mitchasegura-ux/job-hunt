---
description: Answer one free-text application question in your voice
argument-hint: '<question> [company] [char limit]'
---

# /job-answer - Answer one free-text application question

Invoke the `job-hunting` skill and follow its **Answer one application question**
section.

`$ARGUMENTS` is the question, optionally with the company name.

Answer the question actually asked, not a career summary. Roughly a third the
length of a cover letter. Argue against that posting's stated criteria, using
its own language where it fits.

Same voice rules as any letter: no em-dashes, no bold, no meta-commentary, and
nothing outside the claims boundary. Validate with `check_letter.py` before
handing it over.

Report the word and character count, since these boxes often have limits. If
there is a known limit, offer a shorter variant.
