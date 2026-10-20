from fastapi import APIRouter, Depends
from typing import Annotated
from pydantic import BaseModel, Field

from src.user.controller.Controller import UserController

def getRouter()->APIRouter:

    router: APIRouter = APIRouter(
        prefix="/users",
        tags=["User"],
        responses={404: {"description": "Not found"}},
    )

    @router.get("")
    async def getAll(
        controller: Annotated[UserController, Depends(UserController)]
    ):
        return await controller.get_all()

    @router.delete("/{plan_id}")
    async def delete(
        plan_id: int,
        controller: Annotated[UserController, Depends(UserController)],
    ):
        return await controller.soft_delete(plan_id)
        
    return router;

