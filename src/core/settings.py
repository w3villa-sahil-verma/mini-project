from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = ""
    MAIL_FROM_NAME: str = "GYM"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

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

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_ignore_empty=True,
        extra="ignore",
    )


settings = Settings()
