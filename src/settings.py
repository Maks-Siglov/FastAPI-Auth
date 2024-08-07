import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

dotenv_path = os.path.join(BASE_DIR, "..", ".env.local")
load_dotenv(dotenv_path)


@dataclass
class AppSettings:
    host: str = os.environ["APP_HOST"]
    port: int = int(os.environ["APP_PORT"])
    reload: bool = bool(os.environ["APP_RELOAD"])


@dataclass
class DbSettings:
    db_name: str = os.environ["DB_NAME"]
    db_user: str = os.environ["DB_USER"]
    db_password: str = os.environ["DB_PASSWORD"]
    db_host: str = os.environ["DB_HOST"]
    db_port: int = int(os.environ["DB_PORT"])

    async_db_engine: str = os.environ["ASYNC_DB_ENGINE"]
    sync_db_engine: str = os.environ["SYNC_DB_ENGINE"]

    postgres_db: str = os.environ["BASE_POSTGRES_DB"]

    echo: bool = bool(os.environ["DB_ECHO"])

    @classmethod
    def get_async_db_url(cls) -> str:
        return (
            f"{cls.async_db_engine}://{cls.db_user}:{cls.db_password}@"
            f"{cls.db_host}:{cls.db_port}/{cls.db_name}"
        )

    @classmethod
    def get_sync_db_url(cls) -> str:
        return (
            f"{cls.sync_db_engine}://{cls.db_user}:{cls.db_password}@"
            f"{cls.db_host}:{cls.db_port}/{cls.db_name}"
        )

    @classmethod
    def get_postgres_db_url(cls) -> str:
        return (
            f"{cls.async_db_engine}://{cls.db_user}:{cls.db_password}@"
            f"{cls.db_host}:{cls.db_port}/{cls.postgres_db}"
        )


@dataclass
class LogSettings:
    level: str = os.environ["LOGGER_LEVEL"]
    log_file: str = os.environ["LOGGER_FILE"]
    ROOT_FORMATTER: str = (
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )


@dataclass
class RedisSettings:
    host: str = os.environ["REDIS_HOST"]
    port: int = int(os.environ["REDIS_PORT"])

    @classmethod
    def get_redis_url(cls) -> str:
        return f"redis://{cls.host}:{cls.port}"


@dataclass
class JWTSettings:
    ACCESS_TOKEN_TYPE: str = "Access"
    REFRESH_TOKEN_TYPE: str = "Refresh"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 15 * 60
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 30 * 24 * 30 * 60


@dataclass
class SecuritySettings:
    ALGORITHM: str = os.environ["SECURITY_ALGORITHM"]
    SECRET_KEY: str = os.environ["SECRET_KEY"]
