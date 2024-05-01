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

    postgres_db: str = os.getenv("POSTGRES_DB")

    base_url: str = (
        f"{db_engine}://{db_user}:{db_password}@{db_host}:{db_port}"
    )
    db_url: str = f"{base_url}/{db_name}"

    postgres_url: str = f"{base_url}/{postgres_db}"

    sync_db_url: str = (
        f"postgresql+psycopg2://{db_user}:{db_password}@"
        f"{db_host}:{db_port}/{db_name}"
    )
    echo: bool = os.getenv("DB_ECHO", True)


class JWTSettings(BaseModel):
    ACCESS_TOKEN_TYPE: str = "Access"
    REFRESH_TOKEN_TYPE: str = "Refresh"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30


class SecuritySettings(BaseModel):
    ALGORITHM: str = os.getenv("SECURITY_ALGORITHM")
    SECRET_KEY: str = os.getenv("SECRET_KEY")


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    db: DbSettings = DbSettings()
    jwt: JWTSettings = JWTSettings()
    security: SecuritySettings = SecuritySettings()


settings = Settings()
