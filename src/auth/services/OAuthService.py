import hmac
import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Annotated, Literal
from urllib.parse import urlencode

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.token.JwtService import JwtTokenService
from src.common.token.constants import TOKEN_TYPES
from src.database.Database import getAsyncDbSession
from src.models.OAuthIdentity import OAuthIdentity
from src.models.User import User

OAuthProvider = Literal["google", "facebook"]
OAUTH_STATE_MAX_AGE_SECONDS = 600
ACCESS_TOKEN_LIFETIME = timedelta(days=1)
FACEBOOK_GRAPH_VERSION_DEFAULT = "v24.0"
logger = logging.getLogger(__name__)


class OAuthSettings(BaseSettings):
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = (
        "http://localhost:8000/api/v1/auth/oauth/google/callback"
    )
    facebook_app_id: str = ""
    facebook_app_secret: str = ""
    facebook_redirect_uri: str = (
        "http://localhost:8000/api/v1/auth/oauth/facebook/callback"
    )
    facebook_graph_version: str = FACEBOOK_GRAPH_VERSION_DEFAULT
    frontend_base_url: str = "http://localhost:5173"
    oauth_cookie_secure: bool = True

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        extra="ignore",
    )


@dataclass(frozen=True)
class ProviderConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    authorization_endpoint: str
    token_endpoint: str
    profile_endpoint: str
    scope: str


class OAuthService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(getAsyncDbSession)],
        token_service: Annotated[JwtTokenService, Depends(JwtTokenService)],
    ) -> None:
        self.db = db
        self.token_service = token_service
        self.settings = OAuthSettings()

    def get_meta(self) -> dict:
        providers = []
        for provider in ("google", "facebook"):
            try:
                self._provider_config(provider)
            except HTTPException:
                continue
            providers.append(provider)
        return {
            "message": "OAuth providers retrieved successfully",
            "data": {"providers": providers},
        }

    def start(self, provider: OAuthProvider) -> RedirectResponse:
        config = self._provider_config(provider)
        state = secrets.token_urlsafe(32)
        authorization_params = urlencode(
            {
                "client_id": config.client_id,
                "redirect_uri": config.redirect_uri,
                "response_type": "code",
                "scope": config.scope,
                "state": state,
            }
        )
        response = RedirectResponse(
            url=f"{config.authorization_endpoint}?{authorization_params}",
            status_code=status.HTTP_302_FOUND,
        )
        response.set_cookie(
            key=self._state_cookie_name(provider),
            value=state,
            max_age=OAUTH_STATE_MAX_AGE_SECONDS,
            httponly=True,
            secure=self.settings.oauth_cookie_secure,
            samesite="lax",
            path="/",
        )
        return response

    async def callback(
        self,
        provider: OAuthProvider,
        *,
        code: str | None,
        state: str | None,
        stored_state: str | None,
        provider_error: str | None,
    ) -> RedirectResponse:
        if (
            provider_error
            or not code
            or not state
            or not stored_state
            or not hmac.compare_digest(state, stored_state)
        ):
            return self._failed_callback(provider)

        config = self._provider_config(provider)
        try:
            profile = await self._fetch_profile(provider, config, code)
            access_token = await self._authenticate_profile(provider, profile)
        except HTTPException as error:
            logger.warning(
                "%s OAuth callback failed: %s",
                provider,
                error.detail,
            )
            return self._failed_callback(provider)

        response = RedirectResponse(
            url=self.settings.frontend_base_url.rstrip("/"),
            status_code=status.HTTP_302_FOUND,
        )
        response.delete_cookie(
            key=self._state_cookie_name(provider),
            httponly=True,
            secure=self.settings.oauth_cookie_secure,
            samesite="lax",
            path="/",
        )
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=self.settings.oauth_cookie_secure,
            samesite="lax",
            max_age=int(ACCESS_TOKEN_LIFETIME.total_seconds()),
            path="/",
        )
        return response

    async def _fetch_profile(
        self,
        provider: OAuthProvider,
        config: ProviderConfig,
        code: str,
    ) -> dict:
        token_params = {
            "client_id": config.client_id,
            "client_secret": config.client_secret,
            "redirect_uri": config.redirect_uri,
            "code": code,
            "grant_type": "authorization_code",
        }

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                token_response = await client.post(
                    config.token_endpoint,
                    data=token_params,
                    headers={"Accept": "application/json"},
                )
                token_response.raise_for_status()
                token_payload = token_response.json()
                if not isinstance(token_payload, dict):
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="OAuth provider returned an invalid token response.",
                    )
                provider_access_token = token_payload.get("access_token")
                if not isinstance(provider_access_token, str):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="OAuth provider did not return an access token.",
                    )

                profile_response = await client.get(
                    config.profile_endpoint,
                    params=(
                        {"fields": "id,email"}
                        if provider == "facebook"
                        else None
                    ),
                    headers={"Authorization": f"Bearer {provider_access_token}"},
                )
                profile_response.raise_for_status()
                profile = profile_response.json()
        except httpx.HTTPError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Could not complete authentication with the OAuth provider.",
            ) from error
        except ValueError as error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="OAuth provider returned an invalid response.",
            ) from error

        if not isinstance(profile, dict):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="OAuth provider returned an invalid profile response.",
            )
        provider_user_id = (
            profile.get("sub") if provider == "google" else profile.get("id")
        )
        email = profile.get("email")
        if (
            not isinstance(provider_user_id, str)
            or not provider_user_id
            or not isinstance(email, str)
            or not email
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OAuth provider did not return a usable email address.",
            )
        if provider == "google" and profile.get("email_verified") is not True:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Google must confirm the email address before signing in.",
            )
        return {"provider_user_id": provider_user_id, "email": email}

    async def _authenticate_profile(
        self,
        provider: OAuthProvider,
        profile: dict,
    ) -> str:
        provider_user_id = profile["provider_user_id"]
        email = profile["email"].strip().lower()
        if len(email) > 30:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="This email address is too long for a user account.",
            )

        identity = await self.db.scalar(
            select(OAuthIdentity).where(
                OAuthIdentity.provider == provider,
                OAuthIdentity.provider_user_id == provider_user_id,
            )
        )
        user = (
            await self.db.get(User, identity.user_id)
            if identity is not None
            else None
        )
        if user is not None and user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This user account is not available.",
            )

        if user is None:
            user = await self.db.scalar(select(User).where(User.email == email))
            if user is not None and user.is_deleted:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This user account is not available.",
                )
            if user is not None and provider == "facebook":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Sign in with the existing account method before linking Facebook.",
                )

            if user is None:
                user = User(email=email)
                self.db.add(user)
                await self.db.flush()

            self.db.add(
                OAuthIdentity(
                    user_id=user.id,
                    provider=provider,
                    provider_user_id=provider_user_id,
                )
            )
            try:
                await self.db.commit()
            except IntegrityError:
                await self.db.rollback()
                user = await self.db.scalar(
                    select(User)
                    .join(OAuthIdentity, OAuthIdentity.user_id == User.id)
                    .where(
                        OAuthIdentity.provider == provider,
                        OAuthIdentity.provider_user_id == provider_user_id,
                    )
                )
                if user is None:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Could not link this OAuth account. Please try again.",
                    )

        now = datetime.now(timezone.utc)
        return self.token_service.sign(
            {
                "user_id": user.id,
                "role": user.role.value,
                "type": TOKEN_TYPES.ACCESS,
                "exp": now + ACCESS_TOKEN_LIFETIME,
                "iat": now,
            }
        )

    def _provider_config(self, provider: OAuthProvider) -> ProviderConfig:
        if provider == "google":
            client_id = self.settings.google_client_id
            client_secret = self.settings.google_client_secret
            config = ProviderConfig(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=self.settings.google_redirect_uri,
                authorization_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
                token_endpoint="https://oauth2.googleapis.com/token",
                profile_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
                scope="openid email profile",
            )
        else:
            client_id = self.settings.facebook_app_id
            client_secret = self.settings.facebook_app_secret
            graph_base = (
                f"https://graph.facebook.com/"
                f"{self.settings.facebook_graph_version.strip('/')}"
            )
            config = ProviderConfig(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=self.settings.facebook_redirect_uri,
                authorization_endpoint=f"https://www.facebook.com/{self.settings.facebook_graph_version}/dialog/oauth",
                token_endpoint=f"{graph_base}/oauth/access_token",
                profile_endpoint=f"{graph_base}/me",
                scope="email,public_profile",
            )

        if not client_id or not client_secret:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"{provider.capitalize()} sign-in is not configured.",
            )
        return config

    def _failed_callback(self, provider: OAuthProvider) -> RedirectResponse:
        response = RedirectResponse(
            url=f"{self.settings.frontend_base_url.rstrip('/')}/login?oauth_error=1",
            status_code=status.HTTP_302_FOUND,
        )
        response.delete_cookie(
            key=self._state_cookie_name(provider),
            httponly=True,
            secure=self.settings.oauth_cookie_secure,
            samesite="lax",
            path="/",
        )
        return response

    @staticmethod
    def _state_cookie_name(provider: OAuthProvider) -> str:
        return f"oauth_state_{provider}"
