from fastapi import Depends
from typing import Annotated
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.notification.NotificationService import NotificationService
from src.common.notification.Notification import Notification;
from src.common.token.JwtService import JwtTokenService;
from src.common.token.constants import TOKEN_TYPES;
from src.database.Database import getAsyncDbSession


class JwtRegistrationLinkService:
    def __init__(
            self, 
            notification_service: Annotated[NotificationService, Depends(NotificationService)],
            tokenService: Annotated[JwtTokenService, Depends(JwtTokenService)],
            session: Annotated[AsyncSession, Depends(getAsyncDbSession)]
        ):
        self.notificationService = notification_service;
        self.tokenService = tokenService;
        self.session = session;

    async def create_registration_link(self, email: str):

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
            subject="GYM Registration mail",
            body=f"http://abc.com?email={email}&code={token}"
        ))

        return {
            "message" : "Mail sended Successfully"
        }

        

