# Availability ETL

A standalone Python pipeline that ingests partner availability feeds into the
`users` table used by the [web app](../packages/README.md) (`packages/server`,
file-backed SQLite).

## Prereqs

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Run it

```bash
uv sync
uv run etl                          # ingests the default fixture feed
uv run etl data/fixtures/scheds_pract_mgr.csv   # or ingest specific files
```

It prints how many rows were staged, loaded, and rejected, plus a reason for
each rejection.

## What it does

The default run ingests `data/fixtures/scheds_pract_mgr.csv` — nurse
availability submitted by clinic practice managers (`first_name`, `last_name`,
`phone`, `timezone`, `schedule_windows`, `blocked_dates`). Schedule windows use
`Day:HH:MM-HH:MM` segments separated by `;`. Blocked dates use
`start:end:reason`.

1. **Extract** (`src/etl/extract.py`) — parses each feed's rows into a common
   `RawAvailabilityRecord`, without validating or normalizing anything.
2. **Transform + load** (`src/etl/transform.py`, `src/etl/load.py::load`) —
   validates and normalizes each row (phone number, availability days),
   rejecting anything that doesn't pass, then upserts the valid rows into
   `users` keyed on the *normalized phone number* — re-ingesting the same
   feed lands as one row, not a duplicate.

`src/etl/db.py` creates `users` (`CREATE TABLE IF NOT EXISTS`) on connect
and records `0001_users` in `_migrations`, so the pipeline can run
standalone before the Node app has ever booted without Knex trying to
recreate `users` on the next `pnpm dev`.

## Layout

```
src/etl/
  db.py         — SQLite connection + schema
  extract.py    — partner feed parsers
  transform.py  — phone/day validation and normalization
  load.py       — validate + upsert into `users`
  pipeline.py   — orchestrates extract → load; `etl` CLI entry point
data/fixtures/  — partner feed fixtures, git-tracked
tests/          — pytest suite
```

## Commands

| Command         | What it does                             |
| --------------- | ----------------------------------------- |
| `uv run etl`    | Runs the ETL against the default fixture feed |
| `uv run pytest` | Runs the test suite                       |
