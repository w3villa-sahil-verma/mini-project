from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Float
from sqlalchemy import Enum as SQLEnum, ForeignKey, Integer, String

from sqlalchemy.orm import Mapped, mapped_column

from src.database.Base import Base

# -------------------------
# Enums
# -------------------------

class GENDER(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"

# -------------------------
# UserProfile Model
# -------------------------

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(200)
    )

    last_name: Mapped[str] = mapped_column(
        String(200)
    )

    data_of_birth: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    gender: Mapped[GENDER | None] = mapped_column(
        SQLEnum(
            GENDER,
            name="gender",
        ),
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    street: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    postal_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return (
            f"UserProfile("
            f"id={self.id!r}, "
            f"user_id={self.user_id!r}, "
            f"first_name={self.first_name!r}, "
            f"last_name={self.last_name!r}, "
            f"data_of_birth={self.data_of_birth!r}, "
            f"gender={self.gender!r}, "
            f"phone={self.phone!r}, "
            f"street={self.street!r}, "
            f"city={self.city!r}, "
            f"state={self.state!r}, "
            f"postal_code={self.postal_code!r}, "
            f"country={self.country!r}, "
            f"latitude={self.latitude!r}, "
            f"longitude={self.longitude!r}, "
            f"created_at={self.created_at!r}, "
            f"updated_at={self.updated_at!r}"
            f")"
        )