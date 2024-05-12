import time
from typing import Any

from fastapi import Depends
from fastapi.security import HTTPBearer, OAuth2PasswordBearer

from jwt import InvalidTokenError
from redis import Redis

from auth.crud import get_user, get_user_by_email
from auth.exceptions import (
    invalid_token_credential_exception,
    invalid_token_exception,
    invalid_token_type_exception,
    invalid_user_cache_id_exception,
    revoked_token_error,
    unable_decode_jwt_exception
)
from auth.utils.my_jwt import decode_jwt, validate_token_type
from core.redis_config import get_redis
from core.settings import settings
from models import User

http_bearer = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/")


def get_token_payload(token: str = Depends(oauth2_scheme)) -> dict[str, Any]:
    try:
        payload = decode_jwt(token)
    except InvalidTokenError:
        raise unable_decode_jwt_exception
    return payload


async def get_current_user(
    token: str = Depends(oauth2_scheme), redis: Redis = Depends(get_redis)
) -> User:
    if (user_id := redis.get(token)) is not None:
        user_id = int(user_id.decode("utf-8"))
        if (user := await get_user(user_id)) is None:
            raise invalid_user_cache_id_exception
        return user

    try:
        token_payload = decode_jwt(token)
    except InvalidTokenError:
        raise unable_decode_jwt_exception

    if (email := token_payload.get("sub")) is None:
        raise invalid_token_exception

    if token_payload.get("token_revoked") is True:
        raise revoked_token_error

    if (user := await get_user_by_email(email=email)) is None:
        raise invalid_token_credential_exception

    expiration = token_payload["exp"] - int(time.time())
    await redis.set(name=token, value=user.id, ex=expiration)
    return user


async def get_user_from_refresh_token(
    payload: dict[str, Any] = Depends(get_token_payload),
) -> User:
    if not validate_token_type(payload, settings.jwt.REFRESH_TOKEN_TYPE):
        raise invalid_token_type_exception
    return await get_user_by_email(email=payload.get("sub"))
