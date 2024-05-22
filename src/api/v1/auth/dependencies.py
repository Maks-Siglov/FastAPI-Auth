import json
from typing import Any

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from redis.asyncio import Redis

from src.api.v1.auth.crud import get_user_by_email
from exceptions import (
    credential_exceptions,
    invalid_token_credential_exception,
    invalid_token_exception,
    invalid_token_type_exception,
    revoked_token_error,
)
from src.api.v1.auth.utils.my_jwt import validate_token_type
from src.redis_config import get_redis_client
from src.settings import jwt_settings
from src.db.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")


async def get_token_payload(
    token: str = Depends(oauth2_scheme),
    redis: Redis = Depends(get_redis_client),
) -> dict[str, Any]:
    if (payload := await redis.get(token)) is None:
        raise credential_exceptions
    return json.loads(payload)


async def get_current_user(
    token_payload: dict[str, Any] = Depends(get_token_payload),
) -> User:

    if (email := token_payload.get("sub")) is None:
        raise invalid_token_exception

    if token_payload.get("token_revoked") is True:
        raise revoked_token_error

    if (user := await get_user_by_email(email=email)) is None:
        raise invalid_token_credential_exception

    return user


async def get_user_from_refresh_token(
    payload: dict[str, Any] = Depends(get_token_payload),
) -> User | None:
    if not validate_token_type(payload, jwt_settings.REFRESH_TOKEN_TYPE):
        raise invalid_token_type_exception
    if (user := await get_user_by_email(email=payload.get("sub"))) is None:
        raise invalid_token_credential_exception

    return user

