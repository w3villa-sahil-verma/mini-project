from fastapi import APIRouter, Depends, Response, Body
from typing import Annotated
from pydantic import BaseModel, Field

from src.plan.controller.Controller import PlanController

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
        prefix="/plans",
        tags=["Plan"],
        responses={404: {"description": "Not found"}},
    )

    @router.get("")
    async def getAll(
        controller: Annotated[PlanController, Depends(PlanController)],
    ):
        return await controller.get_all()

    @router.post("", status_code=201)
    async def create(
        controller: Annotated[PlanController, Depends(PlanController)],
        payload: PlanCreate,
    ):
        return await controller.create(**payload.model_dump())

    @router.put("/{plan_id}")
    async def replace(
        plan_id: int,
        payload: PlanUpdate,
        controller: Annotated[PlanController, Depends(PlanController)],
    ):
        """Expect whole object. that would be replaced by existing once."""
        return await controller.put(
            plan_id=plan_id,
            **payload.model_dump(),
        )
    
    @router.patch("/{plan_id}")
    async def update(
        plan_id: int,
        payload: PlanPatch,
        controller: Annotated[PlanController, Depends(PlanController)],
    ):
        """Expect the fields to be update in object"""
        updates = payload.model_dump(exclude_unset=True)

        # Reject explicit nulls for fields that cannot be null.
        if any(value is None for value in updates.values()):
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Fields cannot be null",
            )

        return await controller.patch(plan_id, updates)

    @router.delete("/{plan_id}")
    async def delete(
        plan_id: int,
        controller: Annotated[PlanController, Depends(PlanController)],
    ):
        return await controller.soft_delete(plan_id)
        
    return router;

