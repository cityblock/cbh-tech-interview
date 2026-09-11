# Cityblock Tech Interview — After Hours Support

A monorepo for the System Design Interview: a GraphQL web app for managing nurse
availability, plus a Python ETL pipeline that ingests partner clinic feeds into the
same `users` table.

The candidate-facing PRD lives in [`PRD.md`](./PRD.md) (also shared as a Google
Doc at the start of the interview).

> The scaffold ships the **legacy** `User` model (`{ availableDays: string[] }`
> jsonb) end-to-end. Extending it is the exercise.

## What's here

| Component | Path | What it does |
| --------- | ---- | ------------ |
| Web app | [`packages/`](./packages/) | React UI + GraphQL server for viewing and editing nurse availability |
| ETL pipeline | [`etl/`](./etl/) | Ingests partner clinic CSV/JSON feeds into the shared `users` table |

Both components read and write the same file-backed SQLite database
(`data/app.sqlite` by default), so rows ingested by the ETL show up immediately
in the running app.

## Quick start

**Web app** — Node 22, pnpm 10:

```bash
pnpm install
pnpm dev
```

Web: <http://localhost:5173> · GraphQL: <http://localhost:4000/graphql>

**ETL** — Python 3.12+, [uv](https://docs.astral.sh/uv/):

```bash
cd etl
uv sync --extra dev
uv run etl
```

See the component READMEs for full setup, configuration, and layout details:

- [`packages/README.md`](./packages/README.md) — web app and GraphQL server
- [`etl/README.md`](./etl/README.md) — partner clinic feed ingestion pipeline

## Layout

```
packages/
  server/   GraphQL Yoga + Knex (better-sqlite3, file-backed)
  web/      Vite + React 18 + Apollo Client
etl/        Standalone Python pipeline that ingests partner clinic feeds into `users`
```

## Shared configuration

| Env var   | Default           | What it does |
| --------- | ----------------- | ------------ |
| `PORT`    | `4000`            | GraphQL server port |
| `DB_FILE` | `data/app.sqlite` | SQLite file path shared by the server and ETL. Set `DB_FILE=:memory:` for an ephemeral database. |
