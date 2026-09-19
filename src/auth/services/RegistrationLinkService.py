from fastapi import Depends
from typing import Annotated

from src.auth.strategies.JwtRegistrationLinkStrategy import JwtRegistrationLinkService

class RegistrationLinkService:
    def __init__(
            self, 
            strategy: Annotated[JwtRegistrationLinkService, Depends(JwtRegistrationLinkService)]
        ):
        self.strategy = strategy;

    async def create_registration_link(self, email: str):
        return self.strategy.create_registration_link(email);

        

