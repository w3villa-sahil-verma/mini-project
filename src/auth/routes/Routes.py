from fastapi import APIRouter, Depends
from typing import Annotated
from src.auth.controller.Controller import AuthController


def getRouter()->APIRouter:

    router: APIRouter = APIRouter(
        prefix="/auth",
        tags=["Auth"],
        responses={404: {"description": "Not found"}},
    )

    @router.get("/registration-mail")
    async def getRegistrationMail(
        authController: Annotated[AuthController, Depends(AuthController)],
        email: str
    ):

        return await authController.getRegistrationMail(email);
        


    return router;