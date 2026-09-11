"""Load transformed availability rows into `users`.

Upserts each row keyed on the *normalized phone number*, so re-ingesting the
same feed lands as one row, not a duplicate.
"""

import sqlite3
import uuid

from etl.transform import TransformedRecord


def load(conn: sqlite3.Connection, records: list[TransformedRecord]) -> int:
    for record in records:
        existing = conn.execute(
            "SELECT id FROM users WHERE phoneNumber = ?", (record.phone_number,)
        ).fetchone()
        if existing is None:
            conn.execute(
                "INSERT INTO users (id, firstName, lastName, phoneNumber, availability) VALUES (?, ?, ?, ?, ?)",
                (
                    str(uuid.uuid4()),
                    record.first_name,
                    record.last_name,
                    record.phone_number,
                    record.availability,
                ),
            )
        else:
            conn.execute(
                "UPDATE users SET firstName = ?, lastName = ?, phoneNumber = ?, availability = ? WHERE id = ?",
                (
                    record.first_name,
                    record.last_name,
                    record.phone_number,
                    record.availability,
                    existing["id"],
                ),
            )
    conn.commit()
    return len(records)
