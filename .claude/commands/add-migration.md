Create a new Knex migration for: $ARGUMENTS

You are inside a TypeScript monorepo (pnpm workspaces). Follow every step in order.

## 1. Read current state

Before writing anything, read:

- `packages/server/src/db/migrate.ts`
- `packages/server/src/db/migrations/` — list the directory to find the next migration number

## 2. Create the migration file

Name it `packages/server/src/db/migrations/NNNN_<slug>.ts` where:

- `NNNN` is the zero-padded next integer (e.g. `0002`)
- `<slug>` is a short snake_case label derived from the arguments

Export `up(knex: Knex): Promise<void>` and `down(knex: Knex): Promise<void>`, following the pattern in existing migration files.

**Persisted SQLite note:** The DB is **file-backed** (`data/app.sqlite`) and survives restarts. `migrate()` tracks applied migrations in a `_migrations` table, so each migration runs **exactly once**, against whatever data already exists — do **not** assume an empty table. Practical implications:

- `ALTER TABLE ... ADD COLUMN` on a populated table must be **nullable or carry a `DEFAULT`** — a `NOT NULL` column with no default fails when rows already exist. If the column must end up non-null, add it nullable, **backfill** existing rows in the same `up()`, then tighten the constraint.
- Write `up()`/`down()` to be data-safe (don't destroy data you don't mean to).
- To test against a clean slate, delete the file first (`rm data/app.sqlite`) or run with `DB_FILE=:memory:`.

## 3. Register the migration in migrate.ts

Add the import and a new entry in the `migrations` array, following the existing pattern. Imports use `.js` extensions (ESM). The new migration is detected by name and run once on the next boot; previously-applied migrations (recorded in `_migrations`) are skipped.

## 4. Summarize changes

Print a concise list of every file created or modified.
