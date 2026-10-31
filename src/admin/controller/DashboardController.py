from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.Database import getAsyncDbSession
from src.models.Plan import Plan
from src.models.Subscription import Subscription
from src.models.User import User


class DashboardController:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(getAsyncDbSession)],
    ):
        self.db = db

    async def get_dashboard(self) -> dict:
        now = datetime.now(timezone.utc)
        current_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        first_month = self._month_offset(current_month, -11)
        next_month = self._month_offset(current_month, 1)

        total_users = await self.db.scalar(
            select(func.count(User.id)).where(User.is_deleted.is_(False))
        )
        total_plans = await self.db.scalar(
            select(func.count(Plan.id))
        )
        active_subscriptions = await self.db.scalar(
            select(func.count(Subscription.id)).where(
                Subscription.status.in_(("ACTIVE", "SCHEDULED")),
                Subscription.starts_at <= now,
                Subscription.expires_at > now,
            )
        )

        plans_result = await self.db.scalars(
            select(Plan).order_by(Plan.price_minor.asc(), Plan.id.asc())
        )
        recent_users_result = await self.db.scalars(
            select(User)
            .where(User.is_deleted.is_(False))
            .order_by(User.created_at.desc(), User.id.desc())
            .limit(8)
        )

        registration_dates = await self.db.scalars(
            select(User.created_at).where(
                User.is_deleted.is_(False),
                User.created_at >= first_month,
                User.created_at < next_month,
            )
        )
        subscription_dates = await self.db.scalars(
            select(Subscription.created_at).where(
                Subscription.created_at >= first_month,
                Subscription.created_at < next_month,
            )
        )

        registrations_by_month = self._count_by_month(registration_dates.all())
        subscriptions_by_month = self._count_by_month(subscription_dates.all())

        expiration_rows = (
            await self.db.execute(
                select(Subscription, User.email, Plan.name)
                .join(User, User.id == Subscription.user_id)
                .join(Plan, Plan.id == Subscription.plan_id)
                .where(
                    User.is_deleted.is_(False),
                    Subscription.status.in_(("ACTIVE", "SCHEDULED")),
                    Subscription.expires_at > now,
                )
                .order_by(Subscription.expires_at.asc())
                .limit(12)
            )
        ).all()

        return {
            "message": "Dashboard data retrieved successfully",
            "data": {
                "summary": {
                    "total_plans": int(total_plans or 0),
                    "active_subscriptions": int(active_subscriptions or 0),
                    "total_users": int(total_users or 0),
                },
                "plans": [
                    {
                        "id": plan.id,
                        "name": plan.name,
                        "duration_hours": plan.duration_hours,
                        "price_minor": plan.price_minor,
                        "currency": plan.currency,
                        "is_active": plan.is_active,
                    }
                    for plan in plans_result.all()
                ],
                "recent_users": [
                    {
                        "id": user.id,
                        "email": user.email,
                        "role": user.role.value,
                        "created_at": user.created_at,
                    }
                    for user in recent_users_result.all()
                ],
                "user_registrations": self._format_monthly_series(
                    first_month, registrations_by_month
                ),
                "subscriptions_by_month": self._format_monthly_series(
                    first_month, subscriptions_by_month
                ),
                "upcoming_expirations": [
                    {
                        "id": subscription.id,
                        "user_email": email,
                        "plan_name": plan_name,
                        "status": subscription.status,
                        "starts_at": subscription.starts_at,
                        "expires_at": subscription.expires_at,
                    }
                    for subscription, email, plan_name in expiration_rows
                ],
            },
        }

    @staticmethod
    def _month_offset(month: datetime, offset: int) -> datetime:
        month_index = month.year * 12 + month.month - 1 + offset
        year, zero_based_month = divmod(month_index, 12)
        return month.replace(year=year, month=zero_based_month + 1, day=1)

    @staticmethod
    def _count_by_month(dates: list[datetime]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for date in dates:
            month_key = f"{date.year:04d}-{date.month:02d}"
            counts[month_key] = counts.get(month_key, 0) + 1
        return counts

    @classmethod
    def _format_monthly_series(
        cls,
        first_month: datetime,
        counts: dict[str, int],
    ) -> list[dict]:
        months = []
        month = first_month
        for _ in range(12):
            month_key = month.strftime("%Y-%m")
            months.append(
                {
                    "month": month.strftime("%b %Y"),
                    "count": counts.get(month_key, 0),
                }
            )
            month = cls._month_offset(month, 1)
        return months
