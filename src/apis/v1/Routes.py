
from fastapi import APIRouter;

from src.auth.routes.Routes import getRouter as authRouter;
from src.plan.routes.Routes import getRouter as planRouter;


router: APIRouter = APIRouter(
    prefix="/api/v1",
    responses={404: {"description": "Not found"}},  
)

admin_router: APIRouter = APIRouter(
    prefix="/admin",
    responses={404: {"description": "Not found"}}
)

# include other routes below
admin_router.include_router(planRouter());

router.include_router(authRouter());
router.include_router(admin_router);

# router.include_router(other_router);