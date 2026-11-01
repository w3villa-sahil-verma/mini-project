from typing import TypedDict


class AuthTokens(TypedDict):
    access_token: str
    refresh_token: str
