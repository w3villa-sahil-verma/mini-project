from typing import Annotated
from datetime import datetime, timedelta, timezone

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.security.HashingService import HashingService
from src.common.token.JwtService import JwtTokenService
from src.common.token.constants import TOKEN_TYPES
from src.models.User import User
from src.models.Credential import Credential
from src.auth.strategies.ABC_AuthStrategy import AuthStrategy;
from src.database.Database import getAsyncDbSession

class StandardAuthStrategy(AuthStrategy):
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(getAsyncDbSession)],
        tokenService: Annotated[JwtTokenService, Depends(JwtTokenService)],
    ):
        self.db = db
        self.tokenService = tokenService

    async def authenticate(self, email: str, password: str):

        # 1. Get user by email
        result = await self.db.execute(
            select(User).where(User.email == email)
        )

        user = result.scalar_one_or_none()

        if user is None:
            raise ValueError("Invalid email or password")

        # 2. Get credential by user.id
        result = await self.db.execute(
            select(Credential).where(Credential.user_id == user.id)
        )

        credential = result.scalar_one_or_none()

        if credential is None:
            raise ValueError("Invalid email or password")

        # 3. Verify password
        password_valid = HashingService.verify_password(
            password,
            hashed_password=credential.hash,
        )

        if not password_valid:
            raise ValueError("Invalid email or password")

        # 4. Create access token
        now = datetime.now(timezone.utc)

        EXP_IN_MIN = 24 * 60  # 1 day

        accessTokenPayload = {
            "user_id": user.id,
            "type": TOKEN_TYPES.ACCESS,
            "exp": now + timedelta(minutes=EXP_IN_MIN),
            "iat": now,
        }

        access_token = self.tokenService.sign(
            payload=accessTokenPayload
        )

        # 5. Send access token
        return access_token

    async def logout(self):
        # TODO
        # JWT access tokens are stateless.
        #
        # If you want real server-side logout, you need to revoke
        # the token (for example, store its `jti` in a blacklist).
        #
        # Without token revocation, logout is normally handled
        # by deleting the token on the client.
        pass;
