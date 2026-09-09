"""Parsers that turn partner feed files into `RawAvailabilityRecord`s.

The active feed (`sched_self_serv_app`) is CSV. A JSON parser is also registered for
`.json` files if you pass one explicitly. `scheds_pract_mgr` is a second CSV shape
with schedule windows and blocked-date columns. Parsing only pulls fields out
of whatever shape the file has — it does not validate or normalize them. That happens in `transform.py` during load, so a parse failure and a
validation failure are never confused with each other.
"""

import csv
import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RawAvailabilityRecord:
    source: str
    first_name: str | None
    last_name: str | None
    phone_number: str | None
    availability_raw: list[str]
    raw_payload: str


def _schedule_days_from_windows(raw_windows: str) -> list[str]:
    days = []
    for window in raw_windows.split(";"):
        window = window.strip()
        if not window:
            continue
        day, _, _ = window.partition(":")
        if day:
            days.append(day)
    return days


def parse_csv_feed(path: Path) -> list[RawAvailabilityRecord]:
    source = path.stem
    with path.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if rows and "schedule_windows" in rows[0]:
        return [
            RawAvailabilityRecord(
                source=source,
                first_name=(row.get("first_name") or "").strip() or None,
                last_name=(row.get("last_name") or "").strip() or None,
                phone_number=(row.get("phone") or "").strip() or None,
                availability_raw=_schedule_days_from_windows(row.get("schedule_windows") or ""),
                raw_payload=json.dumps(row, separators=(",", ":")),
            )
            for row in rows
        ]
    return [
        RawAvailabilityRecord(
            source=source,
            first_name=(row.get("first_name") or "").strip() or None,
            last_name=(row.get("last_name") or "").strip() or None,
            phone_number=(row.get("phone") or "").strip() or None,
            availability_raw=[d.strip() for d in (row.get("days") or "").split(";") if d.strip()],
            raw_payload=json.dumps(row, separators=(",", ":")),
        )
        for row in rows
    ]


def parse_json_feed(path: Path) -> list[RawAvailabilityRecord]:
    source = path.stem
    rows = json.loads(path.read_text())
    records = []
    for row in rows:
        contact = row.get("contact") or {}
        records.append(
            RawAvailabilityRecord(
                source=source,
                first_name=contact.get("first"),
                last_name=contact.get("last"),
                phone_number=row.get("phoneNumber"),
                availability_raw=list(row.get("availableDays") or []),
                raw_payload=json.dumps(row, separators=(",", ":")),
            )
        )
    return records


_PARSERS: dict[str, Callable[[Path], list[RawAvailabilityRecord]]] = {
    ".csv": parse_csv_feed,
    ".json": parse_json_feed,
}


def extract(path: Path) -> list[RawAvailabilityRecord]:
    parser = _PARSERS.get(path.suffix.lower())
    if parser is None:
        raise ValueError(f"no parser registered for {path.suffix!r} files: {path}")
    return parser(path)
