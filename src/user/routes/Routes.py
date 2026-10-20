from fastapi import APIRouter, Depends
from typing import Annotated
from pydantic import BaseModel, Field

from src.user.controller.Controller import UserController
from src.middlewares.authorization import require_access_token

class PlanCreate(BaseModel):
    name: str = Field(min_length=1, max_length=30)
    duration_hours: int = Field(gt=0)
    price_minor: int = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)

class PlanUpdate(PlanCreate):
    is_active: bool

class PlanPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=30)
    duration_hours: int | None = Field(default=None, gt=0)
    price_minor: int | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    is_active: bool | None = None

def getRouter()->APIRouter:

    router: APIRouter = APIRouter(
        prefix="/users",
        tags=["User"],
        responses={404: {"description": "Not found"}},
    )

    @router.get("")
    async def getAll(
        controller: Annotated[UserController, Depends(UserController)],
        current_user: Annotated[dict, Depends(require_access_token)]
    ):
        return await controller.get_all()

    @router.delete("/{plan_id}")
    async def delete(
        plan_id: int,
        controller: Annotated[UserController, Depends(UserController)],
    ):
        return await controller.soft_delete(plan_id)
        
    return router;

