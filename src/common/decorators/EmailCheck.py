
from functools import wraps
from fastapi import HTTPException, status
from sqlalchemy import select

from src.models.User import User


def check_email_exists(func):
    @wraps(func)
    async def wrapper(self, email: str, *args, **kwargs):
        result = await self.db.execute(
            select(User.id).where(User.email == email)
        )

        existing_user = result.scalar_one_or_none()

        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists",
            )

        return await func(self, email, *args, **kwargs)

    return wrapper
