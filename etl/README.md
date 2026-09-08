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
uv run etl data/fixtures/partner_a.csv   # or ingest specific files
```

It prints how many rows were staged, loaded, and rejected, plus a reason for
each rejection.

## What it does

The default run ingests `data/fixtures/partner_a.csv`, which includes a few
intentionally malformed rows. Two additional feeds ship unwired:

- `data/fixtures/partner_b.json` — nested JSON with a different shape than the
  CSV (`contact` object, `availableDays` array).
- `data/fixtures/partner_c.csv` — schedule windows with start/end times (many
  outside the org's historical 9am–5pm ET window) plus one-off blocked date
  ranges (vacations, conferences). The file also includes planted data-quality
  issues: malformed dates, bad phone numbers, and invalid day names. The
  scaffold parser only extracts day names; hours, time zones, and `blocked_dates`
  are preserved in `raw_payload` but dropped on load. Wiring this feed up without
  losing that detail is the stretch exercise — it mirrors extending the legacy
  `{ availableDays: string[] }` model in the root app.

```bash
uv run etl data/fixtures/partner_c.csv
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
