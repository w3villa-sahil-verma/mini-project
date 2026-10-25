
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.Database import getAsyncDbSession
from src.models.User import User
from src.models.UserProfile import UserProfile


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

        return {
            "message": "Profile retrieved successfully",
            "data": self._serialize_profile(user, profile),
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

        return {
            "message": "Profile updated successfully",
            "data": self._serialize_profile(user, profile),
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

    @staticmethod
    def _serialize_profile(user: User, profile: UserProfile | None) -> dict:
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
