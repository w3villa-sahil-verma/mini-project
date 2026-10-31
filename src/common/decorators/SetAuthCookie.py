
from functools import wraps
from fastapi import Response

from src.core.settings import settings


def set_auth_cookie(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        response: Response = kwargs["response"]

        result = await func(*args, **kwargs)

        access_token = result.get("data", {}).get("access_token")

        if access_token:
            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=settings.OAUTH_COOKIE_SECURE,
                samesite=settings.AUTH_COOKIE_SAMESITE,
                max_age=24 * 60 * 60,
                path="/",
            )

        return result

    return wrapper
