"""SQLite connection and schema helpers for the availability ETL.

The pipeline reads and writes the same `data/app.sqlite` file the
`packages/server` app (Knex-backed) uses, so ingested rows show up
immediately in the running app. Point at a different file with `DB_FILE`
(matches the server's own env var), or `:memory:` for a throwaway run.
"""

import os
import sqlite3
from pathlib import Path

DEFAULT_DB_FILE = Path(__file__).resolve().parents[3] / "packages" / "server" / "data" / "app.sqlite"


def connect(db_file: str | None = None) -> sqlite3.Connection:
    target = db_file if db_file is not None else os.environ.get("DB_FILE", str(DEFAULT_DB_FILE))
    if target != ":memory:":
        Path(target).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(target)
    conn.row_factory = sqlite3.Row
    ensure_schema(conn)
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS _migrations (
            name TEXT PRIMARY KEY
        )
        """
    )
    # Mirrors `packages/server/src/db/migrations/0001_users.ts`; created here
    # too so the ETL can run standalone before the app has ever booted.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            firstName TEXT NOT NULL,
            lastName TEXT NOT NULL,
            phoneNumber TEXT NOT NULL,
            availability TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "INSERT OR IGNORE INTO _migrations (name) VALUES ('0001_users')"
    )
    # Append-only ingestion log populated by this package. Every row a
    # partner feed produces is staged here first, whether or not it ends up
    # in `users` — that keeps ingestion auditable and lets the same file be
    # re-ingested without losing the record of previous attempts.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS raw_availability_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            phone_number TEXT,
            availability_raw TEXT NOT NULL,
            raw_payload TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            error TEXT
        )
        """
    )
    conn.commit()
