"""Orchestrates the availability ETL: extract, transform, then load into `users`.

Run via `uv run etl` (defaults to every file in `data/feeds/`) or
`uv run etl <path> [<path> ...]` to ingest specific files.
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path

from etl.db import connect
from etl.extract import extract
from etl.load import load
from etl.transform import transform

FEEDS_DIR = Path(__file__).resolve().parents[2] / "data" / "feeds"
DEFAULT_FEEDS = [FEEDS_DIR / "partner_clinic_a.csv"]


@dataclass
class IngestResult:
    staged: int = 0
    loaded: int = 0
    rejected: int = 0
    errors: list[str] = field(default_factory=list)


def ingest(paths: list[Path], db_file: str | None = None) -> IngestResult:
    records = [record for path in paths for record in extract(path)]
    transformed = transform(records)

    conn = connect(db_file)
    try:
        loaded = load(conn, transformed.ready)
    finally:
        conn.close()

    return IngestResult(
        staged=len(records),
        loaded=loaded,
        rejected=len(transformed.errors),
        errors=transformed.errors,
    )


def main() -> None:
    args = sys.argv[1:]
    paths = [Path(arg) for arg in args] if args else DEFAULT_FEEDS

    result = ingest(paths)
    print(f"staged {result.staged} → loaded {result.loaded}, rejected {result.rejected}")
    for error in result.errors:
        print(f"  ! {error}")


if __name__ == "__main__":
    main()
