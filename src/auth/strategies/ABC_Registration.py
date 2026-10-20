from abc import ABC, abstractmethod;
from typing import TypedDict

class RegisterResponse(TypedDict):
    access_token: str

class Registration:
    """Interface for Registation service"""

    @abstractmethod
    async def sendRegistrationLink(self, email: str):
        """Send Registration link for user registration"""
        raise NotImplementedError

    @abstractmethod
    async def register(self, email:str, password:str, token:str) -> str:
        """Register user after verify the token"""
        raise NotImplementedError