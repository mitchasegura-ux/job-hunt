# Instructions for non-Claude agents (Codex, Cursor, Gemini CLI, Aider, etc.)

This folder is an Agent Skill. The real instructions live in `SKILL.md`. This
file covers the differences when the agent running it is not Claude Code.

## Load order

1. Read `SKILL.md` in full. It is the router and holds the rules that apply
   everywhere.
2. Read a file under `references/` only when `SKILL.md` or a command says to.
3. `commands/*.md` are the slash-command entry points. If your agent has no
   slash commands, treat the user saying "job-hunt", "job-status", etc. as the
   same request and follow that command file.

## Paths

`SKILL.md` refers to `$SKILL_DIR`: the directory containing this file. Resolve
it to an absolute path before running any script. Nothing is hardcoded to
`~/.claude`.

Workspace paths (resumes, tracker, applications folder) come from
`jobsearch.config.yml` at the user's workspace root, never from this folder.

## Capabilities the skill assumes, and fallbacks

| Assumed | If your agent lacks it |
|---|---|
| Shell access to run `scripts/` | Ask the user to run the command and paste the output. Do not hand-write openpyxl code against the tracker. |
| A job-search connector/tool | Search employer career portals directly. Do not scrape Indeed, LinkedIn, or other aggregators; they rate-limit and CAPTCHA-block quickly. |
| Gmail access (for `/update-sheet`) | Ask the user to paste or forward the relevant emails, then classify with `references/tracker-schema.md`. |
| `open <url>` (macOS) | Print the URLs as a list instead. |

## Hard rules, regardless of agent

- Never send an email, submit an application, or message an employer. Draft
  only; the candidate sends.
- Never claim anything outside the claims boundary in `resume/MASTER.md`.
- Run `scripts/check_letter.py` on every cover letter and application answer
  before showing it as final.
- `JOB.md` files are internal notes and must never be rendered or attached.

## System requirements

- Python 3.9+ (`ensure_venv.sh` creates a local `.venv` with openpyxl)
- `pandoc` and `xelatex` for `render.sh`. On Linux or Windows set
  `JOBHUNT_FONT` to an installed font, since the default is macOS's Helvetica
  Neue.
- `tracker.py` refuses to write while Microsoft Excel is running (macOS check
  via `pgrep`; a no-op elsewhere). Close the tracker in any spreadsheet app
  before writing.
