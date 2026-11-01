from typing import Annotated
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from src.models.User import User
from src.models.Credential import Credential
from src.common.token.JwtService import JwtTokenService
from src.common.token.constants import TOKEN_TYPES;
from src.common.security.HashingService import HashingService
from src.auth.services.AuthTokenService import AuthTokenService
from src.common.notification.NotificationService import NotificationService
from src.common.notification.Notification import Notification;
from src.core.settings import settings
from src.common.decorators.EmailCheck import check_email_exists
from src.auth.strategies.ABC_Registration import Registration;
from src.common.token.types import AuthTokens
from src.database.Database import getAsyncDbSession

class JwtBasedRegistration(Registration):
    def __init__(
            self,
            tokenService: Annotated[JwtTokenService, Depends(JwtTokenService)],
            db: Annotated[AsyncSession, Depends(getAsyncDbSession)],
            notification_service: Annotated[NotificationService, Depends(NotificationService)],
            auth_token_service: Annotated[
                AuthTokenService,
                Depends(AuthTokenService),
            ],
    ) -> None:
        self.tokenService = tokenService;
        self.db = db;
        self.notificationService = notification_service;
        self.auth_token_service = auth_token_service;

    @check_email_exists
    async def sendRegistrationLink(self, email: str):
    
            EXP_IN_MIN = 60
    
            # step 2: Create token
            tokenPayload = {
                "type": TOKEN_TYPES.REGISTRATION,
                "email": email,
                "exp": datetime.now(timezone.utc) + timedelta(minutes=EXP_IN_MIN),
                "iat": datetime.now(timezone.utc),
            }
    
            token = self.tokenService.sign(tokenPayload)
    
            # step 2: Send a verification email to the user with a unique registration link.
            await self.notificationService.send(Notification(
                recipient=email,
                subject="Image Gallery registration",
                body=(
                    f"{settings.FRONTEND_BASE_URL.rstrip('/')}"
                    f"/register?token={token}"
                ),
            ))
    
            return {
                "message" : "Mail sended Successfully"
            }

    # TODO : welcome notification AND seperate repository code
    async def register(
        self,
        email: str,
        password: str,
        token: str,
    ) -> AuthTokens:

        # verify the token
        try:
            payload = self.tokenService.verify(token=token)
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration link is invalid or has expired.",
            ) from error
        if (
            payload.get("type") != TOKEN_TYPES.REGISTRATION.value
            or payload.get("email") != email
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration link is invalid or has expired.",
            )

        # 2. Create everything inside ONE transaction
        async with self.db.begin():

            user = User(
                email=email,
            )

            self.db.add(user)

            # Flush so user.id becomes available
            await self.db.flush()

            credential = Credential(
                user_id=user.id,
                hash=HashingService.hash_password(password)
            )

            self.db.add(credential)

        # transaction commits automatically here

        return await self.auth_token_service.issue_auth_tokens(
            user.id,
            user.role.value,
        )