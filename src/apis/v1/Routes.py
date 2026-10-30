
from fastapi import APIRouter, Depends;


from src.auth.routes.Routes import getRouter as authRouter;
from src.plan.routes.Routes import getPricingRouter, getRouter as planRouter;
from src.user.routes.Routes import getProfileRouter as userProfileRouter;
from src.user.routes.Routes import getRouter as userRouter;
from src.middlewares.authorization import require_role
from src.models.User import USER_ROLE

router: APIRouter = APIRouter(
    prefix="/api/v1",
    responses={404: {"description": "Not found"}},  
)

admin_router: APIRouter = APIRouter(
    prefix="/admin",
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(require_role(USER_ROLE.ADMIN))],
)

# include other routes below
admin_router.include_router(planRouter());
admin_router.include_router(userRouter());

router.include_router(authRouter());
router.include_router(getPricingRouter());
router.include_router(userProfileRouter());
router.include_router(admin_router);

# router.include_router(other_router);