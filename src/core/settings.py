import os
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class AppSettings(BaseModel):
    host: str = os.getenv("APP_HOST", "0.0.0.0")
    port: int = os.getenv("APP_PORT", 8000)
    reload: bool = os.getenv("APP_RELOAD", True)


class Settings(BaseSettings):
    app: AppSettings = AppSettings()


settings = Settings()
