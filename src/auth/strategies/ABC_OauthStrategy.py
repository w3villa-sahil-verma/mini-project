from abc import ABC, abstractmethod

class OauthStrategy(ABC):
    """Interface for oauth strategies."""

    @abstractmethod
    async def getMeta(self):
        """Return Respective Provider (CLIENT_ID, SCOPES, REIDRECT_URL)"""
        raise NotImplementedError

    @abstractmethod
    async def authenticate(self, accessToken: str) -> str:
        """Accept Provider's AccessToken and authenticate user"""
        raise NotImplementedError

    @abstractmethod
    async def logout(self):
        """Remove the ACCESS_TOKEN from Cookie"""
        raise NotImplementedError