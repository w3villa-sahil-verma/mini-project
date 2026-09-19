from typing import Annotated;

from fastapi import Depends

from src.auth.strategies.StandardAuthStrategy import StandardAuthStrategy;

class AuthenticationService:
    def __init__(
        self, 
        strategy: Annotated[StandardAuthStrategy, Depends(StandardAuthStrategy)]
    ) -> None:
        self.strategy = strategy;
        pass

    async def authenticate(self, email:str, password:str):
        return await self.strategy.authenticate(email, password);

    def logout(self):
        pass