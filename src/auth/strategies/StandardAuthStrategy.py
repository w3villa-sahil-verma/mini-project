from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.services.AuthTokenService import AuthTokenService
from src.common.security.HashingService import HashingService
from src.common.token.types import AuthTokens
from src.models.User import User
from src.models.Credential import Credential
from src.auth.strategies.ABC_AuthStrategy import AuthStrategy;
from src.database.Database import getAsyncDbSession

class StandardAuthStrategy(AuthStrategy):
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(getAsyncDbSession)],
        auth_token_service: Annotated[
            AuthTokenService,
            Depends(AuthTokenService),
        ],
    ):
        self.db = db
        self.auth_token_service = auth_token_service

    async def authenticate(self, email: str, password: str) -> AuthTokens:

        # 1. Get user by email
        result = await self.db.execute(
            select(User).where(User.email == email)
        )

        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # 2. Get credential by user.id
        result = await self.db.execute(
            select(Credential).where(Credential.user_id == user.id)
        )

        credential = result.scalar_one_or_none()

        if credential is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # 3. Verify password
        password_valid = HashingService.verify_password(
            password,
            hashed_password=credential.hash,
        )

        if not password_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return await self.auth_token_service.issue_auth_tokens(
            user.id,
            user.role.value,
        )

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
