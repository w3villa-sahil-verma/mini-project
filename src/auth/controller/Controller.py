from typing import Annotated
from fastapi import Depends, HTTPException, Response, status;

from src.auth.services.RegistrationService import RegistrationService
from src.auth.services.AuthenticationService import AuthenticationService;
from src.auth.services.AuthTokenService import AuthTokenService
from src.auth.services.PasswordResetService import PasswordResetService
from src.common.decorators.SetAuthCookie import set_auth_cookie
from src.core.settings import settings


class AuthController:
    def __init__(
            self, 
            registrationService: Annotated[RegistrationService, Depends(RegistrationService)],
            authService: Annotated[AuthenticationService, Depends(AuthenticationService)],
            auth_token_service: Annotated[
                AuthTokenService,
                Depends(AuthTokenService),
            ],
            password_reset_service: Annotated[
                PasswordResetService,
                Depends(PasswordResetService),
            ],
        ):
        self.registrationService = registrationService;
        self.authService = authService;
        self.auth_token_service = auth_token_service
        self.password_reset_service = password_reset_service
        

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
            "data" : result
        }

    @set_auth_cookie
    async def refresh(self, refresh_token: str | None, response: Response):
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Your session has expired. Please sign in again.",
            )

        result = await self.auth_token_service.rotate_refresh_token(refresh_token)
        return {
            "message": "Session refreshed successfully",
            "data": result,
        }

    async def requestPasswordReset(self, email: str):
        await self.password_reset_service.request_reset(email)
        return {
            "message": "Password reset email sent successfully.",
            "data": None,
        }

    async def validatePasswordReset(self, token: str):
        await self.password_reset_service.validate_reset_token(token)
        return {
            "message": "Password reset link is valid.",
            "data": None,
        }

    async def resetPassword(self, token: str, password: str):
        await self.password_reset_service.reset_password(token, password)
        return {
            "message": "Password updated successfully.",
            "data": None,
        }

    async def logout(self, response: Response, refresh_token: str | None):
        await self.auth_token_service.revoke_refresh_token(refresh_token)

        # remove accesstoken from http-only-cookie
        for cookie_name in ("access_token", "refresh_token"):
            response.delete_cookie(
                key=cookie_name,
                httponly=True,
                secure=settings.OAUTH_COOKIE_SECURE,
                samesite=settings.AUTH_COOKIE_SAMESITE,
                path="/",
            )

        return {
            "message": "Logout Successfull",
            "data": None
        };
        
