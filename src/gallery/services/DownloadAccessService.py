from datetime import datetime, timedelta, timezone

DOWNLOAD_WINDOW_HOURS = {
    "silver": 1,
    "silver plan": 1,
    "gold": 3,
    "gold plan": 3,
}


def download_access_expires_at(
    *,
    plan_name: str,
    starts_at: datetime | None,
    subscription_expires_at: datetime | None,
    now: datetime,
) -> datetime | None:
    duration_hours = DOWNLOAD_WINDOW_HOURS.get(plan_name.strip().casefold())
    if (
        duration_hours is None
        or starts_at is None
        or subscription_expires_at is None
    ):
        return None

    starts_at = _as_utc(starts_at)
    subscription_expires_at = _as_utc(subscription_expires_at)
    now = _as_utc(now)
    if starts_at > now or subscription_expires_at <= now:
        return None

    access_expires_at = min(
        starts_at + timedelta(hours=duration_hours),
        subscription_expires_at,
    )
    return access_expires_at if access_expires_at > now else None


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
