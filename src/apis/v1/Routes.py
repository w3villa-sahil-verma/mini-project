
from fastapi import APIRouter;

from src.auth.routes.Routes import getRouter as authRouter;
from src.organization.routes.Routes import getRouter as orgRouter;


router: APIRouter = APIRouter(
    prefix="/api/v1",
    responses={404: {"description": "Not found"}},  
)


# include other routes below

router.include_router(authRouter());
router.include_router(orgRouter());

# router.include_router(other_router);