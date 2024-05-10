import os
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent


class AppSettings(BaseModel):
    host: str = os.environ["APP_HOST"]
    port: int = int(os.environ["APP_PORT"])
    reload: bool = bool(os.environ["APP_RELOAD"])


class DbSettings(BaseModel):
    db_name: str = os.environ["DB_NAME"]
    async_db_engine: str = os.environ["ASYNC_DB_ENGINE"]
    sync_db_engine: str = os.environ["SYNC_DB_ENGINE"]
    db_user: str = os.environ["DB_USER"]
    db_password: str = os.environ["DB_PASSWORD"]
    db_host: str = os.environ["DB_HOST"]
    db_port: int = int(os.environ["DB_PORT"])

    postgres_db: str = os.environ["POSTGRES_DB"]

    base_url: str = (
        f"{async_db_engine}://{db_user}:{db_password}@{db_host}:{db_port}"
    )
    db_url: str = f"{base_url}/{db_name}"

    postgres_url: str = f"{base_url}/{postgres_db}"

    sync_db_url: str = (
        f"{sync_db_engine}://{db_user}:{db_password}@"
        f"{db_host}:{db_port}/{db_name}"
    )
    echo: bool = bool(os.environ["DB_ECHO"])


class Log(BaseModel):
    level: str = os.environ["LOGGER_LEVEL"]


class JWTSettings(BaseModel):
    ACCESS_TOKEN_TYPE: str = "Access"
    REFRESH_TOKEN_TYPE: str = "Refresh"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30


class SecuritySettings(BaseModel):
    ALGORITHM: str = os.environ["SECURITY_ALGORITHM"]
    SECRET_KEY: str = os.environ["SECRET_KEY"]


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    db: DbSettings = DbSettings()
    jwt: JWTSettings = JWTSettings()
    security: SecuritySettings = SecuritySettings()
    log: Log = Log()


settings = Settings()
