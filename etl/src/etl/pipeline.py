"""Orchestrates the availability ETL: extract every feed file, then validate
and load the rows that pass into `users`.

Run via `uv run etl` (defaults to every file in `data/fixtures/`) or
`uv run etl <path> [<path> ...]` to ingest specific files.
"""

import sys
from pathlib import Path

from etl.db import connect
from etl.extract import extract
from etl.load import IngestResult, load

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "data" / "fixtures"
DEFAULT_FIXTURES = [FIXTURES_DIR / "sched_self_serv_app.csv"]


def ingest(paths: list[Path], db_file: str | None = None) -> IngestResult:
    conn = connect(db_file)
    try:
        records = [record for path in paths for record in extract(path)]
        return load(conn, records)
    finally:
        conn.close()


def main() -> None:
    args = sys.argv[1:]
    paths = [Path(arg) for arg in args] if args else DEFAULT_FIXTURES

    result = ingest(paths)
    print(f"staged {result.staged} → loaded {result.loaded}, rejected {result.rejected}")
    for error in result.errors:
        print(f"  ! {error}")


if __name__ == "__main__":
    main()
