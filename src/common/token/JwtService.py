# jwt_utils.py

import jwt

SECRET_KEY = "change-this-to-a-long-random-secret"
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