from typing import Annotated

from fastapi import Depends;

from src.auth.strategies.ABC_Registration import Registration;
from src.common.token.types import AuthTokens
from src.auth.strategies.JwtBasedRegistration import JwtBasedRegistration;

class RegistrationService:
    def __init__(
        self, 
        strategy: Annotated[Registration, Depends(JwtBasedRegistration)]
    ) -> None:
        self.strategy = strategy;

    async def register(
        self,
        email: str,
        password: str,
        token: str,
    ) -> AuthTokens:
        return await self.strategy.register(email, password, token);

    async def sendRegistrationLink(self, email: str):
        return await self.strategy.sendRegistrationLink(email);