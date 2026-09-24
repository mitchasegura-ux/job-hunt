---
name: job-hunting
description: Run a full job search operation - find and screen live postings, build tailored application packets (resume + cover letter + job notes) in the candidate's own voice, track everything in an Excel sheet, sweep Gmail for status changes, and prepare interview materials. Make sure to use this skill whenever the user mentions job searching, job postings, applying to jobs, tailoring a resume or CV, writing a cover letter, an application tracker or spreadsheet of applications, checking whether they heard back from an employer, preparing for a phone screen or interview, answering an application's free-text questions, following up on an application that went quiet, or asks "find me some jobs" / "build me a packet" / "did anyone get back to me" / "help me prep for this interview" - even if they do not name this skill or type a slash command.
---

# Job Hunt

A complete job-search operation: source, screen, write, track, prep.

The value here is not that it can write a cover letter. It is that it writes in
**this candidate's** voice, refuses to claim things they cannot back up, screens
against **their** real constraints, and remembers what was already learned about
the market so each session does not start over.

## Routing

Read the argument and go to the matching section. With no argument, ask which.

| Command | Section |
|---|---|
| `/job-hunt` | [Search and build](#search-and-build) |
| `/interview-prep` | [Interview prep](#interview-prep) |
| `/update-sheet` | [Update the tracker](#update-the-tracker) |
| `/job-status` | [Status](#status) |
| `/job-answer` | [Answer one question](#answer-one-application-question) |
| `/job-followup` | [Follow up](#follow-up) |
| `/job-init` | [Initialize a workspace](#initialize-a-workspace) |
| `/job-profile` | [Build the profile](#build-the-profile) |

## First, load the config

Every command needs it. Look for `jobsearch.config.yml` at the workspace root.
If it is missing, run [`/job-init`](#initialize-a-workspace) first.

It tells you where the candidate's master profile, base resumes, voice
template, applications folder, and tracker live, plus their pay floor and
schedule constraints. Nothing about paths is hardcoded, so this works for
whoever is running it.

## Tools

`$SKILL_DIR` means the folder this `SKILL.md` lives in, wherever it was
installed (`~/.claude/skills/job-hunting`, `~/.codex/skills/job-hunting`, a repo
checkout, etc.). Installed as a Claude Code plugin, it is `${CLAUDE_PLUGIN_ROOT}`.
Resolve it once per session and reuse it.

`scripts/ensure_venv.sh` prints a python path with openpyxl available. Every
script needs it, because system python fails under PEP 668.

```bash
SKILL_DIR=~/.claude/skills/job-hunting   # adjust to the actual install path
PY=$(bash $SKILL_DIR/scripts/ensure_venv.sh)
```

Slash commands (`/job-hunt`, `/job-status`, ...) are shortcuts. In an agent
without them, the user can say the command name in plain words ("run
job-status") and you route it the same way.

| Script | Does |
|---|---|
| `tracker.py` | `init` / `add` / `set-status` / `note` / `dates` / `edit` / `migrate` / `sweep-deadlines` / `report` on the xlsx |
| `check_letter.py` | Validates a letter before it ships. Run it every time. |
| `render.sh` | Renders a packet to docx/pdf, checks page counts, deletes rendered `JOB.*` |
| `new_packet.sh` | Scaffolds a packet folder: `<apps-dir> "<Title>" "<Company>" "<City>" <file_prefix>` |
| `pdf_pages.py` | Page count without Spotlight |

---

## Search and build

Read `references/search-method.md` before the first search of a session. It
holds the query matrix, odds calibration, and the sourcing traps.

1. **Screen against the config first.** Pay floor and schedule are hard filters.
   A posted *range* whose bottom breaches the floor still gets flagged, not
   silently accepted.
2. **Search** with the job-search connector across the configured tracks and
   locations. Do not scrape job boards directly.
3. **Pull full details** on anything that looks viable. Titles lie.
4. **Report before building.** Give the candidate the shortlist with odds and
   the disqualifications, and let them decline. Building a packet nobody wanted
   wastes their time reviewing it.
5. **Build packets** for what survives. See `references/packet-anatomy.md`.
6. **Validate, render, track.**

```bash
$PY $SKILL_DIR/scripts/check_letter.py "<dir>/<Prefix>_CoverLetter.md" --target <cfg> --boundary <cfg>
bash $SKILL_DIR/scripts/render.sh "<dir>"
$PY $SKILL_DIR/scripts/tracker.py add <tracker> --title ... --company ... --city ... --pay ...
```

7. **Open the listings** so they can apply: `open <url>` for each.

## Update the tracker

Sweep Gmail, classify, write back. Details in `references/tracker-schema.md`.

Search the last 5-7 days for application confirmations, rejections, interview
invitations, and employer messages. Then for each match:

```bash
$PY $SKILL_DIR/scripts/tracker.py set-status <tracker> --company "X" --status Applied --notes "Confirmed <date>: <ATS> receipt"
```

Two things that matter:

- **Employer messages sent through a job board are invisible until read.** An
  Indeed "New Message from <employer>" notification is non-repliable and the
  content only exists inside the platform. Flag it as action-needed with the
  date, because these sit unread for days and employers read response time as
  interest.
- **A confirmation email proves submission; its absence proves nothing.**
  Municipal and university portals frequently send no receipt. Ask before
  marking something Not Applied.

Report what changed, then say plainly what did not change. "No rejections" is
information the candidate wants.

## Status

```bash
$PY $SKILL_DIR/scripts/tracker.py report <tracker>
```

Then add what the sheet cannot: which deadlines are close, which packets are
built but unsent, which applications have gone quiet past two weeks, and what
the single next action is. Lead with anything time-boxed.

## Interview prep

Read `references/interview-materials.md`. This produces **two** artifacts, and
getting the interviewer's identity right matters more than anything else.

Before writing, establish **who is actually calling**. An outsourced recruiter
running a 30-minute screen and a hiring manager running a technical round need
completely different question sets. Conflating them produces a mock interview
that rehearses the wrong conversation. If the invitation names a person or firm,
look at what they are: an HR agency cannot evaluate a VLAN definition; a small
company's owner absolutely can and will.

1. `Interview_Prep.md` - a prompt file the candidate pastes into a voice-mode
   assistant to run a realistic mock. It must instruct the interviewer to score
   every answer, interrupt at 90 seconds, stay in character, and end with a
   verdict.
2. `Interview_Reference_Card.md` - two printed pages they keep in front of them
   during the call. Scripted opening sentences, short clauses after.

Both go in the packet folder. Neither renders through `render.sh`.

## Answer one application question

Free-text application boxes ("Why are you a good fit?", "Describe your
experience with X"). Answer the specific question asked, at roughly a third the
length of a cover letter, against that posting's stated criteria rather than as
a career summary. Same voice rules apply: run `check_letter.py` on it.

Give a character count, since these boxes often have limits.

## Follow up

Find applications older than the threshold with no employer response, and draft
a short follow-up in the candidate's voice. Keep it to four or five sentences:
reference the role and when you applied, add one concrete new thing if there is
one (a certification, a relevant project), reiterate interest, close.

Never send anything. Draft it, show it, let them send it.

## Initialize a workspace

Create the shape below and write `jobsearch.config.yml` (template:
`jobsearch.config.example.yml` in this folder). If the user already has
materials in a different layout, point the config at what exists rather than
moving their files.

Include the `formatting:` block: font, font sizes, and margins for resumes and
letters. `render.sh` reads it. Confirm the font renders
(`printf x | pandoc -o /tmp/fonttest.pdf --pdf-engine=xelatex -V mainfont="<font>"`) before saving it.

```
workspace/
├── jobsearch.config.yml
├── Applications/          one folder per job
├── resume/
│   ├── MASTER.md          source of truth, never sent
│   ├── base/              filtered variants per track
│   └── compact.tex        latex header for rendering
├── cover-letters/
│   └── TEMPLATE.md        voice rules, derived from their real letters
└── <tracker>.xlsx
```

```bash
$PY $SKILL_DIR/scripts/tracker.py init <tracker>.xlsx
```

Then run [`/job-profile`](#build-the-profile) to populate the profile.

## Build the profile

Turn the candidate's raw materials into the three files everything else depends
on. Ask for: a current resume, any past cover letters, and a description of what
they are looking for.

**`resume/MASTER.md`** - every bullet they can truthfully claim, tagged by
track. Never sent anywhere. Ends with a **claims boundary**: an explicit list of
things they must never assert. Get these by asking directly. "Your resume says
you led a team, did you have direct reports?" The boundary is what keeps a
tailored resume from drifting into fabrication, and it only exists if someone
asks the uncomfortable questions once.

**`resume/base/*.md`** - one filtered resume per career track.

**`cover-letters/TEMPLATE.md`** - voice rules **measured from their own
letters**, not assumed. Read `references/voice-rules.md` for the method. Count
their average word length and their em-dash usage before writing a single
letter. Write the measured numbers into the config.

---

## Rules that apply everywhere

**Never claim what the profile cannot support.** The claims boundary is not a
style preference. A tailored resume that inflates scope gets caught in an
interview, and the candidate is the one sitting there.

**State odds before building, not after.** An honest 40% with the blocker named
is more useful than an optimistic packet. Say what would disqualify them and let
them decide.

**Flag the thing they will not think to ask.** A range whose floor breaches
theirs. A "part-time" tag contradicting the posting body. Benefits listed as PTO
only. A hard requirement stated twice. These decide outcomes and are easy to
miss while reading for fit.

**`JOB.md` is internal.** It holds odds estimates and candid warnings. It never
renders to PDF and never sits next to files the candidate uploads.

**Report failures plainly.** If a search got rate-limited, a script failed, or
an automation silently did nothing, say so. A confident summary of work that did
not happen is worse than no summary.
