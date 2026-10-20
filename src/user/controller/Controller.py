
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.Database import getAsyncDbSession
from src.models.User import User


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
