from fastapi import APIRouter, Depends, Response, Body
from typing import Annotated
from pydantic import BaseModel

from src.auth.controller.Controller import AuthController

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

    @router.post("/standard-register")
    async def standardRegister(
        authController: Annotated[AuthController, Depends(AuthController)],
        data: RequestBody
    ):
        return await authController.standardRegister(email=data.email, password=data.password, token=data.token);
        

    # TODO : implement later
    @router.post("/oauth-register")
    async def oauthRegister(
        authController: Annotated[AuthController, Depends(AuthController)],
    ):
        pass;

    @router.post("/standard-login")
    async def standardLogin(
        authController: Annotated[AuthController, Depends(AuthController)],
        body: StandardLoginRequestBody,
        response: Response
    ):
        return await authController.login(email=body.email, password=body.password, response=response);



        
    return router;

