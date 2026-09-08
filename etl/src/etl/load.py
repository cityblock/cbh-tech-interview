"""Staging and canonical-load steps for the availability ETL.

`stage` writes every extracted row to `raw_availability_events`
unconditionally — it is an append-only log, so re-ingesting a file is safe
and auditable. `load_pending` then validates each pending row and, if it
passes, upserts it into `users` keyed on the *normalized phone number* rather
than the staging row's id, so re-ingesting the same feed lands as one row,
not a duplicate.
"""

import json
import sqlite3
import uuid
from dataclasses import dataclass, field

from etl.extract import RawAvailabilityRecord
from etl.transform import normalize_days, normalize_phone


def stage(conn: sqlite3.Connection, records: list[RawAvailabilityRecord]) -> None:
    conn.executemany(
        """
        INSERT INTO raw_availability_events
            (source, first_name, last_name, phone_number, availability_raw, raw_payload, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
        """,
        [
            (
                record.source,
                record.first_name,
                record.last_name,
                record.phone_number,
                json.dumps(record.availability_raw, separators=(",", ":")),
                record.raw_payload,
            )
            for record in records
        ],
    )
    conn.commit()


@dataclass
class IngestResult:
    staged: int = 0
    loaded: int = 0
    rejected: int = 0
    errors: list[str] = field(default_factory=list)


def load_pending(conn: sqlite3.Connection) -> IngestResult:
    pending = conn.execute("SELECT * FROM raw_availability_events WHERE status = 'pending'").fetchall()

    result = IngestResult(staged=len(pending))
    for event in pending:
        error = _validate_and_upsert(conn, event)
        if error is None:
            conn.execute(
                "UPDATE raw_availability_events SET status = 'loaded' WHERE id = ?", (event["id"],)
            )
            result.loaded += 1
        else:
            conn.execute(
                "UPDATE raw_availability_events SET status = 'rejected', error = ? WHERE id = ?",
                (error, event["id"]),
            )
            result.rejected += 1
            result.errors.append(f"{event['source']} row {event['id']}: {error}")
    conn.commit()
    return result


def _validate_and_upsert(conn: sqlite3.Connection, event: sqlite3.Row) -> str | None:
    if not event["first_name"] or not event["last_name"]:
        return "missing first or last name"

    if not event["phone_number"]:
        return "missing phone number"
    phone = normalize_phone(event["phone_number"])
    if phone is None:
        return "unparseable phone number"

    raw_days = json.loads(event["availability_raw"])
    days = normalize_days(raw_days)
    if days is None:
        return f"no recognized available day in {raw_days!r}"

    availability = json.dumps({"availableDays": days}, separators=(",", ":"))
    existing = conn.execute("SELECT id FROM users WHERE phoneNumber = ?", (phone,)).fetchone()
    if existing is None:
        conn.execute(
            "INSERT INTO users (id, firstName, lastName, phoneNumber, availability) VALUES (?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), event["first_name"], event["last_name"], phone, availability),
        )
    else:
        conn.execute(
            "UPDATE users SET firstName = ?, lastName = ?, phoneNumber = ?, availability = ? WHERE id = ?",
            (event["first_name"], event["last_name"], phone, availability, existing["id"]),
        )
    return None
