from abc import ABC, abstractmethod;

class Registration:
    """Interface for Registation service"""

    @abstractmethod
    async def sendRegistrationLink(self, email: str):
        """Send Registration link for user registration"""
        raise NotImplementedError

    @abstractmethod
    async def register(self, email:str, password:str, token:str):
        """Register user after verify the token"""
        raise NotImplementedError