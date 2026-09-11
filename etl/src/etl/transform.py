"""Validation and normalization for extracted availability rows.

A row that parsed successfully in `extract.py` can still fail here: a phone
number that isn't a real phone number, a day name outside the canonical set,
a missing name. Rejecting those rows outright (rather than coercing a best
guess) is the point of the exercise — the alternative is a `users` table that
silently disagrees with what the partner clinic actually sent.
"""

import json
import re
from collections.abc import Sequence
from dataclasses import dataclass, field

from etl.extract import RawAvailabilityRecord

CANONICAL_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

_DAY_ALIASES = {
    "mon": "Mon",
    "monday": "Mon",
    "tue": "Tue",
    "tues": "Tue",
    "tuesday": "Tue",
    "wed": "Wed",
    "weds": "Wed",
    "wednesday": "Wed",
    "thu": "Thu",
    "thur": "Thu",
    "thurs": "Thu",
    "thursday": "Thu",
    "fri": "Fri",
    "friday": "Fri",
    "sat": "Sat",
    "saturday": "Sat",
    "sun": "Sun",
    "sunday": "Sun",
}


@dataclass(frozen=True)
class TransformedRecord:
    first_name: str
    last_name: str
    phone_number: str
    availability: str


@dataclass
class TransformResult:
    ready: list[TransformedRecord] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def normalize_phone(raw: str) -> str | None:
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 10:
        return f"+1{digits}"
    if len(digits) == 11 and digits.startswith("1"):
        return f"+{digits}"
    return None


def normalize_days(raw_days: Sequence[str]) -> list[str] | None:
    if not raw_days:
        return None
    normalized: set[str] = set()
    for raw in raw_days:
        day = _DAY_ALIASES.get(raw.strip().lower())
        if day is None:
            return None
        normalized.add(day)
    return sorted(normalized, key=CANONICAL_DAYS.index)


def transform(records: list[RawAvailabilityRecord]) -> TransformResult:
    result = TransformResult()
    for record in records:
        error = _validation_error(record)
        if error is not None:
            result.errors.append(f"{record.source} row: {error}")
            continue
        phone = normalize_phone(record.phone_number)
        days = normalize_days(record.availability_raw)
        result.ready.append(
            TransformedRecord(
                first_name=record.first_name,
                last_name=record.last_name,
                phone_number=phone,
                availability=json.dumps({"availableDays": days}, separators=(",", ":")),
            )
        )
    return result


def _validation_error(record: RawAvailabilityRecord) -> str | None:
    if not record.first_name or not record.last_name:
        return "missing first or last name"

    if not record.phone_number:
        return "missing phone number"
    if normalize_phone(record.phone_number) is None:
        return "unparseable phone number"

    if normalize_days(record.availability_raw) is None:
        return f"no recognized available day in {record.availability_raw!r}"

    return None
