#!/usr/bin/env python3
"""Validate a cover letter before it ships.

Every rule here exists because a draft violated it and a human caught it.

  em-dash           the loudest AI tell. Check the candidate's own letters:
                    if they have zero across dozens, any occurrence is wrong.
  length            match the candidate's measured average, not a generic
                    target. Drafts run ~35% long by default.
  bold in body      real cover letters do not bold phrases mid-paragraph.
  meta-commentary   "I want to be straight about one thing" narrates your own
                    honesty. Candidates almost never do this; models love it.
  claims boundary   role-specific things the candidate must never assert.
                    Supplied via --boundary as a file of regex patterns.

Usage
  check_letter.py LETTER.md [--max-words 500] [--target 406]
                            [--boundary path/to/claims_boundary.txt]
                            [--strict]

Exit code 0 = clean, 1 = at least one hard failure.
--strict also fails on soft warnings (length drift).
"""
import argparse, re, sys, unicodedata

BANNED_PHRASES = [
    r"I want to be (straight|clear|precise|accurate|honest)",
    r"I(?:'| a)m going to be (straight|honest|blunt)",
    r"\bto be (perfectly |completely )?(clear|honest|frank)\b",
    r"Two (notes|things) (for accuracy|I want to answer)",
    r"I would rather (name|say) that plainly",
    r"\bI'll take you at your word\b",
    r"\bgenuinely\b", r"\bsquarely\b", r"\bprecisely\b", r"\boutright\b",
    r"\bcandidly\b", r"\bcrucially\b", r"\bmeaningfully\b",
]

# Structural tells: "not X, but Y" and colon-then-list rhetorical rhythm.
SOFT_PATTERNS = [
    (r"\bnot (just |merely |simply )?[a-z ]+, but\b", "not-X-but-Y construction"),
    (r"\bThat is (not )?the whole\b", "rhetorical flourish"),
    (r"\bwhich is (exactly )?why\b", "explainer connective"),
]


def strip_header(text):
    """Drop the address block so word count measures the letter body."""
    m = re.search(r"^Dear\b", text, re.M)
    return text[m.start():] if m else text


def boundary_patterns(path):
    """Forbidden phrases from a claims-boundary file.

    The file may be a plain list of regexes, or a markdown MASTER.md whose
    boundary lives under a "CLAIMS BOUNDARY" heading. Feeding markdown prose
    straight to re.finditer used to crash on the first "**Name:**" bullet, which
    silently took the whole check offline. Inside the markdown section the real
    signal is the quoted forbidden wording, so pull that out and escape it.
    """
    text = open(path, encoding="utf-8").read()
    if "CLAIMS BOUNDARY" in text:
        section = text.split("CLAIMS BOUNDARY", 1)[1]
        seen = []
        for phrase in re.findall(r'"([^"]{3,60})"', section):
            phrase = phrase.strip().strip(".,;:")
            if len(phrase) >= 4 and phrase not in seen:
                seen.append(phrase)
        return [r"\b" + re.escape(p) + r"\b" for p in seen]

    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            re.compile(line)
        except re.error:
            print(f"  WARN  boundary line is not a valid regex, skipped: {line[:60]}")
            continue
        out.append(line)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("letter")
    ap.add_argument("--max-words", type=int, default=500)
    ap.add_argument("--target", type=int, default=None,
                    help="candidate's measured average; warns at +25%%")
    ap.add_argument("--boundary", default=None,
                    help="file of regex patterns the letter must not match")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()

    raw = open(a.letter, encoding="utf-8").read()
    body = strip_header(raw)
    words = len(body.split())

    hard, soft = [], []

    # 1. em-dashes and en-dashes in prose
    for ch, name in (("—", "em-dash"), ("–", "en-dash")):
        n = raw.count(ch)
        if n:
            lines = [i for i, l in enumerate(raw.splitlines(), 1) if ch in l]
            hard.append(f"{n} {name}(s) on line(s) {lines[:8]}")

    # 2. length
    if words > a.max_words:
        hard.append(f"{words} words, ceiling is {a.max_words}")
    elif a.target and words > a.target * 1.25:
        soft.append(f"{words} words vs target {a.target} (+{words/a.target-1:.0%})")

    # 3. bold inside the body
    bold = re.findall(r"\*\*[^*\n]+\*\*", body)
    if bold:
        hard.append(f"{len(bold)} bold span(s) in body: {bold[:3]}")

    # 4. banned meta-commentary and filler
    for pat in BANNED_PHRASES:
        for m in re.finditer(pat, body, re.I):
            hard.append(f"banned phrase: \"{m.group(0)}\"")

    # 5. soft structural tells
    for pat, label in SOFT_PATTERNS:
        if re.search(pat, body, re.I):
            soft.append(label)

    # 6. claims boundary
    #
    # A pattern can legitimately appear inside a disclaimer: "I have not
    # operated a SIEM" is the candidate respecting the boundary, not crossing
    # it. Look backwards a short distance for a negation before failing, and
    # downgrade to a warning when one is present so a human still eyeballs it.
    NEG = re.compile(r"\b(not|never|no|haven'?t|hasn'?t|don'?t|without|lack)\b", re.I)
    if a.boundary:
        for pat in boundary_patterns(a.boundary):
            for m in re.finditer(pat, body, re.I):
                window = body[max(0, m.start() - 90):m.start()]
                quote = body[max(0, m.start() - 60):m.end() + 20].replace("\n", " ")
                if NEG.search(window):
                    soft.append(f"boundary term \"{m.group(0)}\" appears negated, verify: ...{quote}...")
                else:
                    hard.append(f"CLAIMS BOUNDARY: /{pat}/ -> ...{quote}...")

    # 7. smart quotes, which betray a copy-paste round trip
    if any(unicodedata.name(c, "").startswith(("LEFT DOUBLE", "RIGHT DOUBLE"))
           for c in raw):
        soft.append("curly quotes present; plain quotes survive ATS better")

    print(f"{a.letter}\n  words: {words}" + (f"  (target {a.target})" if a.target else ""))
    for h in hard:
        print(f"  FAIL  {h}")
    for s in soft:
        print(f"  warn  {s}")
    if not hard and not soft:
        print("  clean")

    if hard or (a.strict and soft):
        sys.exit(1)


if __name__ == "__main__":
    main()
