from fastapi import APIRouter, Depends
from typing import Annotated

from src.middlewares.authorization import require_access_token
from src.user.controller.Controller import ProfileUpdate, UserController

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


def getProfileRouter() -> APIRouter:
    router = APIRouter(
        prefix="/users",
        tags=["User profile"],
        responses={404: {"description": "Not found"}},
    )

    @router.get("/me")
    async def get_profile(
        current_user: Annotated[dict, Depends(require_access_token)],
        controller: Annotated[UserController, Depends(UserController)],
    ):
        return await controller.get_profile(int(current_user["user_id"]))

    @router.put("/me")
    async def update_profile(
        payload: ProfileUpdate,
        current_user: Annotated[dict, Depends(require_access_token)],
        controller: Annotated[UserController, Depends(UserController)],
    ):
        return await controller.update_profile(
            int(current_user["user_id"]),
            payload,
        )

    return router
