import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

dotenv_path = os.path.join(BASE_DIR, "..", ".env.local")
load_dotenv(dotenv_path)


class AppSettings(BaseSettings):
    host: str = os.environ["APP_HOST"]
    port: int = int(os.environ["APP_PORT"])
    reload: bool = bool(os.environ["APP_RELOAD"])


class DbSettings(BaseSettings):
    db_name: str = os.environ["DB_NAME"]
    db_user: str = os.environ["DB_USER"]
    db_password: str = os.environ["DB_PASSWORD"]
    db_host: str = os.environ["DB_HOST"]
    db_port: int = int(os.environ["DB_PORT"])

    async_db_engine: str = os.environ["ASYNC_DB_ENGINE"]
    sync_db_engine: str = os.environ["SYNC_DB_ENGINE"]

    postgres_db: str = os.environ["BASE_POSTGRES_DB"]

    echo: bool = bool(os.environ["DB_ECHO"])

    def get_async_db_url(self) -> str:
        return (
            f"{self.async_db_engine}://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def get_sync_db_url(self) -> str:
        return (
            f"{self.sync_db_engine}://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )

    def get_postgres_db_url(self) -> str:
        return (
            f"{self.async_db_engine}://{self.db_user}:{self.db_password}@"
            f"{self.db_host}:{self.db_port}/{self.postgres_db}"
        )


class LogSettings(BaseSettings):
    level: str = os.environ["LOGGER_LEVEL"]
    ROOT_FORMATTER: str = (
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )


class RedisSettings(BaseSettings):
    host: str = os.environ["REDIS_HOST"]
    port: int = int(os.environ["REDIS_PORT"])

    def get_redis_url(self) -> str:
        return f"redis://{self.host}:{self.port}"


class JWTSettings(BaseSettings):
    ACCESS_TOKEN_TYPE: str = "Access"
    REFRESH_TOKEN_TYPE: str = "Refresh"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 15 * 60
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 30 * 24 * 30 * 60


class SecuritySettings(BaseSettings):
    ALGORITHM: str = os.environ["SECURITY_ALGORITHM"]
    SECRET_KEY: str = os.environ["SECRET_KEY"]


app_settings: AppSettings = AppSettings()
db_settings: DbSettings = DbSettings()
jwt_settings: JWTSettings = JWTSettings()
security_settings: SecuritySettings = SecuritySettings()
log_settings: LogSettings = LogSettings()
redis_settings: RedisSettings = RedisSettings()
