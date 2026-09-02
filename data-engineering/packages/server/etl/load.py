"""Staging and canonical-load steps for the availability ETL.

`stage` writes every extracted row to `raw_availability_events`
unconditionally — it is an append-only log, so re-ingesting a file is safe
and auditable. `load_pending` then validates each pending row and, if it
passes, upserts it into `users` keyed on the *normalized phone number* rather
than the staging row's id, so the same person arriving from two feeds — or
the same feed ingested twice — lands as one row, not a duplicate.
"""

import json
import uuid
from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.orm import Session

from server.db.models import RawAvailabilityEvent, User
from server.etl.extract import RawAvailabilityRecord
from server.etl.transform import normalize_days, normalize_phone


def stage(db: Session, records: list[RawAvailabilityRecord]) -> list[RawAvailabilityEvent]:
    rows = [
        RawAvailabilityEvent(
            source=record.source,
            first_name=record.first_name,
            last_name=record.last_name,
            phone_number=record.phone_number,
            availability_raw=json.dumps(record.availability_raw, separators=(",", ":")),
            raw_payload=record.raw_payload,
            status="pending",
        )
        for record in records
    ]
    db.add_all(rows)
    db.commit()
    return rows


@dataclass
class IngestResult:
    staged: int = 0
    loaded: int = 0
    rejected: int = 0
    errors: list[str] = field(default_factory=list)


def load_pending(db: Session) -> IngestResult:
    pending = db.scalars(
        select(RawAvailabilityEvent).where(RawAvailabilityEvent.status == "pending")
    ).all()

    result = IngestResult(staged=len(pending))
    for event in pending:
        error = _validate_and_upsert(db, event)
        if error is None:
            event.status = "loaded"
            result.loaded += 1
        else:
            event.status = "rejected"
            event.error = error
            result.rejected += 1
            result.errors.append(f"{event.source} row {event.id}: {error}")
    db.commit()
    return result


def _validate_and_upsert(db: Session, event: RawAvailabilityEvent) -> str | None:
    if not event.first_name or not event.last_name:
        return "missing first or last name"

    if not event.phone_number:
        return "missing phone number"
    phone = normalize_phone(event.phone_number)
    if phone is None:
        return f"unparseable phone number: {event.phone_number!r}"

    raw_days = json.loads(event.availability_raw)
    days = normalize_days(raw_days)
    if days is None:
        return f"no recognized available day in {raw_days!r}"

    existing = db.scalar(select(User).where(User.phoneNumber == phone))
    availability = json.dumps({"availableDays": days}, separators=(",", ":"))
    if existing is None:
        db.add(
            User(
                id=str(uuid.uuid4()),
                firstName=event.first_name,
                lastName=event.last_name,
                phoneNumber=phone,
                availability=availability,
            )
        )
    else:
        existing.firstName = event.first_name
        existing.lastName = event.last_name
        existing.phoneNumber = phone
        existing.availability = availability
    return None
