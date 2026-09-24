# Voice rules

## Measure before you write

Do not assume a target length or style. Read the candidate's own past cover
letters and count.

```bash
# word counts across their real letters, and em-dash usage
for f in CVs/*.pdf; do ... extract text ... ; done
```

For one candidate, 38 real letters averaged **406 words** with **zero
em-dashes**. The first 22 drafts written for them averaged **560 words** with
**61 em-dashes**. Neither number was guessable. Both went into the config.

Write the measured average and the ceiling into `jobsearch.config.yml` so every
future letter is checked against their real baseline.

## The tells

These are what make a letter read as generated. Most were found by comparing
drafts against a candidate's real writing.

**Em-dashes.** Usually the loudest single signal. If a candidate has never used
one across dozens of letters, any occurrence is wrong. Use a comma, a period, or
a colon. A sentence that needs an em-dash to hold together is two sentences.

**Bold inside the body.** Real letters do not bold phrases mid-paragraph. No
bolded requirement headers, no bolded key terms.

**Meta-commentary about your own honesty.** The worst offender, and the hardest
to notice while writing. Delete every instance of:

- "I want to be straight about one thing"
- "Two notes for accuracy"
- "I want to be precise, because I think precision matters here"
- "I would rather name that plainly than let it be a surprise"

Candidates almost never narrate their own candor. Models do it constantly. If
there is a real gap, address it in one clause inside a paragraph doing other
work, or leave it off. Never give a gap its own confessional paragraph.

**Structural tics.** "Not X, but Y" constructions. Rhetorical triads where a
real list would do. Colon-then-elaboration as a rhythm device. Sentences that
begin "What I bring is".

**Vocabulary.** genuinely, precisely, squarely, outright, candidly, notably,
crucially, meaningfully, "the shape of", "reads like", "lands".

## What good looks like

Pull the candidate's actual openers and closers verbatim from their old letters
and reuse them. They will have two or three they favor.

Their real voice usually includes things a model would smooth away: a slightly
long flowing sentence joined with commas, gear named specifically instead of
described generically, warmth about a place, and exactly one moment of humor or
self-awareness. Keep those.

Specificity substitutes for adjectives. "UniFi and Cisco gear" beats "network
hardware". "Proxmox, Docker, and Ubuntu Server" beats "virtualization
experience".

## Enforce it

```bash
check_letter.py <letter> --target <their-average> --boundary <boundary-file>
```

Run it on every letter before rendering. It catches what re-reading does not,
including violations in letters you were confident about.
