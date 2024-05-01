from typing import Any

from fastapi import Depends
from fastapi.security import HTTPBearer, OAuth2PasswordBearer

from sqlalchemy.ext.asyncio import AsyncSession

from jwt import InvalidTokenError

from auth.crud import get_user_by_email
from auth.exceptions import (
    invalid_token_credential_exception,
    invalid_token_exception,
    invalid_token_type_exception,
    revoked_token_error,
    unable_decode_jwt_exception
)
from auth.utils.my_jwt import decode_jwt, validate_token_type
from core.settings import settings
from db.main import get_session
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
    payload: dict[str, Any] = Depends(get_token_payload),
    session: AsyncSession = Depends(get_session),
) -> User:
    if (email := payload.get("sub")) is None:
        raise invalid_token_exception

    if payload.get("token_revoked") is True:
        raise revoked_token_error

    if (user := await get_user_by_email(session=session, email=email)) is None:
        raise invalid_token_credential_exception

    return user


async def get_user_from_refresh_token(
    payload: dict[str, Any] = Depends(get_token_payload),
    session: AsyncSession = Depends(get_session),
) -> User:
    if not validate_token_type(payload, settings.jwt.REFRESH_TOKEN_TYPE):
        raise invalid_token_type_exception
    return await get_user_by_email(session, email=payload.get("sub"))
