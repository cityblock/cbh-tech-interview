"""Orchestrates the availability ETL: extract every feed file, stage every
row, then validate and load the ones that pass into `users`.

Run via `uv run etl` (defaults to every file in `data/fixtures/`) or
`uv run etl <path> [<path> ...]` to ingest specific files.
"""

import sys
from pathlib import Path

from server.db.engine import Session
from server.db.migrate import migrate
from server.etl.extract import extract
from server.etl.load import IngestResult, load_pending, stage

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "data" / "fixtures"


def ingest(paths: list[Path]) -> IngestResult:
    migrate()
    with Session() as db:
        records = [record for path in paths for record in extract(path)]
        stage(db, records)
        return load_pending(db)


def main() -> None:
    args = sys.argv[1:]
    paths = [Path(arg) for arg in args] if args else sorted(FIXTURES_DIR.iterdir())

    result = ingest(paths)
    print(f"staged {result.staged} → loaded {result.loaded}, rejected {result.rejected}")
    for error in result.errors:
        print(f"  ! {error}")
