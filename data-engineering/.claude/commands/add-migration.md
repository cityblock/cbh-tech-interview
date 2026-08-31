Create a new Alembic migration for: $ARGUMENTS

You are inside a Python project managed by uv. Follow every step in order.

## 1. Read current state

Before writing anything, read:

- `packages/server/db/migrate.py`
- `packages/server/db/models.py`
- `packages/server/db/migrations/versions/` — list the directory to find the next migration number and the current head revision

## 2. Create the migration file

Generate it with the CLI so the revision is registered correctly:

```bash
uv run alembic revision --rev-id NNNN -m <slug>
```

where:

- `NNNN` is the zero-padded next integer (e.g. `0002`)
- `<slug>` is a short snake_case label derived from the arguments

This writes `packages/server/db/migrations/versions/NNNN_<slug>.py` with `upgrade()` and `downgrade()` to fill in, following the pattern in existing migration files.

**Persisted SQLite note:** The DB is **file-backed** (`data/app.sqlite`) and survives restarts. Alembic tracks applied revisions in an `alembic_version` table, so each migration runs **exactly once**, against whatever data already exists — do **not** assume an empty table. Practical implications:

- `ALTER TABLE ... ADD COLUMN` on a populated table must be **nullable or carry a `DEFAULT`** — a `NOT NULL` column with no default fails when rows already exist. If the column must end up non-null, add it nullable, **backfill** existing rows in the same `upgrade()`, then tighten the constraint.
- SQLite cannot alter a column in place. Use `op.batch_alter_table(...)` for anything beyond adding a column; batch mode is already enabled in `env.py`.
- Write `upgrade()`/`downgrade()` to be data-safe (don't destroy data you don't mean to).
- To test against a clean slate, delete the file first (`rm data/app.sqlite`) or run with `DB_FILE=:memory:`.

## 3. Update the model

Alembic chains revisions through `down_revision`, so there is no registry to edit. Instead, mirror the schema change in `packages/server/db/models.py` so the model and the migrated database agree. The new migration runs once on the next boot; previously-applied revisions are skipped.

## 4. Summarize changes

Print a concise list of every file created or modified.
