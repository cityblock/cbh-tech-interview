from sqlalchemy import Integer, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(Text, primary_key=True)
    firstName: Mapped[str] = mapped_column(Text, nullable=False)
    lastName: Mapped[str] = mapped_column(Text, nullable=False)
    phoneNumber: Mapped[str] = mapped_column(Text, nullable=False)
    availability: Mapped[str] = mapped_column(Text, nullable=False)


# Append-only ingestion log populated by `server.etl`. Every row a partner feed
# produces is staged here first, whether or not it ends up in `users` — that
# keeps ingestion auditable and lets the same file be re-ingested without
# losing the record of previous attempts.
class RawAvailabilityEvent(Base):
    __tablename__ = "raw_availability_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    first_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(Text, nullable=True)
    availability_raw: Mapped[str] = mapped_column(Text, nullable=False)
    raw_payload: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
