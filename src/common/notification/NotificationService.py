from typing import Annotated
from fastapi import Depends

from src.common.notification.Notification import Notification
from src.common.notification.ABC_NotificationStrategy import NotificationStrategy
from src.common.notification.email.Strategy import EmailNotificationStrategy
from src.common.notification.email.GoogleAppsScriptStrategy import (
    GoogleAppsScriptEmailStrategy,
)
from src.common.notification.email.config import settings


def get_email_notification_strategy() -> NotificationStrategy:
    if settings.EMAIL_PROVIDER == "google_apps_script":
        return GoogleAppsScriptEmailStrategy()
    return EmailNotificationStrategy()


class NotificationService:
    """Application service responsible for sending notifications."""

    def __init__(
        self,
        strategy: Annotated[
            NotificationStrategy,
            Depends(get_email_notification_strategy),
        ],
    ) -> None:
        self.strategy = strategy

    async def send(self, notification: Notification) -> None:
        await self.strategy.send(notification)
