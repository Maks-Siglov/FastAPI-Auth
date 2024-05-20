import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

dotenv_path = os.path.join(BASE_DIR, "..", ".env.local")
load_dotenv(dotenv_path)


class AppSettings(BaseModel):
    host: str = os.environ["APP_HOST"]
    port: int = int(os.environ["APP_PORT"])
    reload: bool = bool(os.environ["APP_RELOAD"])


class DbSettings(BaseModel):
    db_name: str = os.environ["DB_NAME"]
    db_user: str = os.environ["DB_USER"]
    db_password: str = os.environ["DB_PASSWORD"]
    db_host: str = os.environ["DB_HOST"]
    db_port: int = int(os.environ["DB_PORT"])

    async_db_engine: str = os.environ["ASYNC_DB_ENGINE"]
    sync_db_engine: str = os.environ["SYNC_DB_ENGINE"]

    postgres_db: str = os.environ["BASE_POSTGRES_DB"]

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


class LogSettings(BaseModel):
    level: str = os.environ["LOGGER_LEVEL"]
    ROOT_FORMATTER = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"


class RedisSettings(BaseModel):
    host: str = os.environ["REDIS_HOST"]
    port: int = os.environ["REDIS_PORT"]
    url: str = f"redis://{host}:{port}"


class JWTSettings(BaseModel):
    ACCESS_TOKEN_TYPE: str = "Access"
    REFRESH_TOKEN_TYPE: str = "Refresh"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 15 * 60
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 30 * 24 * 30 * 60


class SecuritySettings(BaseModel):
    ALGORITHM: str = os.environ["SECURITY_ALGORITHM"]
    SECRET_KEY: str = os.environ["SECRET_KEY"]


class Settings(BaseSettings):
    app: AppSettings = AppSettings()
    db: DbSettings = DbSettings()
    jwt: JWTSettings = JWTSettings()
    security: SecuritySettings = SecuritySettings()
    log: LogSettings = LogSettings()
    redis: RedisSettings = RedisSettings()


settings = Settings()
