from typing import Annotated
from fastapi import Depends, Request, Response;

from src.auth.services.RegistrationService import RegistrationService
from src.auth.services.AuthenticationService import AuthenticationService;

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
            "message" : "success",
            "data" : result
        }

    async def standardRegister(self, email: str, password:str, token:str):

        result = await self.registrationService.register(email, password, token);

        return {
            "message" : "success",
            "data" : result
        }

    async def login(self, email: str, password:str, response: Response):

        result = await self.authService.authenticate(email, password);

        # TODO : http-only-cookie
        # set access_token in cookie
        response.set_cookie(key="access_token", value=result)

        return {
            "message" : "success",
            "data" : {
                "access_token": result
            }
        }

    async def oauthLogin(self, accessToken: str):

        result = self.authService.oauthAuthenticate(accessToken=accessToken)

        # Backend's Acces Token
        return {
            "message" : "success",
            "data" : result
        }

    async def getOauthMeta(self):

        result = await self.authService.getOauthMeta();

        # CLIENT_ID + REDIRECT_URL + SCOPE
        return {
            "message" : "success",
            "data" : result
        }
    
    async def logout(self):

        # remove accesstoken from http-only-cookie

        pass;
        
