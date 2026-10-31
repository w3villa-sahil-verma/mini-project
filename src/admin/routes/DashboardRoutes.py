from typing import Annotated

from fastapi import APIRouter, Depends

from src.admin.controller.DashboardController import DashboardController


def getRouter() -> APIRouter:
    router = APIRouter(
        tags=["Admin dashboard"],
    )

    @router.get("/dashboard")
    async def get_dashboard(
        controller: Annotated[
            DashboardController,
            Depends(DashboardController),
        ],
    ):
        return await controller.get_dashboard()

    return router
