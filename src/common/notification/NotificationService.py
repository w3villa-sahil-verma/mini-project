from typing import Annotated;
from fastapi import Depends;

from src.common.notification.Notification import Notification;
from src.common.notification.ABC_NotificationStrategy import NotificationStrategy;
from src.common.notification.email.Strategy import EmailNotificationStrategy

class NotificationService:  
    """Application service responsible for sending notifications."""

    def __init__(self, strategy: Annotated[NotificationStrategy, Depends(EmailNotificationStrategy)]):
        self.strategy = strategy

    async def send(self, notification: Notification) -> None:
        await self.strategy.send(notification)
