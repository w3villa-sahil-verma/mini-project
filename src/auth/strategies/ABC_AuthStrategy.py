from abc import ABC, abstractmethod
from typing import TypedDict

class LoginResponse(TypedDict):
    access_token: str

class AuthStrategy(ABC):
    """Interface for auth strategies."""

    #TODO : Registration Link merge here

    @abstractmethod
    async def authenticate(self, email: str, password: str) -> str:
        """Accept Provider's AccessToken and authenticate user"""
        raise NotImplementedError

    @abstractmethod
    async def logout(self)->None:
        """Remove the ACCESS_TOKEN from Cookie"""
        raise NotImplementedError