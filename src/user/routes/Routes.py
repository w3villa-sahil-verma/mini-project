from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query

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
        controller: Annotated[UserController, Depends(UserController)],
        page: Annotated[int, Query(ge=1)] = 1,
        page_size: Annotated[int, Query(ge=1, le=100)] = 20,
        search: Annotated[str | None, Query(max_length=100)] = None,
        role: Annotated[Literal["ADMIN", "USER"] | None, Query()] = None,
        status_filter: Annotated[
            Literal["all", "active", "deleted"],
            Query(alias="status"),
        ] = "all",
    ):
        return await controller.get_all(
            page=page,
            page_size=page_size,
            search=search,
            role=role,
            status_filter=status_filter,
        )

    @router.delete("/{user_id}")
    async def delete(
        user_id: int,
        controller: Annotated[UserController, Depends(UserController)],
    ):
        return await controller.soft_delete(user_id)
        
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
