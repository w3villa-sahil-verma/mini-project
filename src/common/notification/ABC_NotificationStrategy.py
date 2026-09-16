from abc import ABC, abstractmethod

from src.common.notification.Notification import Notification;


class NotificationStrategy(ABC):
    """Interface for notification delivery strategies."""

    @abstractmethod
    async def send(self, notification: Notification) -> None:
        """Send a notification."""
        raise NotImplementedError