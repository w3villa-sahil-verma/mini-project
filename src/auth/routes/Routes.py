from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from typing import Annotated
from typing import Literal
from pydantic import BaseModel, Field

from src.auth.controller.Controller import AuthController
from src.auth.services.OAuthService import OAuthService
from src.core.settings import settings
from src.middlewares.authorization import require_access_token
from src.user.controller.Controller import UserController


class RequestBody(BaseModel):
    email: str
    password: str
    token: str

class StandardLoginRequestBody(BaseModel):
    email: str
    password: str

class PasswordResetRequestBody(BaseModel):
    email: str

class PasswordResetBody(BaseModel):
    token: str
    password: str = Field(min_length=8)

def getRouter()->APIRouter:

    router: APIRouter = APIRouter(
        prefix="/auth",
        tags=["Auth"],
        responses={404: {"description": "Not found"}},
    )

    @router.get("/registeration-mail")
    async def getRegistrationMail(
        authController: Annotated[AuthController, Depends(AuthController)],
        email: str
    ):
        return await authController.getRegistrationMail(email);

    @router.post("/standard/register")
    async def standardRegister(
        response: Response,
        authController: Annotated[AuthController, Depends(AuthController)],
        data: RequestBody
    ):
        return await authController.standardRegister(email=data.email, password=data.password, token=data.token, response=response);

    @router.post("/standard/login")
    async def standardLogin(
        authController: Annotated[AuthController, Depends(AuthController)],
        body: StandardLoginRequestBody,
        response: Response
    ):
        return await authController.login(email=body.email, password=body.password, response=response);

    @router.post("/refresh")
    async def refresh(
        request: Request,
        response: Response,
        auth_controller: Annotated[AuthController, Depends(AuthController)],
    ):
        verify_cookie_request_origin(request)
        return await auth_controller.refresh(
            refresh_token=request.cookies.get("refresh_token"),
            response=response,
        )

    @router.post("/password-reset/request")
    async def requestPasswordReset(
        body: PasswordResetRequestBody,
        auth_controller: Annotated[AuthController, Depends(AuthController)],
    ):
        return await auth_controller.requestPasswordReset(body.email)

    @router.get("/password-reset/validate")
    async def validatePasswordReset(
        token: str,
        auth_controller: Annotated[AuthController, Depends(AuthController)],
    ):
        return await auth_controller.validatePasswordReset(token)

    @router.post("/password-reset/confirm")
    async def resetPassword(
        body: PasswordResetBody,
        auth_controller: Annotated[AuthController, Depends(AuthController)],
    ):
        return await auth_controller.resetPassword(body.token, body.password)

    @router.get("/oauth/meta")
    async def oauthMeta(
        oauth_service: Annotated[OAuthService, Depends(OAuthService)],
    ):
        return oauth_service.get_meta()

    @router.get("/oauth/{provider}")
    async def oauthStart(
        provider: Literal["google", "facebook"],
        oauth_service: Annotated[OAuthService, Depends(OAuthService)],
    ):
        return oauth_service.start(provider)

    @router.get("/oauth/{provider}/callback")
    async def oauthCallback(
        provider: Literal["google", "facebook"],
        request: Request,
        oauth_service: Annotated[OAuthService, Depends(OAuthService)],
        code: str | None = None,
        state: str | None = None,
        error: str | None = None,
    ):
        return await oauth_service.callback(
            provider,
            code=code,
            state=state,
            stored_state=request.cookies.get(f"oauth_state_{provider}"),
            provider_error=error,
        )

    @router.post("/logout")
    async def logout(
        request: Request,
        response: Response,
        authController: Annotated[AuthController, Depends(AuthController)],
    ):
        verify_cookie_request_origin(request)
        return await authController.logout(
            response=response,
            refresh_token=request.cookies.get("refresh_token"),
        );

    @router.get("/me")
    async def me(
        me: Annotated[dict, Depends(require_access_token)],
        user_controller: Annotated[UserController, Depends(UserController)],
    ):
        identity = await user_controller.get_auth_identity(int(me["user_id"]))
        exp = me.get("exp")

        if exp is not None:
            expired_at = datetime.fromtimestamp(
                float(exp),
                tz=ZoneInfo("Asia/Kolkata")
            )
            message = f"Access token expires at {expired_at.strftime('%d-%m-%Y %I:%M:%S %p %Z')}"
        else:
            message = "Access token expiration time is not available"

        return {
            "message" : message,
            "data": {**me, **identity}
        }
                
    return router;


def verify_cookie_request_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    if origin is None or origin.rstrip("/") not in settings.cors_allowed_origins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Request origin is not allowed.",
        )
