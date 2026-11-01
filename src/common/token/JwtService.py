import jwt

from src.core.settings import settings

SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = "HS256"


class JwtTokenService:
    def sign(self, payload: dict) -> str:
        """Create a JWT access token."""

        token = jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM
        )

        return token


    def verify(self, token: str) -> dict:
        """Verify a JWT and return its payload."""

        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")

        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")