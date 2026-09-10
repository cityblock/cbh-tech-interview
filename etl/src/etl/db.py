"""SQLite connection and schema helpers for the availability ETL.

The pipeline reads and writes the same `data/app.sqlite` file the
`packages/server` app (Knex-backed) uses, so ingested rows show up
immediately in the running app. Point at a different file with `DB_FILE`
(matches the server's own env var), or `:memory:` for a throwaway run.
"""

import os
import sqlite3
from pathlib import Path

DEFAULT_DB_FILE = Path(__file__).resolve().parents[3] / "data" / "app.sqlite"


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
    conn.execute("DROP TABLE IF EXISTS raw_availability_events")
    conn.commit()
