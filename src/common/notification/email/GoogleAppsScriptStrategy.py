import httpx

from src.common.notification.ABC_NotificationStrategy import NotificationStrategy
from src.common.notification.Notification import Notification
from src.common.notification.email.config import settings


class GoogleAppsScriptEmailStrategy(NotificationStrategy):
    """Deliver email through a deployed Google Apps Script web app."""

    def __init__(self) -> None:
        if not settings.GOOGLE_SCRIPT_URL:
            raise ValueError(
                "GOOGLE_SCRIPT_URL must be configured for Google Apps Script email."
            )
        if not settings.GOOGLE_SCRIPT_URL.startswith("https://"):
            raise ValueError("GOOGLE_SCRIPT_URL must use HTTPS.")
        if not settings.EMAIL_API_SECRET:
            raise ValueError(
                "EMAIL_API_SECRET must be configured for Google Apps Script email."
            )

    async def send(self, notification: Notification) -> None:
        payload = {
            "secret": settings.EMAIL_API_SECRET,
            "to": notification.recipient,
            "subject": notification.subject,
            "text": notification.body,
            "html": "",
        }

        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            response = await client.post(settings.GOOGLE_SCRIPT_URL, json=payload)
            response.raise_for_status()
            try:
                result = response.json()
            except ValueError as error:
                raise RuntimeError(
                    "Google Apps Script returned an invalid response."
                ) from error

        if not isinstance(result, dict) or result.get("success") is not True:
            raise RuntimeError("Google Apps Script failed to send the email.")
