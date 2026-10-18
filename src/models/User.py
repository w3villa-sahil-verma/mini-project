from datetime import datetime
from enum import Enum

from sqlalchemy import String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.database.Base import Base

# -------------------------
# Enums
# -------------------------

class USER_ROLE(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True,autoincrement=True)

    email: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        unique=True,
        index=True
    )

    role: Mapped[USER_ROLE] = mapped_column(
        SQLEnum(USER_ROLE, name="type"),
        nullable=False,
        default=USER_ROLE.USER
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self) -> str:
        return (
            f"User("
            f"id={self.id!r}, "
            f"email={self.email!r}, "
            f"created_at={self.created_at!r}, "
            f"updated_at={self.updated_at!r}"
            f")"
        )