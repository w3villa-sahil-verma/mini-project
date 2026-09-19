from typing import Annotated
from fastapi import Depends, Request;

from src.auth.services.RegistrationLinkService import RegistrationLinkService
from src.auth.services.RegistrationService import RegistrationService

class AuthController:
    def __init__(
            self, 
            registrationLinkService: Annotated[RegistrationLinkService, Depends(RegistrationLinkService)],
            registrationService: Annotated[RegistrationService, Depends(RegistrationService)]
        ):
        self.registrationLinkService = registrationLinkService;
        self.registrationService = registrationService;
        

    async def getRegistrationMail(self, email:str):
        
        result =  await self.registrationLinkService.create_registration_link(email)

        return {
            "message" : "success",
            "data" : result
        }

    async def standardRegister(self, email: str, password:str, token:str):

        result = await self.registrationService.standardRegister(email, password, token);

        return {
            "message" : "success",
            "data" : result
        }

    async def oauthRegister(self, request: Request):

        result = self.registrationService.oauthRegister()

        return {
            "message" : "success",
            "data" : result
        }
        
