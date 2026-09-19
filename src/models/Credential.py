from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLEnum, ForeignKey, Integer

from sqlalchemy.orm import Mapped, mapped_column

from src.database.Base import Base


# -------------------------
# Enums
# -------------------------

class CREDENTIAL_TYPES(str, Enum):
    STANDARD = "STANDARD"
    GOOGLE_OAUTH = "GOOGLE_OAUTH"

# -------------------------
# Credential Model
# -------------------------

class Credential(Base):
    __tablename__ = "credentials"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True,
    )

    hash: Mapped[str] = mapped_column(
        nullable=False,
    )

    type: Mapped[CREDENTIAL_TYPES] = mapped_column(
        SQLEnum(CREDENTIAL_TYPES, name="type"),
        nullable=False,
        default=CREDENTIAL_TYPES.STANDARD
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
            f"Credential("
            f"id={self.id!r}, "
            f"user_id={self.user_id!r}, "
            f"type={self.type!r}"
            f"hash={self.hash!r}, "
            f"created_at={self.created_at!r}, "
            f"updated_at={self.updated_at!r}"
            f")"
        )