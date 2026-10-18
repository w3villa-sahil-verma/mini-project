
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.Database import getAsyncDbSession
from src.models.Plan import Plan


class PlanController:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(getAsyncDbSession)],
    ):
        self.db = db

    async def create(
        self,
        name: str,
        duration_hours: int,
        price_minor: int,
        currency: str,
    ):
        if duration_hours <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Duration must be greater than zero",
            )

        if price_minor < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Price cannot be negative",
            )

        existing = await self.db.scalar(
            select(Plan).where(Plan.name == name)
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Plan name already exists",
            )

        plan = Plan(
            name=name,
            duration_hours=duration_hours,
            price_minor=price_minor,
            currency=currency.upper(),
            is_active=True,
        )

        self.db.add(plan)
        await self.db.commit()
        await self.db.refresh(plan)

        return {
            "message": "Plan created successfully",
            "data": self._serialize(plan),
        }

    async def get_all(self):
        result = await self.db.scalars(
            select(Plan).order_by(Plan.id.desc())
        )

        plans = result.all()

        return {
            "message": "Plans retrieved successfully",
            "data": [self._serialize(plan) for plan in plans],
        }

    async def get(self, plan_id: int):
        plan = await self.db.get(Plan, plan_id)

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found",
            )

        return {
            "message": "Plan retrieved successfully",
            "data": self._serialize(plan),
        }

    async def put(
        self,
        plan_id: int,
        name: str,
        duration_hours: int,
        price_minor: int,
        currency: str,
        is_active: bool,
    ):
        plan = await self.db.get(Plan, plan_id)

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found",
            )

        if duration_hours <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Duration must be greater than zero",
            )

        if price_minor < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Price cannot be negative",
            )

        duplicate = await self.db.scalar(
            select(Plan).where(
                Plan.name == name,
                Plan.id != plan_id,
            )
        )

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Plan name already exists",
            )

        plan.name = name
        plan.duration_hours = duration_hours
        plan.price_minor = price_minor
        plan.currency = currency.upper()
        plan.is_active = is_active
        plan.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(plan)

        return {
            "message": "Plan updated successfully",
            "data": self._serialize(plan),
        }

    async def patch(
        self,
        plan_id: int,
        updates: dict,
    ):
        plan = await self.db.get(Plan, plan_id)

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found",
            )

        allowed_fields = {
            "name",
            "duration_hours",
            "price_minor",
            "currency",
            "is_active",
        }

        invalid_fields = set(updates) - allowed_fields

        if invalid_fields:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid fields: {', '.join(sorted(invalid_fields))}",
            )

        if "duration_hours" in updates and updates["duration_hours"] <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Duration must be greater than zero",
            )

        if "price_minor" in updates and updates["price_minor"] < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Price cannot be negative",
            )

        if "name" in updates:
            duplicate = await self.db.scalar(
                select(Plan).where(
                    Plan.name == updates["name"],
                    Plan.id != plan_id,
                )
            )

            if duplicate:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Plan name already exists",
                )

        if "currency" in updates:
            updates["currency"] = updates["currency"].upper()

        for field, value in updates.items():
            setattr(plan, field, value)

        plan.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(plan)

        return {
            "message": "Plan updated successfully",
            "data": self._serialize(plan),
        }

    async def soft_delete(self, plan_id: int):
        plan = await self.db.get(Plan, plan_id)

        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found",
            )

        plan.is_active = False
        plan.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(plan)

        return {
            "message": "Plan deactivated successfully",
            "data": self._serialize(plan),
        }

    @staticmethod
    def _serialize(plan: Plan) -> dict:
        return {
            "id": plan.id,
            "name": plan.name,
            "duration_hours": plan.duration_hours,
            "price_minor": plan.price_minor,
            "currency": plan.currency,
            "is_active": plan.is_active,
            "created_at": plan.created_at,
            "updated_at": plan.updated_at,
        }
