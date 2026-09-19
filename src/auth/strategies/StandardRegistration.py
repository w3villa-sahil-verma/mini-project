from typing import Annotated
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Request

from src.models.User import User
from src.models.Account import Account, EmailVerificationStatus
from src.models.Credential import Credential
from src.common.token.JwtService import JwtTokenService
from src.common.token.constants import TOKEN_TYPES;
from src.database.Database import getAsyncDbSession
from src.common.security.HashingService import HashingService


class StandardRegistration:
    def __init__(
            self,
            tokenService: Annotated[JwtTokenService, Depends(JwtTokenService)],
            db: Annotated[AsyncSession, Depends(getAsyncDbSession)]

    ) -> None:
        self.tokenService = tokenService;
        self.db = db;

    async def register(self, email:str, password:str, token:str):

        # verify the token
        payload = self.tokenService.verify(token=token)

        # 2. Create everything inside ONE transaction
        async with self.db.begin():

            user = User(
                email=email,
            )

            self.db.add(user)

            # Flush so user.id becomes available
            await self.db.flush()

            account = Account(
                user_id=user.id,
                email_verification_status=EmailVerificationStatus.VERIFIED
            )

            credential = Credential(
                user_id=user.id,
                hash=HashingService.hash_password(password)
            )

            self.db.add(account)
            self.db.add(credential)

        # transaction commits automatically here


        # Generate access token after successful commit
        EXP_IN_MIN = 24 * 60 # 1 day

        accessTokenPayload = {
            "user_id": user.id,
            "type": TOKEN_TYPES.ACCESS,
            "exp": datetime.now(timezone.utc) + timedelta(minutes=EXP_IN_MIN),
            "iat": datetime.now(timezone.utc),
        }
        access_token = self.tokenService.sign(payload=accessTokenPayload)

        return {
            "access_token": access_token,
        }