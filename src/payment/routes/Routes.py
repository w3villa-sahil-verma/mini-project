from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.middlewares.authorization import require_access_token
from src.payment.controller.Controller import PaymentController


class CheckoutRequest(BaseModel):
    plan_id: int = Field(gt=0)


class PaymentVerificationRequest(BaseModel):
    razorpay_order_id: str = Field(min_length=1, max_length=100)
    razorpay_payment_id: str = Field(min_length=1, max_length=100)
    razorpay_signature: str = Field(min_length=1, max_length=256)


def getRouter() -> APIRouter:
    router = APIRouter(
        prefix="/payments",
        tags=["Payments"],
    )

    @router.post("/checkout")
    async def checkout(
        payload: CheckoutRequest,
        current_user: Annotated[dict, Depends(require_access_token)],
        controller: Annotated[PaymentController, Depends(PaymentController)],
    ):
        return await controller.checkout(
            user_id=int(current_user["user_id"]),
            plan_id=payload.plan_id,
        )

    @router.post("/verify")
    async def verify_payment(
        payload: PaymentVerificationRequest,
        current_user: Annotated[dict, Depends(require_access_token)],
        controller: Annotated[PaymentController, Depends(PaymentController)],
    ):
        return await controller.verify_payment(
            user_id=int(current_user["user_id"]),
            order_id=payload.razorpay_order_id,
            payment_id=payload.razorpay_payment_id,
            signature=payload.razorpay_signature,
        )

    @router.get("/subscriptions/me")
    async def get_my_subscriptions(
        current_user: Annotated[dict, Depends(require_access_token)],
        controller: Annotated[PaymentController, Depends(PaymentController)],
    ):
        return await controller.get_my_subscriptions(
            user_id=int(current_user["user_id"]),
        )

    return router
