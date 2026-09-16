from fastapi import Depends
from typing import Annotated

from src.common.notification.NotificationService import NotificationService
from src.common.notification.Notification import Notification;

class RegistrationLinkService:
    def __init__(self, notification_service: Annotated[NotificationService, Depends(NotificationService)]):
        self.notificationService = notification_service;

    async def create_registration_link(self, email: str):
        # step 1: Create a user and account.

        # step 2: Create token

        # step 2: Send a verification email to the user with a unique registration link.
        await self.notificationService.send(Notification(
            recipient=email,
            body="http://abc.com?email={email}&code=abc",
            subject="GYM Registration mail"
        ))

        return { "link" : f"http://abc.com?email={email}&code=abc"}

        

