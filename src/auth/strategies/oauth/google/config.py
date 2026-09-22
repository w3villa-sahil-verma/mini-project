from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict;


class Settings(BaseSettings):
    GOOGLE_CLIENT_ID: str = Field(default="")
    GOOGLE_CLIENT_SECREATE: str = Field(default="")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"   # or remove this line if you want strict validation
    )


settings = Settings()