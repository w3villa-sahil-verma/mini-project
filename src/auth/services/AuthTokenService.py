import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.token.constants import TOKEN_TYPES
from src.common.token.JwtService import JwtTokenService
from src.common.token.types import AuthTokens
from src.database.Database import getAsyncDbSession
from src.models.AuthToken import AuthToken
from src.models.User import User

ACCESS_TOKEN_LIFETIME = timedelta(days=1)
REFRESH_TOKEN_LIFETIME = timedelta(days=30)


class AuthTokenService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(getAsyncDbSession)],
        token_service: Annotated[JwtTokenService, Depends(JwtTokenService)],
    ) -> None:
        self.db = db
        self.token_service = token_service

    async def issue_auth_tokens(self, user_id: int, role: str) -> AuthTokens:
        tokens = self._create_auth_tokens(user_id, role)
        await self.db.commit()
        return tokens

    async def rotate_refresh_token(self, token: str) -> AuthTokens:
        payload = self._verify_token(token, TOKEN_TYPES.REFRESH)
        user_id = payload.get("user_id")
        jti = payload.get("jti")
        if not isinstance(user_id, int) or not isinstance(jti, str):
            raise self._invalid_refresh_token()

        stored_token = await self.db.scalar(
            select(AuthToken)
            .where(
                AuthToken.jti == jti,
                AuthToken.user_id == user_id,
                AuthToken.token_type == TOKEN_TYPES.REFRESH.value,
            )
            .with_for_update()
        )
        if stored_token is None:
            raise self._invalid_refresh_token()

        if stored_token.used_at is not None:
            raise self._invalid_refresh_token()

        user = await self.db.scalar(
            select(User).where(
                User.id == user_id,
                User.is_deleted.is_(False),
            )
        )
        if user is None:
            stored_token.used_at = datetime.now(timezone.utc)
            await self.db.commit()
            raise self._invalid_refresh_token()

        stored_token.used_at = datetime.now(timezone.utc)
        tokens = self._create_auth_tokens(user.id, user.role.value)
        await self.db.commit()
        return tokens

    async def revoke_refresh_token(self, token: str | None) -> None:
        if not token:
            return

        try:
            payload = self._verify_token(token, TOKEN_TYPES.REFRESH)
        except HTTPException:
            return

        jti = payload.get("jti")
        user_id = payload.get("user_id")
        if not isinstance(jti, str) or not isinstance(user_id, int):
            return

        stored_token = await self.db.scalar(
            select(AuthToken).where(
                AuthToken.jti == jti,
                AuthToken.user_id == user_id,
                AuthToken.token_type == TOKEN_TYPES.REFRESH.value,
                AuthToken.used_at.is_(None),
            )
        )
        if stored_token is not None:
            stored_token.used_at = datetime.now(timezone.utc)
            await self.db.commit()

    def _create_auth_tokens(self, user_id: int, role: str) -> AuthTokens:
        now = datetime.now(timezone.utc)
        refresh_jti = secrets.token_urlsafe(32)
        access_token = self.token_service.sign(
            {
                "user_id": user_id,
                "role": role,
                "type": TOKEN_TYPES.ACCESS.value,
                "exp": now + ACCESS_TOKEN_LIFETIME,
                "iat": now,
            }
        )
        refresh_token = self.token_service.sign(
            {
                "user_id": user_id,
                "role": role,
                "type": TOKEN_TYPES.REFRESH.value,
                "jti": refresh_jti,
                "exp": now + REFRESH_TOKEN_LIFETIME,
                "iat": now,
            }
        )
        self.db.add(
            AuthToken(
                jti=refresh_jti,
                user_id=user_id,
                token_type=TOKEN_TYPES.REFRESH.value,
                expires_at=now + REFRESH_TOKEN_LIFETIME,
            )
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    def _verify_token(self, token: str, expected_type: TOKEN_TYPES) -> dict:
        try:
            payload = self.token_service.verify(token)
        except ValueError as error:
            raise self._invalid_refresh_token() from error

        if payload.get("type") != expected_type.value:
            raise self._invalid_refresh_token()
        return payload

    @staticmethod
    def _invalid_refresh_token() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session has expired. Please sign in again.",
        )
