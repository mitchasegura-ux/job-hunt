# Tracker schema

`tracker.py` owns the file. Do not hand-write openpyxl code.

## Shape

Sheet `Applications`, nine columns: Job Title, Company, City, Pay, Status,
Date Posted, Date Applied, Deadline, Notes. Status is a dropdown restricted to
Not Applied, Applied, Interview, Rejected, Accepted, Passed Up, applied down to
row 200 so new rows inherit it. Each status has a fill color. Sheet `Summary`
holds COUNTIF formulas per status plus a total.

Dates are ISO `YYYY-MM-DD` only. `tracker.py migrate` adds the three date
columns to an older six-column tracker. `tracker.py sweep-deadlines` moves Not
Applied rows whose deadline has passed to Passed Up.

Notes carry everything the columns cannot: how a status was verified, deadlines,
what to ask on the call, known gaps, and action flags.

## Two failure modes

**Excel holding the file open silently discards writes.** openpyxl saves
successfully, then Excel's own save clobbers it, and the rows vanish with no
error anywhere. `tracker.py` refuses to write while Excel is running. If a user
reports missing rows, this is why.

**Apple Events to Excel can be blocked** with `-1743 Not authorized`, and it
fails quietly. So `report` computes counts in Python from cell values rather
than driving Excel to recalculate. The COUNTIF formulas stay in the file for the
human and populate when they open it. Never claim the sheet was recalculated
unless cached values actually came back non-empty.

## Gmail sweep

Search the last 5-7 days. Useful query shape:

```
(application OR applying OR interview OR offer OR "unfortunately" OR
 "not selected" OR "moving forward" OR "other candidates" OR received OR
 "next steps" OR schedule) newer_than:7d
```

Classify by sender and subject:

| Signal | Status |
|---|---|
| ATS receipt (Workday, Lever, Rippling, iCIMS, CareerPlug, BrightMove, Workable, AppliTrack) | Applied |
| "Thank you for your interest ... we have decided", "not selected" | Rejected |
| "Schedule your interview", calendar invite | Interview |
| Offer letter | Accepted |
| "Application Started" without submission | still Not Applied, flag it |

Read the actual message before classifying. "Thank you for your interest in the
X position. We sincerely appreciate the time you invested" is a rejection, and
the subject line will not say so.

## Two things to always surface

**Employer messages sent through a job board.** A notification saying "New
Message from <employer>" is non-repliable and the content lives only inside the
platform. Flag it with the date as action-needed. These sit unread for days and
employers read response time as interest.

**Absence of a receipt proves nothing.** Municipal and university portals
frequently send none. Ask the candidate before marking anything Not Applied.
