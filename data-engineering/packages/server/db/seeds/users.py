import json
import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from server.db.models import User


def seed(db: Session) -> None:
    # Only seed an empty table so edits survive restarts on a persisted database.
    existing = db.scalar(select(func.count()).select_from(User)) or 0
    if existing > 0:
        return

    db.add_all(
        [
            User(
                id=str(uuid.uuid4()),
                firstName="Ada",
                lastName="Lovelace",
                phoneNumber="+15555550101",
                availability=json.dumps(
                    {"availableDays": ["Mon", "Tue", "Wed", "Thu", "Fri"]},
                    separators=(",", ":"),
                ),
            ),
            User(
                id=str(uuid.uuid4()),
                firstName="Grace",
                lastName="Hopper",
                phoneNumber="+15555550102",
                availability=json.dumps(
                    {"availableDays": ["Tue", "Wed", "Thu"]},
                    separators=(",", ":"),
                ),
            ),
            User(
                id=str(uuid.uuid4()),
                firstName="Katherine",
                lastName="Johnson",
                phoneNumber="+15555550103",
                availability=json.dumps(
                    {"availableDays": ["Sat", "Sun"]},
                    separators=(",", ":"),
                ),
            ),
            User(
                id=str(uuid.uuid4()),
                firstName="Mae",
                lastName="Jemison",
                phoneNumber="+15555550104",
                availability=json.dumps(
                    {"availableDays": ["Mon", "Wed", "Fri"]},
                    separators=(",", ":"),
                ),
            ),
        ]
    )
    db.commit()
