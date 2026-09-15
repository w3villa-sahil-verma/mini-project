
class NotificationService:

    def notify(self, email: str, token: str):
        """
        Notify the user about an event.
        """
        # Implementation of the notification logic goes here
        print(f"Notification sent to {email}: /auth/register?code={token}")
