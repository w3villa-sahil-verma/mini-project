from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import uuid4

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.Database import getAsyncDbSession
from src.models.Plan import Plan
from src.models.Subscription import Subscription
from src.models.User import User
from src.payment.services.PaymentService import PaymentService


class PaymentController:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(getAsyncDbSession)],
        payment_service: Annotated[PaymentService, Depends(PaymentService)],
    ):
        self.db = db
        self.payment_service = payment_service

    async def checkout(self, user_id: int, plan_id: int) -> dict:
        plan = await self._get_available_plan(plan_id)

        if plan.price_minor == 0:
            subscription = await self._activate_subscription(user_id, plan)
            await self.db.commit()
            await self.db.refresh(subscription)
            return {
                "message": "Free plan activated successfully",
                "data": {
                    "type": "activated",
                    "subscription": self._serialize_subscription(subscription),
                },
            }

        order = await self.payment_service.create_order(
            amount_minor=plan.price_minor,
            currency=plan.currency,
            receipt=f"gym-{uuid4().hex[:30]}",
        )
        subscription = Subscription(
            user_id=user_id,
            plan_id=plan.id,
            provider_order_id=order["id"],
            amount_minor=plan.price_minor,
            currency=plan.currency,
            status="PAYMENT_PENDING",
        )
        self.db.add(subscription)
        await self.db.commit()

        return {
            "message": "Payment order created successfully",
            "data": {
                "type": "razorpay",
                "order_id": order["id"],
                "amount": order["amount"],
                "currency": order["currency"],
                "plan_name": plan.name,
            },
        }

    async def verify_payment(
        self,
        *,
        user_id: int,
        order_id: str,
        payment_id: str,
        signature: str,
    ) -> dict:
        if not self.payment_service.verify_signature(
            order_id=order_id,
            payment_id=payment_id,
            signature=signature,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment signature verification failed.",
            )

        subscription = await self.db.scalar(
            select(Subscription).where(
                Subscription.provider_order_id == order_id,
                Subscription.user_id == user_id,
            )
        )
        if subscription is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment order not found.",
            )

        if subscription.status != "PAYMENT_PENDING":
            if (
                subscription.provider_payment_id == payment_id
                and subscription.status in {"ACTIVE", "SCHEDULED"}
            ):
                return {
                    "message": "Payment was already verified",
                    "data": self._serialize_subscription(subscription),
                }
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This payment order has already been processed.",
            )

        subscription.provider_payment_id = payment_id
        await self._schedule_subscription(subscription)
        await self.db.commit()
        await self.db.refresh(subscription)

        return {
            "message": "Payment verified and plan scheduled successfully",
            "data": self._serialize_subscription(subscription),
        }

    async def get_my_subscriptions(self, user_id: int) -> dict:
        result = await self.db.scalars(
            select(Subscription)
            .where(Subscription.user_id == user_id)
            .order_by(Subscription.created_at.desc())
        )
        return {
            "message": "Subscriptions retrieved successfully",
            "data": [
                self._serialize_subscription(subscription)
                for subscription in result.all()
            ],
        }

    async def _get_available_plan(self, plan_id: int) -> Plan:
        plan = await self.db.get(Plan, plan_id)
        if plan is None or not plan.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found or is no longer available.",
            )
        return plan

    async def _activate_subscription(
        self,
        user_id: int,
        plan: Plan,
    ) -> Subscription:
        subscription = Subscription(
            user_id=user_id,
            plan_id=plan.id,
            amount_minor=plan.price_minor,
            currency=plan.currency,
            status="PAYMENT_PENDING",
        )
        self.db.add(subscription)
        await self.db.flush()
        await self._schedule_subscription(subscription)
        return subscription

    async def _schedule_subscription(self, subscription: Subscription) -> None:
        now = datetime.now(timezone.utc)
        await self.db.scalar(
            select(User.id)
            .where(User.id == subscription.user_id)
            .with_for_update()
        )
        latest_expiry = await self.db.scalar(
            select(Subscription.expires_at)
            .where(
                Subscription.user_id == subscription.user_id,
                Subscription.id != subscription.id,
                Subscription.status.in_(("ACTIVE", "SCHEDULED")),
                Subscription.expires_at > now,
            )
            .order_by(Subscription.expires_at.desc())
            .limit(1)
        )

        starts_at = now
        if latest_expiry is not None:
            if latest_expiry.tzinfo is None:
                latest_expiry = latest_expiry.replace(tzinfo=timezone.utc)
            starts_at = max(now, latest_expiry)

        plan = await self.db.get(Plan, subscription.plan_id)
        if plan is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found.",
            )

        subscription.starts_at = starts_at
        subscription.expires_at = starts_at + timedelta(hours=plan.duration_hours)
        subscription.status = "SCHEDULED" if starts_at > now else "ACTIVE"

    @staticmethod
    def _serialize_subscription(subscription: Subscription) -> dict:
        now = datetime.now(timezone.utc)
        starts_at = subscription.starts_at
        expires_at = subscription.expires_at
        if starts_at is not None and starts_at.tzinfo is None:
            starts_at = starts_at.replace(tzinfo=timezone.utc)
        if expires_at is not None and expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        current_status = subscription.status
        if current_status in {"ACTIVE", "SCHEDULED"}:
            if expires_at is not None and expires_at <= now:
                current_status = "EXPIRED"
            elif starts_at is not None and starts_at <= now:
                current_status = "ACTIVE"

        return {
            "id": subscription.id,
            "plan_id": subscription.plan_id,
            "status": current_status,
            "amount_minor": subscription.amount_minor,
            "currency": subscription.currency,
            "starts_at": starts_at,
            "expires_at": expires_at,
        }
