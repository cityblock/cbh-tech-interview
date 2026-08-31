from sqlalchemy import Text
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
