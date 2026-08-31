import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Persist to a file by default so state survives restarts.
# Set DB_FILE=:memory: for an ephemeral database (e.g. tests, throwaway runs).
DB_FILE = os.environ.get("DB_FILE") or str(Path.cwd() / "data/app.sqlite")
if DB_FILE != ":memory:":
    Path(DB_FILE).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite+pysqlite:///{DB_FILE}",
    # One shared connection. For :memory: this is also what keeps the database
    # from being discarded between checkouts.
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)

Session = sessionmaker(bind=engine)
