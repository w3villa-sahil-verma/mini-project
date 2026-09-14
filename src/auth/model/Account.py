from datetime import datetime
from enum import Enum

from sqlalchemy import String, DateTime
from sqlalchemy import Enum as SQLEnum, ForeignKey, Integer

from sqlalchemy.orm import Mapped, mapped_column

from src.database.Base import Base
from src.auth.model.VerificationStatus import EmailVerificationStatus


# -------------------------
# Enums
# -------------------------

class AccountType(str, Enum):
    BASIC = "BASIC"
    SILVER = "SILVER"
    GOLD = "GOLD"


class CredentialType(str, Enum):
    STANDARD = "STANDARD"
    GOOGLE_OAUTH = "GOOGLE_OAUTH"


# -------------------------
# Account Model
# -------------------------

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("users.id"),
        nullable=False,
        unique=True,
    )

    type: Mapped[AccountType] = mapped_column(
        SQLEnum(AccountType, name="account_type"),
        nullable=False,
        default=AccountType.BASIC,
    )

    email_verification_status: Mapped[EmailVerificationStatus] = mapped_column(
        SQLEnum(
            EmailVerificationStatus,
            name="email_verification_status",
        ),
        nullable=False,
        default=EmailVerificationStatus.PENDING,
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
            f"Account("
            f"id={self.id!r}, "
            f"user_id={self.user_id!r}, "
            f"type={self.type!r}, "
            f"email_verification_status={self.email_verification_status!r}, "
            f"created_at={self.created_at!r}, "
            f"updated_at={self.updated_at!r}"
            f")"
        )