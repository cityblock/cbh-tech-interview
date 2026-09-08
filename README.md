# Cityblock Tech Interview — After Hours Support

A minimal, working monorepo for the System Design Interview. The candidate-facing PRD lives in [`PRD.md`](./PRD.md) (also shared as a Google Doc at the start of the interview).

> The scaffold ships the **legacy** `User` model (`{ availableDays: string[] }` jsonb) end-to-end. Extending it is the exercise.

## Prereqs

- Node 22 (`nvm use` will pick up `.nvmrc`)
- pnpm 10 (`corepack enable` or `npm i -g pnpm@10`)

## Run it

```bash
pnpm install
pnpm dev
```

- Web app: <http://localhost:5173>
- GraphQL endpoint (with built-in playground): <http://localhost:4000/graphql>

The database is **file-backed SQLite**, persisted to `data/app.sqlite` (git-ignored), so **state survives restarts**. On boot the server runs any pending migrations — tracked in a `_migrations` table, so each runs exactly once — and seeds the demo users **only when the `users` table is empty**, so your edits are never clobbered.

### Resetting the database

To start from a clean slate, remove the file and restart (boot re-migrates and re-seeds):

```bash
rm data/app.sqlite          # or keep a backup: mv data/app.sqlite data/app.sqlite.bak
pnpm dev
```

### Configuration

| Env var   | Default           | What it does                                                        |
| --------- | ----------------- | ------------------------------------------------------------------- |
| `PORT`    | `4000`            | GraphQL server port                                                 |
| `DB_FILE` | `data/app.sqlite` | SQLite file path. Set `DB_FILE=:memory:` for an ephemeral database. |

## Layout

```
packages/
  server/   GraphQL Yoga + Knex (better-sqlite3, file-backed)
  web/      Vite + React 18 + Apollo Client
etl/        Standalone Python pipeline that ingests partner feeds into `users`
```

See [`etl/README.md`](./etl/README.md) for the ETL pipeline.

### Where to look

**Server**

- `packages/server/src/schema.ts` — SDL types
- `packages/server/src/resolvers/user.ts` — resolvers
- `packages/server/src/db/migrations/0001_users.ts` — `users` table
- `packages/server/src/db/seeds/users.ts` — seeded users
- `packages/server/src/db/knex.ts` — Knex configuration

**Web**

- `packages/web/src/pages/UserList.tsx` — list view
- `packages/web/src/pages/UserEdit.tsx` — edit form
- `packages/web/src/graphql/user.ts` — GraphQL operations

## Commands

| Command          | What it does                                        |
| ---------------- | --------------------------------------------------- |
| `pnpm dev`       | Runs server (`:4000`) and web (`:5173`) in parallel |
| `pnpm test`      | Runs Vitest across packages                         |
| `pnpm typecheck` | TypeScript across packages                          |
| `pnpm lint`      | ESLint + Prettier check                             |
| `pnpm format`    | Prettier write                                      |
| `pnpm build`     | Builds both packages                                |
