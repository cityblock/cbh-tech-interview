# Cityblock Tech Interview — After Hours Support

A minimal, working project for the System Design Interview. The candidate-facing PRD lives in [`PRD.md`](./PRD.md) (also shared as a Google Doc at the start of the interview).

> The scaffold ships the **legacy** `User` model (`{ availableDays: string[] }` jsonb) end-to-end. Extending it is the exercise.

## Prereqs

- Python 3.12 (`uv` will pick up `.python-version`)
- uv 0.12 (`brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Run it

```bash
uv sync
uv run dev
```

- Web app: <http://localhost:4000>
- GraphQL endpoint (with built-in playground): <http://localhost:4000/graphql>

The database is **file-backed SQLite**, persisted to `data/app.sqlite` (git-ignored), so **state survives restarts**. On boot the server runs any pending migrations — tracked in an `alembic_version` table, so each runs exactly once — and seeds the demo users **only when the `users` table is empty**, so your edits are never clobbered.

### Resetting the database

To start from a clean slate, remove the file and restart (boot re-migrates and re-seeds):

```bash
rm data/app.sqlite          # or keep a backup: mv data/app.sqlite data/app.sqlite.bak
uv run dev
```

### Configuration

| Env var   | Default           | What it does                                                        |
| --------- | ----------------- | ------------------------------------------------------------------- |
| `PORT`    | `4000`            | Server port                                                         |
| `DB_FILE` | `data/app.sqlite` | SQLite file path. Set `DB_FILE=:memory:` for an ephemeral database. |

## Layout

```
packages/
  server/   Strawberry GraphQL on FastAPI + SQLAlchemy (Alembic, file-backed SQLite)
  web/      Jinja2 templates, served by the same FastAPI app
```

### Where to look

**Server**

- `packages/server/types.py` — GraphQL types
- `packages/server/schema.py` — schema assembly
- `packages/server/resolvers/user.py` — resolvers
- `packages/server/db/migrations/versions/0001_users.py` — `users` table
- `packages/server/db/models.py` — SQLAlchemy model
- `packages/server/db/seeds/users.py` — seeded users
- `packages/server/db/engine.py` — engine configuration

**Web**

- `packages/web/templates/user_list.html` — list view
- `packages/web/templates/user_edit.html` — edit form
- `packages/web/graphql/user.py` — GraphQL operations

## Commands

| Command                 | What it does                                     |
| ----------------------- | ------------------------------------------------ |
| `uv run dev`            | Runs the app and GraphQL endpoint on `:4000`     |
| `uv run pytest`         | Runs the test suite                              |
| `uv run ruff check .`   | Lints                                            |
| `uv run ruff format .`  | Formats                                          |
| `uv run alembic ...`    | Migration CLI, e.g. `alembic upgrade head`       |

## Replacing the exercise

This track is a Python mirror of `software-engineering/`, and the exercise content is meant to be swapped out. The seam sits here:

- **Exercise-specific**, replace freely: `packages/server/types.py`, `packages/server/resolvers/`, `packages/server/db/models.py`, `packages/server/db/migrations/versions/`, `packages/server/db/seeds/`, `packages/web/templates/`, `packages/server/test/test_user.py`, and `PRD.md`.
- **Plumbing**, expected to survive a swap: `pyproject.toml`, `alembic.ini`, `packages/server/index.py`, `packages/server/context.py`, `packages/server/schema.py`, `packages/server/db/engine.py`, `packages/server/db/migrate.py`, `packages/server/db/seed.py`, `packages/web/routes.py`, `packages/web/client.py`, and `packages/server/test/conftest.py`.
