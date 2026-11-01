from pathlib import Path

from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    JWT_SECRET_KEY: str = "change-this-to-a-long-random-secret"
    CORS_ALLOWED_ORIGINS: str = (
        "http://localhost:5173,http://127.0.0.1:5173"
    )
    AUTH_COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_FROM_NAME: str = "GYM"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    EMAIL_PROVIDER: Literal["smtp", "google_apps_script"] = "smtp"
    GOOGLE_SCRIPT_URL: str = ""
    EMAIL_API_SECRET: str = ""

    ROZAR_PAY_API_KEY: str = ""
    ROZAR_PAY_SECRET: str = ""

    STORJ_ACCESS_KEY: str = ""
    STORJ_SECRET_KEY: str = ""
    STORJ_BUCKET: str = ""
    STORJ_S3_ENDPOINT: str = "https://gateway.storjshare.io"
    STORJ_REGION: str = "us-east-1"
    STORJ_PUBLIC_BASE_URL: str = ""

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = (
        "http://localhost:8000/api/v1/auth/oauth/google/callback"
    )
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""
    FACEBOOK_REDIRECT_URI: str = (
        "http://localhost:8000/api/v1/auth/oauth/facebook/callback"
    )
    FACEBOOK_GRAPH_VERSION: str = "v24.0"
    FRONTEND_BASE_URL: str = "http://localhost:5173"
    OAUTH_COOKIE_SECURE: bool = False

    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str = "admin"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_NAME: str = "gym_management"
    DATABASE_DRIVER: str = "mysql+aiomysql"

    @field_validator("MAIL_PORT", mode="before")
    @classmethod
    def default_empty_mail_port(cls, value: object) -> object:
        return 587 if value == "" else value

    @field_validator("AUTH_COOKIE_SAMESITE", mode="before")
    @classmethod
    def default_empty_auth_cookie_samesite(cls, value: object) -> object:
        return "lax" if value == "" else value

    @field_validator("JWT_SECRET_KEY", mode="before")
    @classmethod
    def default_empty_jwt_secret_key(cls, value: object) -> object:
        return "change-this-to-a-long-random-secret" if value == "" else value

    @field_validator("MAIL_STARTTLS", mode="before")
    @classmethod
    def default_empty_mail_starttls(cls, value: object) -> object:
        return True if value == "" else value

    @field_validator("MAIL_SSL_TLS", mode="before")
    @classmethod
    def default_empty_mail_ssl_tls(cls, value: object) -> object:
        return False if value == "" else value

    @field_validator("MAIL_SERVER", mode="before")
    @classmethod
    def default_empty_mail_server(cls, value: object) -> object:
        return "smtp.gmail.com" if value == "" else value

    @field_validator("MAIL_FROM_NAME", mode="before")
    @classmethod
    def default_empty_mail_from_name(cls, value: object) -> object:
        return "GYM" if value == "" else value

    @field_validator("STORJ_S3_ENDPOINT", mode="before")
    @classmethod
    def default_empty_storj_endpoint(cls, value: object) -> object:
        return "https://gateway.storjshare.io" if value == "" else value

    @field_validator("STORJ_REGION", mode="before")
    @classmethod
    def default_empty_storj_region(cls, value: object) -> object:
        return "us-east-1" if value == "" else value

    @field_validator("DATABASE_PORT", mode="before")
    @classmethod
    def default_empty_database_port(cls, value: object) -> object:
        return 3306 if value == "" else value

    @model_validator(mode="after")
    def validate_auth_cookie_settings(self) -> "Settings":
        if self.AUTH_COOKIE_SAMESITE == "none" and not self.OAUTH_COOKIE_SECURE:
            raise ValueError(
                "OAUTH_COOKIE_SECURE must be true when AUTH_COOKIE_SAMESITE is none."
            )
        return self

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        extra="ignore",
    )

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [
            origin.strip().rstrip("/")
            for origin in self.CORS_ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]


settings = Settings()
