
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.Database import getAsyncDbSession
from src.models.User import User
from src.models.UserProfile import UserProfile
from src.models.Plan import Plan
from src.models.Subscription import Subscription


class ProfileUpdate(BaseModel):
    full_name: str = Field(min_length=1, max_length=401)
    email: str = Field(
        min_length=3,
        max_length=30,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    phone: str | None = Field(max_length=30)
    street: str | None = Field(max_length=255)
    city: str | None = Field(max_length=100)
    state: str | None = Field(max_length=100)
    postal_code: str | None = Field(max_length=20)
    country: str | None = Field(max_length=100)
    latitude: float | None = Field(ge=-90, le=90)
    longitude: float | None = Field(ge=-180, le=180)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, full_name: str) -> str:
        parts = full_name.strip().split(maxsplit=1)
        if not parts or any(len(part) > 200 for part in parts):
            raise ValueError("Name parts must be no longer than 200 characters")
        return " ".join(parts)

    @model_validator(mode="after")
    def validate_coordinates(self) -> "ProfileUpdate":
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("Latitude and longitude must be supplied together")
        return self


class UserController:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(getAsyncDbSession)],
    ):
        self.db = db

    async def get_all(self):
        result = await self.db.scalars(
            select(User).order_by(User.id.desc())
        )

        users = result.all()

        return {
            "message": "Users retrieved successfully",
            "data": [self._serialize(user) for user in users],
        }

    async def get(self, plan_id: int):
        user = await self.db.get(User, plan_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return {
            "message": "User retrieved successfully",
            "data": self._serialize(user),
        }

    async def soft_delete(self, plan_id: int):
        user = await self.db.get(User, plan_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user.is_deleted = True
        user.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(user)

        return {
            "message": "User deleted successfully",
            "data": self._serialize(user),
        }

    async def get_profile(self, user_id: int):
        user = await self._get_active_user(user_id)
        profile = await self._get_user_profile(user_id)
        membership = await self._get_membership_summary(user_id)

        return {
            "message": "Profile retrieved successfully",
            "data": self._serialize_profile(user, profile, membership),
        }

    async def update_profile(self, user_id: int, payload: ProfileUpdate):
        user = await self._get_active_user(user_id)
        email = payload.email.strip()

        existing_user = await self.db.scalar(
            select(User).where(User.email == email, User.id != user_id)
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email address is already in use",
            )

        profile = await self._get_user_profile(user_id)
        first_name, _, last_name = payload.full_name.partition(" ")

        if profile is None:
            profile = UserProfile(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
            )
            self.db.add(profile)
        else:
            profile.first_name = first_name
            profile.last_name = last_name

        user.email = email
        profile.phone = payload.phone or None
        profile.street = payload.street or None
        profile.city = payload.city or None
        profile.state = payload.state or None
        profile.postal_code = payload.postal_code or None
        profile.country = payload.country or None
        profile.latitude = payload.latitude
        profile.longitude = payload.longitude

        try:
            await self.db.commit()
        except IntegrityError as error:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Profile data conflicts with an existing record",
            ) from error

        await self.db.refresh(user)
        await self.db.refresh(profile)
        membership = await self._get_membership_summary(user_id)

        return {
            "message": "Profile updated successfully",
            "data": self._serialize_profile(user, profile, membership),
        }

    async def _get_active_user(self, user_id: int) -> User:
        user = await self.db.get(User, user_id)
        if user is None or user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    async def _get_user_profile(self, user_id: int) -> UserProfile | None:
        return await self.db.scalar(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )

    async def _get_membership_summary(self, user_id: int) -> dict | None:
        now = datetime.now(timezone.utc)
        membership_query = (
            select(Subscription, Plan.name)
            .join(Plan, Plan.id == Subscription.plan_id)
            .where(Subscription.user_id == user_id)
        )

        current_membership = (
            await self.db.execute(
                membership_query.where(
                    Subscription.status == "ACTIVE",
                    Subscription.starts_at <= now,
                    Subscription.expires_at > now,
                )
                .order_by(Subscription.expires_at.desc())
                .limit(1)
            )
        ).first()

        if current_membership is not None:
            subscription, plan_name = current_membership
            status = "ACTIVE"
        else:
            current_membership = (
                await self.db.execute(
                    membership_query.where(
                        Subscription.status == "SCHEDULED",
                        Subscription.starts_at > now,
                        Subscription.expires_at > now,
                    )
                    .order_by(Subscription.starts_at.asc())
                    .limit(1)
                )
            ).first()
            if current_membership is not None:
                subscription, plan_name = current_membership
                status = "SCHEDULED"
            else:
                current_membership = (
                    await self.db.execute(
                        membership_query.where(
                            or_(
                                Subscription.status == "EXPIRED",
                                and_(
                                    Subscription.status.in_(("ACTIVE", "SCHEDULED")),
                                    Subscription.expires_at <= now,
                                ),
                            )
                        )
                        .order_by(Subscription.expires_at.desc())
                        .limit(1)
                    )
                ).first()
                if current_membership is None:
                    return None
                subscription, plan_name = current_membership
                status = "EXPIRED"

        return {
            "plan_name": plan_name,
            "status": status,
            "starts_at": subscription.starts_at,
            "expires_at": subscription.expires_at,
            "has_premium_access": status == "ACTIVE",
        }

    @staticmethod
    def _serialize_profile(
        user: User,
        profile: UserProfile | None,
        membership: dict | None,
    ) -> dict:
        return {
            "full_name": " ".join(
                part
                for part in (
                    profile.first_name if profile else "",
                    profile.last_name if profile else "",
                )
                if part
            ),
            "email": user.email,
            "phone": profile.phone if profile else None,
            "street": profile.street if profile else None,
            "city": profile.city if profile else None,
            "state": profile.state if profile else None,
            "postal_code": profile.postal_code if profile else None,
            "country": profile.country if profile else None,
            "latitude": profile.latitude if profile else None,
            "longitude": profile.longitude if profile else None,
            "membership": membership,
        }

    @staticmethod
    def _serialize(user: User) -> dict:
        return {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "is_deleted": user.is_deleted,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }
