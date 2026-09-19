from typing import Annotated

from fastapi import Request, Depends;

from src.auth.strategies.StandardRegistration import StandardRegistration

class RegistrationService:
    def __init__(self, standardStrategy: Annotated[StandardRegistration, Depends(StandardRegistration)]) -> None:
        self.standardStrategy = standardStrategy;

    def standardRegister(self, email: str, password:str, token:str):
        return self.standardStrategy.register(email, password, token);

    def oauthRegister(self):
        pass;