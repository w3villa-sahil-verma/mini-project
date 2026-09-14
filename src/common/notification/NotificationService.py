
class NotificationService:

    def notify(self, email: str, token: str):
        """
        Notify the user about an event.
        """
        # Implementation of the notification logic goes here
        print(f"Notification sent to {email}: /auth/register?code={token}")



"""
Dependency for FastAPI
"""

def get_notification_service():
    return NotificationService()