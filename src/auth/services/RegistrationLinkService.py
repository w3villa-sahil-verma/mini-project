from fastapi import Depends

from common.notification.NotificationService import get_notification_service

class RegistrationLinkService:
    def __init__(self, registration_link_repository, notification_service = Depends(get_notification_service)):
        self.registration_link_repository = registration_link_repository

    def create_registration_link(self, email: str):
        # step 1: Create a user and account.
        

        # step 2: Send a verification email to the user with a unique registration link.

        pass

    def validate_registration_link(self, link):
        # Logic to validate the provided registration link
        pass
        

registrationLinkService = RegistrationLinkService(registration_link_repository=None)  # Replace None with actual repository instance