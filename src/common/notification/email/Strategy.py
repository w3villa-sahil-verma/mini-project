from fastapi_mail import (
    FastMail,
    MessageSchema,
    ConnectionConfig,
    MessageType,
    NameEmail,
)
from pydantic import SecretStr

from src.common.notification.ABC_NotificationStrategy import NotificationStrategy
from src.common.notification.Notification import Notification
from src.common.notification.email.config import settings


class EmailNotificationStrategy(NotificationStrategy):
    """Email implementation of the notification strategy."""

    def __init__(self):
        if not settings.MAIL_FROM:
            raise ValueError("MAIL_FROM must be configured to send email through SMTP.")

        conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=SecretStr(settings.MAIL_PASSWORD),
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )
        self.mailer = FastMail(conf)

    async def send(self, notification: Notification) -> None:
        message = MessageSchema(
            subject=notification.subject,
            recipients=[NameEmail(name="", email=notification.recipient)],
            body=notification.body,
            subtype=MessageType.html,
        )

        await self.mailer.send_message(message)
