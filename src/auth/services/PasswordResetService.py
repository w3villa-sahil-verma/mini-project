import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.notification.Notification import Notification
from src.common.notification.NotificationService import NotificationService
from src.common.security.HashingService import HashingService
from src.common.token.constants import TOKEN_TYPES
from src.common.token.JwtService import JwtTokenService
from src.core.settings import settings
from src.database.Database import getAsyncDbSession
from src.models.AuthToken import AuthToken
from src.models.Credential import Credential
from src.models.User import User

PASSWORD_RESET_TOKEN_LIFETIME = timedelta(minutes=30)
INVALID_RESET_TOKEN_MESSAGE = (
    "This password reset link is invalid or has expired. Request a new one."
)


class PasswordResetService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(getAsyncDbSession)],
        token_service: Annotated[JwtTokenService, Depends(JwtTokenService)],
        notification_service: Annotated[
            NotificationService,
            Depends(NotificationService),
        ],
    ) -> None:
        self.db = db
        self.token_service = token_service
        self.notification_service = notification_service

    async def request_reset(self, email: str) -> None:
        user = await self.db.scalar(
            select(User).where(
                User.email == email,
                User.is_deleted.is_(False),
            )
        )
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No account is registered with this email address.",
            )

        now = datetime.now(timezone.utc)
        await self.db.execute(
            update(AuthToken)
            .where(
                AuthToken.user_id == user.id,
                AuthToken.token_type == TOKEN_TYPES.PASSWORD_RESET.value,
                AuthToken.used_at.is_(None),
            )
            .values(used_at=now)
        )

        jti = secrets.token_urlsafe(32)
        expires_at = now + PASSWORD_RESET_TOKEN_LIFETIME
        token = self.token_service.sign(
            {
                "user_id": user.id,
                "email": user.email,
                "type": TOKEN_TYPES.PASSWORD_RESET.value,
                "jti": jti,
                "exp": expires_at,
                "iat": now,
            }
        )
        self.db.add(
            AuthToken(
                jti=jti,
                user_id=user.id,
                token_type=TOKEN_TYPES.PASSWORD_RESET.value,
                expires_at=expires_at,
            )
        )
        await self.db.commit()

        reset_url = (
            f"{settings.FRONTEND_BASE_URL.rstrip('/')}"
            f"/reset-password?token={token}"
        )
        await self.notification_service.send(
            Notification(
                recipient=user.email,
                subject="Reset your Image Gallery password",
                body=(
                    "We received a request to reset your Image Gallery "
                    f"password. Open this link to continue: {reset_url}\n\n"
                    "This link expires in 30 minutes. If you did not request "
                    "a reset, you can ignore this email."
                ),
                html_body=(
                    "<p>We received a request to reset your Image Gallery "
                    "password.</p>"
                    f'<p><a href="{reset_url}">Choose a new password</a></p>'
                    "<p>This link expires in 30 minutes. If you did not "
                    "request a reset, you can ignore this email.</p>"
                ),
            )
        )

    async def validate_reset_token(self, token: str) -> None:
        payload = self._decode_reset_token(token)
        stored_token = await self._find_stored_token(payload)
        if stored_token is None or stored_token.used_at is not None:
            raise self._invalid_reset_token()

        user = await self.db.scalar(
            select(User).where(
                User.id == payload["user_id"],
                User.is_deleted.is_(False),
            )
        )
        if user is None:
            raise self._invalid_reset_token()

    async def reset_password(self, token: str, password: str) -> None:
        payload = self._decode_reset_token(token)
        stored_token = await self._find_stored_token(payload, lock=True)
        if stored_token is None or stored_token.used_at is not None:
            raise self._invalid_reset_token()

        user = await self.db.scalar(
            select(User).where(
                User.id == payload["user_id"],
                User.is_deleted.is_(False),
            )
        )
        if user is None:
            raise self._invalid_reset_token()

        credential = await self.db.scalar(
            select(Credential)
            .where(Credential.user_id == user.id)
            .with_for_update()
        )
        hashed_password = HashingService.hash_password(password)
        if credential is None:
            self.db.add(Credential(user_id=user.id, hash=hashed_password))
        else:
            credential.hash = hashed_password

        now = datetime.now(timezone.utc)
        stored_token.used_at = now
        await self.db.execute(
            update(AuthToken)
            .where(
                AuthToken.user_id == user.id,
                AuthToken.token_type == TOKEN_TYPES.REFRESH.value,
                AuthToken.used_at.is_(None),
            )
            .values(used_at=now)
        )
        await self.db.commit()

    def _decode_reset_token(self, token: str) -> dict:
        try:
            payload = self.token_service.verify(token)
        except ValueError as error:
            raise self._invalid_reset_token() from error

        if (
            payload.get("type") != TOKEN_TYPES.PASSWORD_RESET.value
            or not isinstance(payload.get("user_id"), int)
            or not isinstance(payload.get("jti"), str)
        ):
            raise self._invalid_reset_token()
        return payload

    async def _find_stored_token(
        self,
        payload: dict,
        *,
        lock: bool = False,
    ) -> AuthToken | None:
        query = select(AuthToken).where(
            AuthToken.jti == payload["jti"],
            AuthToken.user_id == payload["user_id"],
            AuthToken.token_type == TOKEN_TYPES.PASSWORD_RESET.value,
        )
        if lock:
            query = query.with_for_update()
        return await self.db.scalar(query)

    @staticmethod
    def _invalid_reset_token() -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_RESET_TOKEN_MESSAGE,
        )
