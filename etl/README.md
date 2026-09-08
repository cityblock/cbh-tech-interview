# Availability ETL

A standalone Python pipeline that ingests partner availability feeds into the
`users` table used by the [root app](../README.md) (`packages/server`,
file-backed SQLite). It reads and writes the **same** `data/app.sqlite` file
the Node server uses — by default `packages/server/data/app.sqlite`, override
with `DB_FILE` — so ingested rows show up immediately when you run `pnpm dev`.

## Prereqs

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Run it

```bash
uv sync
uv run etl                          # ingests every file in data/fixtures/
uv run etl data/fixtures/sched_self_serv_app.csv   # or ingest specific files
```

It prints how many rows were staged, loaded, and rejected, plus a reason for
each rejection.

## What it does

The default run ingests `data/fixtures/sched_self_serv_app.csv` — nurse
availability exported from the self-service app (`first_name`, `last_name`,
`phone`, `days`).

A second feed is also available:

- `data/fixtures/scheds_pract_mgr.csv` — nurse availability submitted by clinic
  practice managers (`first_name`, `last_name`, `phone`, `timezone`,
  `schedule_windows`, `blocked_dates`). Schedule windows use
  `Day:HH:MM-HH:MM` segments separated by `;`. Blocked dates use
  `start:end:reason`.

```bash
uv run etl data/fixtures/scheds_pract_mgr.csv
```

1. **Extract** (`src/etl/extract.py`) — parses each feed's rows into a common
   `RawAvailabilityRecord`, without validating or normalizing anything.
2. **Stage** (`src/etl/load.py::stage`) — writes every extracted row to
   `raw_availability_events`, an append-only log, so re-ingesting a file is
   safe and auditable.
3. **Transform + load** (`src/etl/transform.py`, `src/etl/load.py::load_pending`) —
   validates and normalizes each pending row (phone number, availability
   days), rejecting anything that doesn't pass, then upserts the valid rows
   into `users` keyed on the *normalized phone number* — re-ingesting the
   same feed lands as one row, not a duplicate.

`src/etl/db.py` creates both tables (`CREATE TABLE IF NOT EXISTS`) on
connect and records `0001_users` in `_migrations`, so the pipeline can run
standalone before the Node app has ever booted without Knex trying to
recreate `users` on the next `pnpm dev`.

## Layout

```
src/etl/
  db.py         — SQLite connection + schema
  extract.py    — partner feed parsers
  transform.py  — phone/day validation and normalization
  load.py       — stage + upsert into `users`
  pipeline.py   — orchestrates extract → stage → load; `etl` CLI entry point
data/fixtures/  — partner feed fixtures, git-tracked
tests/          — pytest suite
```

## Commands

| Command         | What it does                             |
| --------------- | ----------------------------------------- |
| `uv run etl`    | Runs the ETL, default input `data/fixtures/` |
| `uv run pytest` | Runs the test suite                       |
