from typing import Annotated

from fastapi import Request, Depends;

from src.auth.strategies.ABC_Registration import Registration;
from src.auth.strategies.JwtBasedRegistration import JwtBasedRegistration;

class RegistrationService:
    def __init__(
        self, 
        strategy: Annotated[Registration, Depends(JwtBasedRegistration)]
    ) -> None:
        self.strategy = strategy;

    def register(self, email: str, password:str, token:str):
        return self.strategy.register(email, password, token);

    def sendRegistrationLink(self, email: str):
        return self.strategy.sendRegistrationLink(email);