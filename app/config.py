from pydantic_settings import BaseSettings
from pydantic import Field
from pydantic import ConfigDict


class Settings(BaseSettings):
    DATABASE_HOST: str = Field(...)
    DATABASE_PASSWORD: str = Field(...)
    DATABASE_NAME: str = Field(...)
    DATABASE_USER: str = Field(...)
    DATABASE_PORT: int = Field(...)
    SECRET_KEY: str = Field(...)
    ALGORITHM: str = Field(...)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(...)
    FRONTEND_URL: str = Field(...)

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
