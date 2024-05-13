import json
from typing import Any

from fastapi import Depends
from fastapi.security import HTTPBearer, OAuth2PasswordBearer

from redis.asyncio import Redis

from auth.crud import get_user_by_email
from auth.exceptions import (
    credential_exceptions,
    invalid_token_credential_exception,
    invalid_token_exception,
    invalid_token_type_exception,
    revoked_token_error,
)
from auth.utils.my_jwt import validate_token_type
from core.redis_config import get_redis_client
from core.settings import settings
from models import User

http_bearer = HTTPBearer(auto_error=False)
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
) -> User:
    if not validate_token_type(payload, settings.jwt.REFRESH_TOKEN_TYPE):
        raise invalid_token_type_exception
    return await get_user_by_email(email=payload.get("sub"))
