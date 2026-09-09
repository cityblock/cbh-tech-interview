"""Validation and normalization for extracted availability rows.

A row that parsed successfully in `extract.py` can still fail here: a phone
number that isn't a real phone number, a day name outside the canonical set,
a missing name. Rejecting those rows outright (rather than coercing a best
guess) is the point of the exercise — the alternative is a `users` table that
silently disagrees with what the partner actually sent.
"""

import re
from collections.abc import Sequence

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
