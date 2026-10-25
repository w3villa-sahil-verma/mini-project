from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, Response, Body
from typing import Annotated
from pydantic import BaseModel

from src.auth.controller.Controller import AuthController
from src.middlewares.authorization import require_access_token


class RequestBody(BaseModel):
    email: str
    password: str
    token: str

class StandardLoginRequestBody(BaseModel):
    email: str
    password: str

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

    @router.get("/oauth/meta")
    async def oauthMeta(
        authController: Annotated[AuthController, Depends(AuthController)],
    ):
        return await authController.getOauthMeta();

    @router.post("/oauth/login")
    async def oauthLogin(
        authController: Annotated[AuthController, Depends(AuthController)],
    ):
        pass;

    @router.get("/logout")
    async def logout(
        response: Response,
        authController: Annotated[AuthController, Depends(AuthController)],
    ):
        return await authController.logout(response=response);

    @router.get("/me")
    async def me(
        me: Annotated[dict, Depends(require_access_token)],
    ):
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
            "data": me
        }
                
    return router;

