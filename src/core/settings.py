import os
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class AppSettings(BaseModel):
    host: str = os.getenv("APP_HOST", "0.0.0.0")
    port: int = int(os.getenv("APP_PORT", 8000))
    reload: bool = os.getenv("APP_RELOAD", True)


class DbSettings(BaseModel):
    db_name: str = os.getenv("DB_NAME")
    db_engine: str = os.getenv("DB_ENGINE")
    db_user: str = os.getenv("DB_USER")
    db_password: str = os.getenv("DB_PASSWORD")
    db_host: str = os.getenv("DB_HOST")
    db_port: int = os.getenv("DB_PORT")
    postgres_url: str = (
        f"{db_engine}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    sync_postgres_url: str = (
        f"postgresql+psycopg2://{db_user}:{db_password}@"
        f"{db_host}:{db_port}/{db_name}"
    )
    echo: bool = os.getenv("DB_ECHO", True)


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    db: DbSettings = DbSettings()


settings = Settings()
