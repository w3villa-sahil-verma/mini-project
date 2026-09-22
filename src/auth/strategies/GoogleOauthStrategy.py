from auth.strategies.ABC_OauthStrategy import OauthStrategy;

class GoogleOauthStrategy(OauthStrategy):

    def __init__(self) -> None:
        self.CLIENT_ID = ""
        self.CLIENT_SECREATE = "" # should be private member
        self.REDIRECT_URL = ""
        self.SCOPS = []

    async def authenticate(self, accessToken: str) -> str:
        return ""

    async def logout(self):
        pass;
