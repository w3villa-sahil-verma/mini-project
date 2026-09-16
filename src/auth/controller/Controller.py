from typing import Annotated
from fastapi import Depends;

from src.auth.services.RegistrationLinkService import RegistrationLinkService


class AuthController:
    def __init__(self, registrationLinkService: Annotated[RegistrationLinkService, Depends(RegistrationLinkService)]):
        self.registrationLinkService = registrationLinkService;
        

    async def getRegistrationMail(self, email:str):
        
        result =  await self.registrationLinkService.create_registration_link(email)

        return {
            "message" : "success",
            "data" : result
        }
        
