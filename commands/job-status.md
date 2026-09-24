---
description: Report where every application stands and the next action
---

# /job-status - Where everything stands

Invoke the `job-hunting` skill and follow its **Status** section.

```bash
PY=$(bash $SKILL_DIR/scripts/ensure_venv.sh)
$PY $SKILL_DIR/scripts/tracker.py report <tracker>
```

Then add what the spreadsheet cannot say:
- deadlines inside the next week
- packets built but never submitted
- applications quiet for more than two weeks
- the single highest-value next action

Lead with anything time-boxed. If nothing is urgent, say that rather than
manufacturing urgency.
