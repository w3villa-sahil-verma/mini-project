
from fastapi import APIRouter;

from src.auth.routes.Routes import getRouter;

router: APIRouter = APIRouter(
    prefix="/api/v1",
    responses={404: {"description": "Not found"}},  
)


# include other routes below

router.include_router(getRouter());

# router.include_router(other_router);