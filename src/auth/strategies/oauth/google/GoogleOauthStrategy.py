from src.auth.strategies.oauth.ABC_OauthStrategy import OauthStrategy;
from src.auth.strategies.oauth.google.config import settings;

class GoogleOauthStrategy(OauthStrategy):

    def __init__(self) -> None:
        self.CLIENT_ID = settings.GOOGLE_CLIENT_ID
        self._CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
        self.REDIRECT_URL = ""
        self.SCOPS = "openid email profile"

    async def getMeta(self):
        return {
            "clientId" : self.CLIENT_ID,
            "redirectUrl" : self.REDIRECT_URL,
            "scops": self.SCOPS
        }

    async def authenticate(self, accessToken: str) -> str:
        return ""

    async def logout(self):
        pass;
