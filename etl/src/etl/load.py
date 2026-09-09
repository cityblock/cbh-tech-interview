"""Validation and load steps for the availability ETL.

`load` validates each extracted row and, if it passes, upserts it into
`users` keyed on the *normalized phone number*, so re-ingesting the same
feed lands as one row, not a duplicate.
"""

import json
import sqlite3
import uuid
from dataclasses import dataclass, field

from etl.extract import RawAvailabilityRecord
from etl.transform import normalize_days, normalize_phone


@dataclass
class IngestResult:
    staged: int = 0
    loaded: int = 0
    rejected: int = 0
    errors: list[str] = field(default_factory=list)


def load(conn: sqlite3.Connection, records: list[RawAvailabilityRecord]) -> IngestResult:
    result = IngestResult(staged=len(records))
    for record in records:
        error = _validate_and_upsert(conn, record)
        if error is None:
            result.loaded += 1
        else:
            result.rejected += 1
            result.errors.append(f"{record.source} row: {error}")
    conn.commit()
    return result


def _validate_and_upsert(conn: sqlite3.Connection, record: RawAvailabilityRecord) -> str | None:
    if not record.first_name or not record.last_name:
        return "missing first or last name"

    if not record.phone_number:
        return "missing phone number"
    phone = normalize_phone(record.phone_number)
    if phone is None:
        return "unparseable phone number"

    days = normalize_days(record.availability_raw)
    if days is None:
        return f"no recognized available day in {record.availability_raw!r}"

    availability = json.dumps({"availableDays": days}, separators=(",", ":"))
    existing = conn.execute("SELECT id FROM users WHERE phoneNumber = ?", (phone,)).fetchone()
    if existing is None:
        conn.execute(
            "INSERT INTO users (id, firstName, lastName, phoneNumber, availability) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), record.first_name, record.last_name, phone, availability),
        )
    else:
        conn.execute(
            "UPDATE users SET firstName = ?, lastName = ?, phoneNumber = ?, availability = ? WHERE id = ?",
            (record.first_name, record.last_name, phone, availability, existing["id"]),
        )
    return None
