#!/usr/bin/env python3
"""Application tracker: owns the .xlsx so the model never rewrites openpyxl code.

Commands
  init        <xlsx>                                  create an empty tracker
  add         <xlsx> --title --company --city --pay [--status] [--notes]
  set-status  <xlsx> --company <name> --status <s> [--notes] [--title <t>]
  note        <xlsx> --company <name> --append <text>
  dates       <xlsx> --company <name> [--posted|--applied|--deadline YYYY-MM-DD]
  edit        <xlsx> --company <name> [--set-title|--set-company|--city|--pay]
  migrate     <xlsx>                                  add the three date columns
  sweep-deadlines <xlsx> [--today YYYY-MM-DD]         Not Applied + past due -> Passed Up
  report      <xlsx> [--json]                         counts + deadlines + stale

Two failure modes this guards against, both observed in the wild:

1. Excel holding the file open silently discards writes. openpyxl saves fine,
   then Excel's own save clobbers it and the rows vanish with no error. Any
   mutating command refuses to run while Excel is open.

2. Driving Excel via osascript to recalculate can be blocked by macOS
   ("-1743 Not authorized to send Apple events"), and it fails quietly. So
   `report` computes every count in Python from cell values. The COUNTIF
   formulas stay in the file for the human; their cached values populate the
   moment the user opens it. Never claim the sheet was "recalculated" unless
   you actually verified cached values came back non-None.
"""
import argparse, datetime, json, os, subprocess, sys
from collections import Counter

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

HEADERS = ["Job Title", "Company", "City", "Pay", "Status",
           "Date Posted", "Date Applied", "Deadline", "Notes"]
STATUSES = ["Not Applied", "Applied", "Interview", "Rejected", "Accepted", "Passed Up"]
FILL = {
    "Not Applied": "F2F2F2",
    "Applied": "DDEBF7",
    "Interview": "FFF2CC",
    "Rejected": "FCE4E4",
    "Accepted": "E2EFDA",
    "Passed Up": "E4E0EC",
}
POSTED_COL, APPLIED_COL, DEADLINE_COL, NOTES_COL = 6, 7, 8, 9
DATE_COLS = (POSTED_COL, APPLIED_COL, DEADLINE_COL)
DATE_FMT = "yyyy-mm-dd"
WIDTHS = {"A": 46, "B": 34, "C": 22, "D": 30, "E": 14,
          "F": 13, "G": 13, "H": 13, "I": 62}
THIN = Side(style="thin", color="D0D0D0")
BORDER = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
DV_LAST_ROW = 200


def excel_is_running():
    try:
        out = subprocess.run(["pgrep", "-x", "Microsoft Excel"],
                             capture_output=True, text=True, timeout=5)
        return out.returncode == 0
    except Exception:
        return False


def guard_excel():
    if excel_is_running():
        sys.exit(
            "REFUSING TO WRITE: Microsoft Excel is running.\n"
            "Excel holds the file open and its next save silently discards\n"
            "anything written underneath it. Quit Excel, then re-run.\n"
            "  osascript -e 'tell application \"Microsoft Excel\" to quit saving no'"
        )


def parse_date(v):
    """ISO only. Refusing fuzzy formats keeps 'Sept 8' from landing in the wrong year."""
    if v in (None, "", "-"):
        return None
    if isinstance(v, datetime.datetime):
        return v.date()
    if isinstance(v, datetime.date):
        return v
    try:
        return datetime.date.fromisoformat(str(v).strip())
    except ValueError:
        sys.exit(f"bad date {v!r}: use YYYY-MM-DD")


def set_date(ws, row, col, value):
    c = ws.cell(row, col)
    c.value = parse_date(value)
    c.number_format = DATE_FMT
    style_cell(c, col)


def style_cell(cell, col_idx, wrap_cols=(1, NOTES_COL)):
    cell.font = Font(name="Arial", size=10)
    cell.alignment = Alignment(vertical="top", wrap_text=(col_idx in wrap_cols))
    cell.border = BORDER


def apply_status(ws, row, status):
    c = ws.cell(row, 5)
    c.value = status
    c.fill = PatternFill("solid", fgColor=FILL.get(status, FILL["Not Applied"]))
    c.font = Font(name="Arial", size=10, bold=True)


def build_summary(wb):
    s = wb["Summary"] if "Summary" in wb.sheetnames else wb.create_sheet("Summary")
    s["A1"] = "Application Status Summary"
    s["A1"].font = Font(name="Arial", bold=True, size=14)
    s["A2"] = "Counts update automatically as you change the Status column."
    s["A2"].font = Font(name="Arial", size=10, italic=True, color="808080")
    s["A4"], s["B4"] = "Status", "Count"
    for c in ("A4", "B4"):
        s[c].font = Font(name="Arial", bold=True, size=11, color="FFFFFF")
        s[c].fill = PatternFill("solid", fgColor="1F3864")
    for i, st in enumerate(STATUSES, start=5):
        s[f"A{i}"] = st
        s[f"A{i}"].font = Font(name="Arial", size=10)
        s[f"A{i}"].fill = PatternFill("solid", fgColor=FILL[st])
        s[f"B{i}"] = f'=COUNTIF(Applications!$E$2:$E${DV_LAST_ROW},A{i})'
        s[f"B{i}"].font = Font(name="Arial", size=10)
    total = 5 + len(STATUSES)
    s[f"A{total}"] = "Total tracked"
    s[f"A{total}"].font = Font(name="Arial", bold=True, size=10)
    s[f"B{total}"] = f"=SUM(B5:B{total-1})"
    s[f"B{total}"].font = Font(name="Arial", bold=True, size=10)
    s.column_dimensions["A"].width = 74
    s.column_dimensions["B"].width = 12
    return s


def format_sheet(ws):
    """Header row, dropdown, widths, freeze. Shared by init and migrate."""
    for c, h in enumerate(HEADERS, start=1):
        cell = ws.cell(1, c, h)
        cell.font = Font(name="Arial", bold=True, size=11, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1F3864")
        cell.alignment = Alignment(horizontal="left", vertical="center")
        cell.border = BORDER
    ws.row_dimensions[1].height = 22
    dv = DataValidation(type="list", formula1='"' + ",".join(STATUSES) + '"',
                        allow_blank=False, showDropDown=False)
    dv.promptTitle, dv.prompt = "Status", "Pick one: " + ", ".join(STATUSES)
    dv.errorTitle, dv.error = "Invalid status", "Choose from the dropdown."
    ws.add_data_validation(dv)
    dv.add(f"E2:E{DV_LAST_ROW}")
    for col, w in WIDTHS.items():
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"
    return ws


def cmd_init(a):
    if os.path.exists(a.xlsx):
        sys.exit(f"{a.xlsx} already exists. Refusing to overwrite.")
    guard_excel()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Applications"
    format_sheet(ws)
    build_summary(wb)
    wb.save(a.xlsx)
    print(f"created {a.xlsx}")


def cmd_migrate(a):
    """Widen an old 6-column tracker to the 9-column layout. Idempotent."""
    guard_excel()
    wb = openpyxl.load_workbook(a.xlsx)
    old = wb["Applications"]
    if old.cell(1, POSTED_COL).value == "Date Posted":
        print("already migrated")
        return
    keep = []
    for r in range(2, old.max_row + 1):
        if old.cell(r, 2).value is None:
            continue
        keep.append([old.cell(r, c).value for c in range(1, 7)])  # ..., status, notes
    idx = wb.sheetnames.index("Applications")
    wb.remove(old)
    ws = wb.create_sheet("Applications", idx)
    format_sheet(ws)
    for i, (title, company, city, pay, status, notes) in enumerate(keep, start=2):
        for c, v in enumerate([title, company, city, pay, status], start=1):
            style_cell(ws.cell(i, c, v), c)
        for c in DATE_COLS:
            set_date(ws, i, c, None)
        style_cell(ws.cell(i, NOTES_COL, notes or ""), NOTES_COL)
        apply_status(ws, i, str(status))
    ws.auto_filter.ref = f"A1:{chr(64+NOTES_COL)}{ws.max_row}"
    build_summary(wb)
    wb.save(a.xlsx)
    print(f"migrated {len(keep)} rows to {len(HEADERS)} columns")


def cmd_add(a):
    guard_excel()
    wb = openpyxl.load_workbook(a.xlsx)
    ws = wb["Applications"]
    existing = {(str(ws.cell(r, 1).value), str(ws.cell(r, 2).value))
                for r in range(2, ws.max_row + 1)}
    if (a.title, a.company) in existing:
        print(f"already tracked: {a.title} @ {a.company}")
        return
    r = ws.max_row + 1
    for c, v in enumerate([a.title, a.company, a.city, a.pay, a.status], start=1):
        style_cell(ws.cell(r, c, v), c)
    set_date(ws, r, POSTED_COL, a.posted)
    set_date(ws, r, APPLIED_COL, a.applied)
    set_date(ws, r, DEADLINE_COL, a.deadline)
    style_cell(ws.cell(r, NOTES_COL, a.notes or ""), NOTES_COL)
    apply_status(ws, r, a.status)
    ws.auto_filter.ref = f"A1:{chr(64+NOTES_COL)}{ws.max_row}"
    wb.save(a.xlsx)
    print(f"added row {r}: {a.title} @ {a.company} [{a.status}]")


def _match_rows(ws, company, title=None):
    hits = []
    for r in range(2, ws.max_row + 1):
        if str(ws.cell(r, 2).value).strip().lower() == company.strip().lower():
            if title and title.strip().lower() not in str(ws.cell(r, 1).value).strip().lower():
                continue
            hits.append(r)
    return hits


def cmd_set_status(a):
    guard_excel()
    wb = openpyxl.load_workbook(a.xlsx)
    ws = wb["Applications"]
    hits = _match_rows(ws, a.company, a.title)
    if not hits:
        sys.exit(f"no row for company '{a.company}'"
                 + (f" with title containing '{a.title}'" if a.title else ""))
    if len(hits) > 1 and not a.title:
        rows = ", ".join(f"row {r} ({ws.cell(r,1).value})" for r in hits)
        sys.exit(f"'{a.company}' matches multiple rows: {rows}\nPass --title to disambiguate.")
    for r in hits:
        apply_status(ws, r, a.status)
        if a.notes:
            ws.cell(r, NOTES_COL).value = a.notes
        print(f"row {r}: {ws.cell(r,1).value} @ {a.company} -> {a.status}")
    wb.save(a.xlsx)


def cmd_note(a):
    guard_excel()
    wb = openpyxl.load_workbook(a.xlsx)
    ws = wb["Applications"]
    hits = _match_rows(ws, a.company, a.title)
    if not hits:
        sys.exit(f"no row for company '{a.company}'")
    for r in hits:
        cur = ws.cell(r, NOTES_COL).value or ""
        if a.append not in cur:
            ws.cell(r, NOTES_COL).value = (cur + " || " + a.append).lstrip(" |")
        print(f"row {r}: note appended")
    wb.save(a.xlsx)


def cmd_dates(a):
    """Fill Date Posted / Date Applied / Deadline. Omitted flags are left alone."""
    guard_excel()
    wb = openpyxl.load_workbook(a.xlsx)
    ws = wb["Applications"]
    hits = _match_rows(ws, a.company, a.title)
    if not hits:
        sys.exit(f"no row for company '{a.company}'")
    if len(hits) > 1 and not a.title:
        rows = ", ".join(f"row {r} ({ws.cell(r,1).value})" for r in hits)
        sys.exit(f"'{a.company}' matches multiple rows: {rows}\nPass --title to disambiguate.")
    for r in hits:
        for col, val in ((POSTED_COL, a.posted), (APPLIED_COL, a.applied),
                         (DEADLINE_COL, a.deadline)):
            if val is not None:
                set_date(ws, r, col, val)
        print(f"row {r}: {ws.cell(r,1).value} @ {a.company} "
              f"posted={ws.cell(r,POSTED_COL).value} "
              f"applied={ws.cell(r,APPLIED_COL).value} "
              f"deadline={ws.cell(r,DEADLINE_COL).value}")
    wb.save(a.xlsx)


def cmd_sweep_deadlines(a):
    """Not Applied + deadline already past -> Passed Up. Blank deadlines untouched."""
    guard_excel()
    today = parse_date(a.today) if a.today else datetime.date.today()
    wb = openpyxl.load_workbook(a.xlsx)
    ws = wb["Applications"]
    changed = []
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, 2).value is None:
            continue
        if str(ws.cell(r, 5).value).strip() != "Not Applied":
            continue
        d = parse_date(ws.cell(r, DEADLINE_COL).value)
        if d and d < today:
            apply_status(ws, r, "Passed Up")
            changed.append((r, ws.cell(r, 2).value, ws.cell(r, 1).value, d))
    if not changed:
        print(f"no Not Applied rows past deadline as of {today}")
        return
    for r, co, ti, d in changed:
        print(f"row {r}: {co} - {ti} (deadline {d}) -> Passed Up")
    wb.save(a.xlsx)


def cmd_edit(a):
    """Correct Job Title / City / Pay. Omitted flags are left alone."""
    guard_excel()
    wb = openpyxl.load_workbook(a.xlsx)
    ws = wb["Applications"]
    hits = _match_rows(ws, a.company, a.title)
    if not hits:
        sys.exit(f"no row for company '{a.company}'")
    if len(hits) > 1 and not a.title:
        rows = ", ".join(f"row {r} ({ws.cell(r,1).value})" for r in hits)
        sys.exit(f"'{a.company}' matches multiple rows: {rows}\nPass --title to disambiguate.")
    for r in hits:
        for col, val in ((1, a.set_title), (2, a.set_company), (3, a.city), (4, a.pay)):
            if val is not None:
                style_cell(ws.cell(r, col, val), col)
        print(f"row {r}: {ws.cell(r,1).value} @ {ws.cell(r,2).value} | "
              f"{ws.cell(r,3).value} | {ws.cell(r,4).value}")
    wb.save(a.xlsx)


def cmd_report(a):
    wb = openpyxl.load_workbook(a.xlsx)
    ws = wb["Applications"]
    rows = []
    for r in range(2, ws.max_row + 1):
        if ws.cell(r, 2).value is None:
            continue
        rows.append({
            "row": r,
            "title": ws.cell(r, 1).value,
            "company": ws.cell(r, 2).value,
            "city": ws.cell(r, 3).value,
            "pay": ws.cell(r, 4).value,
            "status": str(ws.cell(r, 5).value),
            "posted": parse_date(ws.cell(r, POSTED_COL).value),
            "applied": parse_date(ws.cell(r, APPLIED_COL).value),
            "deadline": parse_date(ws.cell(r, DEADLINE_COL).value),
            "notes": ws.cell(r, NOTES_COL).value or "",
        })
    today = datetime.date.today()
    upcoming = sorted(
        (x for x in rows if x["deadline"] and x["status"] in ("Not Applied", "Passed Up")),
        key=lambda x: x["deadline"])
    overdue = [x for x in upcoming if x["deadline"] < today and x["status"] == "Not Applied"]
    counts = Counter(x["status"] for x in rows)
    flagged = [x for x in rows
               if any(k in x["notes"].upper()
                      for k in ("ACTION NEEDED", "DEADLINE", "CLOSES", "PRIORITY"))]
    payload = {
        "total": len(rows),
        "counts": {s: counts.get(s, 0) for s in STATUSES},
        "not_applied": [x for x in rows if x["status"] == "Not Applied"],
        "interview": [x for x in rows if x["status"] == "Interview"],
        "flagged": flagged,
        "deadlines": upcoming,
        "overdue": overdue,
    }
    if a.json:
        print(json.dumps(payload, indent=2, default=str))
        return
    print(f"TRACKER: {a.xlsx}\n")
    for s in STATUSES:
        print(f"  {s:<15} {counts.get(s,0)}")
    print(f"  {'TOTAL':<15} {len(rows)}\n")
    if payload["interview"]:
        print("INTERVIEWS")
        for x in payload["interview"]:
            print(f"  {x['company']} - {x['title']}")
            if x["notes"]:
                print(f"      {x['notes'][:150]}")
        print()
    if upcoming:
        print("DEADLINES (unsubmitted)")
        for x in upcoming:
            days = (x["deadline"] - today).days
            when = "PASSED" if days < 0 else ("TODAY" if days == 0 else f"{days}d")
            print(f"  {str(x['deadline']):<12} {when:<7} {x['company']:<34} [{x['status']}]")
        print()
    if overdue:
        print("OVERDUE, still Not Applied -> run sweep-deadlines")
        for x in overdue:
            print(f"  {x['company']} - {x['title']}")
        print()
    if payload["not_applied"]:
        print("NOT YET APPLIED")
        for x in payload["not_applied"]:
            d = str(x["deadline"]) if x["deadline"] else "no deadline"
            print(f"  {x['company']:<32} {x['title'][:38]:<40} {d}")
        print()
    if flagged:
        print("FLAGGED (deadline / action needed)")
        for x in flagged:
            print(f"  {x['company']:<32} {x['notes'][:110]}")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                               formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("init"); q.add_argument("xlsx"); q.set_defaults(fn=cmd_init)

    q = sub.add_parser("migrate"); q.add_argument("xlsx"); q.set_defaults(fn=cmd_migrate)

    q = sub.add_parser("dates")
    q.add_argument("xlsx")
    q.add_argument("--company", required=True)
    q.add_argument("--title", default=None)
    q.add_argument("--posted", default=None, help="YYYY-MM-DD")
    q.add_argument("--applied", default=None, help="YYYY-MM-DD")
    q.add_argument("--deadline", default=None, help="YYYY-MM-DD")
    q.set_defaults(fn=cmd_dates)

    q = sub.add_parser("edit")
    q.add_argument("xlsx")
    q.add_argument("--company", required=True, help="match on this")
    q.add_argument("--title", default=None, help="match on this too")
    q.add_argument("--set-title", default=None)
    q.add_argument("--set-company", default=None)
    q.add_argument("--city", default=None)
    q.add_argument("--pay", default=None)
    q.set_defaults(fn=cmd_edit)

    q = sub.add_parser("sweep-deadlines")
    q.add_argument("xlsx")
    q.add_argument("--today", default=None, help="override today, YYYY-MM-DD")
    q.set_defaults(fn=cmd_sweep_deadlines)

    q = sub.add_parser("add")
    q.add_argument("xlsx")
    for f in ("title", "company", "city", "pay"):
        q.add_argument(f"--{f}", required=True)
    q.add_argument("--status", default="Not Applied", choices=STATUSES)
    q.add_argument("--notes", default="")
    q.add_argument("--posted", default=None, help="YYYY-MM-DD")
    q.add_argument("--applied", default=None, help="YYYY-MM-DD")
    q.add_argument("--deadline", default=None, help="YYYY-MM-DD")
    q.set_defaults(fn=cmd_add)

    q = sub.add_parser("set-status")
    q.add_argument("xlsx")
    q.add_argument("--company", required=True)
    q.add_argument("--status", required=True, choices=STATUSES)
    q.add_argument("--title", default=None)
    q.add_argument("--notes", default=None)
    q.set_defaults(fn=cmd_set_status)

    q = sub.add_parser("note")
    q.add_argument("xlsx")
    q.add_argument("--company", required=True)
    q.add_argument("--append", required=True)
    q.add_argument("--title", default=None)
    q.set_defaults(fn=cmd_note)

    q = sub.add_parser("report")
    q.add_argument("xlsx")
    q.add_argument("--json", action="store_true")
    q.set_defaults(fn=cmd_report)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
