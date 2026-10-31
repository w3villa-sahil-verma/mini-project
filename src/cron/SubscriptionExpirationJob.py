import asyncio
import logging
from datetime import datetime, timezone

from sqlalchemy import update

from src.database.Database import db
from src.models.Subscription import Subscription

logger = logging.getLogger(__name__)
CHECK_INTERVAL_SECONDS = 60


async def expire_subscriptions() -> int:
    now = datetime.now(timezone.utc)
    async with (await db.getAsyncSession()) as session:
        result = await session.execute(
            update(Subscription)
            .where(
                Subscription.status.in_(("ACTIVE", "SCHEDULED")),
                Subscription.expires_at <= now,
            )
            .values(status="EXPIRED", updated_at=now)
        )
        await session.commit()
        return result.rowcount or 0


async def run_subscription_expiration_job() -> None:
    while True:
        try:
            expired_count = await expire_subscriptions()
            if expired_count:
                logger.info("Marked %s subscriptions as expired", expired_count)
        except Exception:
            logger.exception("Subscription expiration check failed")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
