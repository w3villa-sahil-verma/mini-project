from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MAIL_USERNAME: str = Field(default="")
    MAIL_PASSWORD: str = Field(default="")
    MAIL_FROM: str = Field(default="")
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "GYM"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

    class Config:
        env_file = ".env"


settings = Settings()