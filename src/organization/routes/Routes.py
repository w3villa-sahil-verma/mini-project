from fastapi import APIRouter, Depends
from typing import Annotated

from src.organization.controller.Controller import Controller;
from src.organization.schema import Organization


def getRouter()->APIRouter:

    router: APIRouter = APIRouter(
        prefix="/organizations",
        tags=["Organization"],
        responses={404: {"description": "Not found"}},
    )

    @router.post("")
    async def register(
        controller: Annotated[Controller, Depends(Controller)],
        organization: Organization
    ):
        return await controller.register(org=organization)

    @router.get("/{id}")
    async def getOrganization(
        controller: Annotated[Controller, Depends(Controller)],
        id: str
    ):
        return await controller.getOrganization(id);
        
    return router;

