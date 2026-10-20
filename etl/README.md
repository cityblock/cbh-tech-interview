# Availability ETL

A standalone Python pipeline that ingests nurses' on-call availability schedules
from our partner clinics, loading cleaned and standardized records into the
`users` table:

| column       | type                                  |
| ------------ | ------------------------------------- |
| id           | UUID                                  |
| firstName    | string                                |
| lastName     | string                                |
| phoneNumber  | phoneNumber                           |
| availability | jsonb — `{ availableDays: [string] }` |

## Prereqs

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Data

The default `uv run etl` run ingests both partner clinic feeds in `data/feeds/`:

1. `partner_clinic_a.csv` — `first_name`, `last_name`, `phone`, and `days`. Day
   segments separated by `;`.
2. `partner_clinic_b.csv` — `first_name`, `last_name`, `phone`, `timezone`,
   `schedule_windows`, and `blocked_dates`. Schedule windows use
   `Day:HH:MM-HH:MM` segments separated by `;`. Blocked dates use
   `start:end:reason`.

## Layout

```
src/etl/
  db.py         — SQLite connection + user table shell
  extract.py    — partner clinic feed parsers
  transform.py  — phone/day validation and normalization
  load.py       — upsert into `users`
  pipeline.py   — orchestrates extract → transform → load; `etl` CLI entry point
data/feeds/     — sample partner clinic feeds, git-tracked
tests/          — pytest suite
```

## Pipeline flow

```mermaid
flowchart TB
    subgraph feeds ["Partner clinic feeds"]
        feed_a["partner_clinic_a.csv"]
        feed_b["partner_clinic_b.csv"]
    end

    subgraph etl ["ETL pipeline"]
        extract["extract.py"]
        record["RawAvailabilityRecord"]
        transform["transform.py"]
        load["load.py"]
        extract --> record
        record --> transform
        transform --> load
    end

    subgraph storage ["SQLite users table"]
        users[("users")]
    end

    feed_a --> extract
    feed_b --> extract
    load -->|"upsert by normalized phone"| users
```

Partner clinic files stay in their native shape on disk. The pipeline:

1. **Extract** (`src/etl/extract.py`) — parses each feed's rows into a common
   `RawAvailabilityRecord`, without validating or normalizing anything.
2. **Transform** (`src/etl/transform.py`) — validates and normalizes phone
   numbers and available days, rejecting rows that don't pass.
3. **Load** (`src/etl/load.py`) — upserts valid rows into `users` keyed on the
   *normalized phone number*, so re-ingesting the same feed lands as one row,
   not a duplicate.

Rows that fail validation are rejected with a reason and never written to the
table.

## Run it

```bash
uv sync --extra dev
uv run etl                                          # both feeds in data/feeds/
uv run etl data/feeds/partner_clinic_a.csv          # ingest a specific file
uv run pytest
```

`uv run etl` prints how many rows were staged, loaded, and rejected, plus a
reason for each rejection.

Loaded rows land in `../data/app.sqlite` (repo-root `data/app.sqlite`). Query
them with the `sqlite3` CLI:

```bash
sqlite3 ../data/app.sqlite "SELECT firstName, lastName, phoneNumber, availability FROM users;"
```

`availability` is stored as text containing JSON, such as
`{"availableDays":["Mon","Wed"]}`. If `DB_FILE` is set, query that path
instead.
