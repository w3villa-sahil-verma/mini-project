from fastapi import Depends
from typing import Annotated

from src.common.notification.NotificationService import NotificationService

class RegistrationLinkService:
    def __init__(self, notification_service: Annotated[NotificationService, Depends(NotificationService)]):
        self.notificationService = notification_service;

    def create_registration_link(self, email: str):
        # step 1: Create a user and account.

        # step 2: Send a verification email to the user with a unique registration link.
        self.notificationService.notify(email,"abc")

        return { "link" : f"http://abc.com?email={email}&code=abc"}

    def validate_registration_link(self, link):
        # Logic to validate the provided registration link
        pass
        

