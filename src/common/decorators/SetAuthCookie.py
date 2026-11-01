
from functools import wraps
from fastapi import Response

from src.core.settings import settings

from src.auth.services.AuthTokenService import (
    ACCESS_TOKEN_LIFETIME,
    REFRESH_TOKEN_LIFETIME,
)
from src.common.token.types import AuthTokens


def set_auth_cookies(response: Response, tokens: AuthTokens) -> None:
    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=settings.OAUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        max_age=int(ACCESS_TOKEN_LIFETIME.total_seconds()),
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=settings.OAUTH_COOKIE_SECURE,
        samesite=settings.AUTH_COOKIE_SAMESITE,
        max_age=int(REFRESH_TOKEN_LIFETIME.total_seconds()),
        path="/",
    )


def set_auth_cookie(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        response: Response = kwargs["response"]

        result = await func(*args, **kwargs)

        data = result.get("data", {})
        access_token = data.get("access_token")
        refresh_token = data.get("refresh_token")

        if access_token and refresh_token:
            set_auth_cookies(response, data)
            data.pop("refresh_token", None)

        return result

    return wrapper
