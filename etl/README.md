# Availability ETL

A standalone Python pipeline that ingests nursing on-call schedules from our partner clinics into the `users` table.

## Prereqs

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Layout

```
src/etl/
  db.py         — SQLite connection + user table shell
  extract.py    — partner clinic feed parsers
  transform.py  — phone/day validation and normalization
  load.py       — upsert into `users`
  pipeline.py   — orchestrates extract → transform → load; `etl` CLI entry point
data/feeds/  — sample partner clinic feeds, git-tracked
tests/          — pytest suite
```

## Partner clinic data feeds

Two sample feeds live in `data/feeds/`:

- `partner_clinic_a.csv` — a simple feed with `first_name`, `last_name`, `phone`,
and `days` (`Day` segments separated by `;`). This is the default when you run
`uv run etl`.
- `partner_clinic_b.csv` — a more complex feed with `first_name`, `last_name`,
`phone`, `timezone`, `schedule_windows`, and `blocked_dates`. Schedule windows
use `Day:HH:MM-HH:MM` segments separated by `;`. Blocked dates use
`start:end:reason`. Pass its path explicitly to ingest it.

