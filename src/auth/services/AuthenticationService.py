from typing import Annotated;

from fastapi import Depends;

from src.auth.strategies.StandardAuthStrategy import StandardAuthStrategy;
from src.auth.strategies.ABC_AuthStrategy import AuthStrategy;

class AuthenticationService:
    def __init__(
        self, 
        strategy: Annotated[AuthStrategy, Depends(StandardAuthStrategy)],
    ) -> None:
        self.strategy = strategy;

    # Standard authentication
    async def authenticate(self, email:str, password:str):
        return await self.strategy.authenticate(email, password);

    def logout(self):
        pass