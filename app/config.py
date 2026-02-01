from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


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
    GOOGLE_API_KEY: str = Field(...)
    HF_TOKEN: str = Field(...)
    MLFLOW_TRACKING_URI: str = Field(...)

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
