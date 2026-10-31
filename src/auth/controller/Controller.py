from typing import Annotated
from fastapi import Depends, Request, Response;

from src.auth.services.RegistrationService import RegistrationService
from src.auth.services.AuthenticationService import AuthenticationService;
from src.common.decorators.SetAuthCookie import set_auth_cookie


class AuthController:
    def __init__(
            self, 
            registrationService: Annotated[RegistrationService, Depends(RegistrationService)],
            authService: Annotated[AuthenticationService, Depends(AuthenticationService)]
        ):
        self.registrationService = registrationService;
        self.authService = authService;
        

    async def getRegistrationMail(self, email:str):
        
        result =  await self.registrationService.sendRegistrationLink(email);

        return {
            "message" : f"Mail successfully send at {email}",
            "data" : result
        }

    @set_auth_cookie
    async def standardRegister(self, email: str, password:str, token:str, response: Response): # response used by decorator

        result = await self.registrationService.register(email, password, token);

        return {
            "message" : "User Registration Successful",
            "data" : result
        }
    
    @set_auth_cookie
    async def login(self, email: str, password:str, response: Response):

        result = await self.authService.authenticate(email, password);

        return {
            "message" : "User Login Successful",
            "data" : {
                "access_token": result
            }
        }

    async def logout(self, response: Response):

        # remove accesstoken from http-only-cookie
        response.delete_cookie(
            key="access_token",
            httponly=True,
            secure=True,
            samesite="lax",
            path="/",
        )

        return {
            "message": "Logout Successfull",
            "data": None
        };
        
