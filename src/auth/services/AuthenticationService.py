from typing import Annotated;

from fastapi import Depends;

from src.auth.strategies.StandardAuthStrategy import StandardAuthStrategy;
from src.auth.strategies.oauth.google.GoogleOauthStrategy import GoogleOauthStrategy;
from src.auth.strategies.oauth.ABC_OauthStrategy import OauthStrategy;
from src.auth.strategies.ABC_AuthStrategy import AuthStrategy;

class AuthenticationService:
    def __init__(
        self, 
        strategy: Annotated[AuthStrategy, Depends(StandardAuthStrategy)],
        oauthStrategy: Annotated[OauthStrategy, Depends(GoogleOauthStrategy)]
    ) -> None:
        self.strategy = strategy;
        self.oauthStrategy = oauthStrategy;

    # Standard authentication
    async def authenticate(self, email:str, password:str):
        return await self.strategy.authenticate(email, password);

    # Oauth authentication
    async def oauthAuthenticate(self, accessToken:str):
        return self.oauthStrategy.authenticate(accessToken=accessToken);

    # Get CLIENT_ID + SCOPES + REDIRECT_URL
    async def getOauthMeta(self):
        return await self.oauthStrategy.getMeta();

    def logout(self):
        pass