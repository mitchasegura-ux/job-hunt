# Packet anatomy

One folder per application: `Applications/<Title> - <Company> - <City>/`

Keep that naming. The tracker and status commands locate packets by the company
segment.

```
JOB.md                    listing details, odds, warnings   INTERNAL ONLY
<Prefix>_Resume.md/.docx/.pdf
<Prefix>_CoverLetter.md/.docx/.pdf
Interview_Prep.md         added later if they get an interview
Interview_Reference_Card.md/.pdf
```

Filenames use the candidate's surname. Employers receive a folder of
`Resume.pdf` files from everyone; a named file is easier to keep.

## JOB.md

Written for the candidate, never for the employer. It carries the odds estimate
and the candid warnings, so it must never be rendered to PDF and never sit in
the folder as anything but markdown. `render.sh` deletes rendered copies.

Structure:

- A header table: company, location, pay, posted, deadline, resume base used, odds
- **Why it fits** - map their requirements to the candidate's actual experience.
  A two-column table works well when the alignment is strong.
- **Watch** - what could sink it, what to ask about, what is unusual. Schedule
  conflicts, thin benefits, hard requirements, weird application mechanics.
- **Requirements** and **Key duties**, quoted closely enough to write against.

Quote the posting's own distinctive language. "This is not primarily a help desk
role" is the sentence the cover letter should answer.

## Resume

Start from the base resume for the matching track. Then:

1. **Rewrite the summary** to mirror the posting's title and top requirements.
   Highest-value edit available.
2. **Reorder skill categories** so their top three requirements are the first
   three lines.
3. **Swap in their exact phrasing.** If they say "endpoint management" and the
   resume says "device management", change it. Exact match beats synonym.
4. **Reorder or trim experience.** Cut the weakest bullets to hold two pages.
5. **Pull extra bullets from MASTER.md** if needed. Never invent one.

Two pages. Verify with `render.sh`, and trim if it runs to three: condense skill
blocks first, then drop the least relevant experience entry, then drop a project.

## Cover letter

See `voice-rules.md`. One page, matching their measured average length.

Structure that works: hook and what the work is for, technical proof with named
tools, the bridge connecting two halves of their background, a pressure story,
why this specific place, close.

The "why here" paragraph is the only one that must be written from scratch every
time. It is also the one that decides whether the letter sounds like a person.

## Before shipping

```bash
check_letter.py <letter> --target <avg> --boundary <boundary-file>
render.sh <packet-dir>
```

Resume 2 pages, letter 1 page, no rendered `JOB.*`, no unfilled `[TOKENS]`.
