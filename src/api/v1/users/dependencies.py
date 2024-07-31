import json
from typing import Any, AsyncGenerator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from redis.asyncio import Redis

from src.api.exceptions import (
    CREDENTIAL_EXCEPTIONS,
    INVALID_TOKEN_CREDENTIAL_EXCEPTION,
    INVALID_TOKEN_EXCEPTION,
    INVALID_TOKEN_TYPE_EXCEPTION,
    REVOKED_TOKEN_ERROR,
)
from src.api.v1.users.crud import get_user_by_email
from src.api.v1.users.utils.my_jwt import validate_token_type
from src.db.models import User
from src.settings import JWTSettings, RedisSettings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login/")


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    redis_client = Redis(host=RedisSettings.host, port=RedisSettings.port)
    yield redis_client
    await redis_client.aclose()


async def get_token_payload(
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis_client),
) -> dict[str, Any]:
    if (payload := await redis.get(token)) is None:
        raise CREDENTIAL_EXCEPTIONS
    return json.loads(payload)


async def get_current_user(
    token_payload: dict[str, Any] = Depends(get_token_payload),
) -> User:
    if (email := token_payload.get("sub")) is None:
        raise INVALID_TOKEN_EXCEPTION

    if token_payload.get("token_revoked") is True:
        raise REVOKED_TOKEN_ERROR

    if (user := await get_user_by_email(email=email)) is None:
        raise INVALID_TOKEN_CREDENTIAL_EXCEPTION

    return user


async def get_user_from_refresh_token(
    payload: dict[str, Any] = Depends(get_token_payload),
) -> User | None:
    if not validate_token_type(payload, JWTSettings.REFRESH_TOKEN_TYPE):
        raise INVALID_TOKEN_TYPE_EXCEPTION
    if (email := payload.get("sub")) is None:
        raise INVALID_TOKEN_EXCEPTION
    if (user := await get_user_by_email(email)) is None:
        raise INVALID_TOKEN_CREDENTIAL_EXCEPTION

    return user
