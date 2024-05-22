import time
from typing import Any

import jwt

from src.core.settings import jwt_settings, security_settings
from src.db.models import User


def create_jwt(
    token_type: str,
    token_data: dict,
    expire_time_seconds: int,
) -> tuple[str, dict[str, Any]]:
    jwt_payload = {"type": token_type}
    now = int(time.time())
    jwt_payload["iat"] = now
    jwt_payload["exp"] = now + expire_time_seconds

    jwt_payload.update(token_data)
    token = jwt.encode(
        payload=jwt_payload,
        algorithm=security_settings.ALGORITHM,
        key=security_settings.SECRET_KEY,
    )

    return token, jwt_payload


def create_access_token(user: User) -> tuple[str, dict[str, Any]]:
    jwt_payload = {
        "sub": user.email,
        "id": user.id,
        "is_active": user.is_active,
        "token_revoked": False,
    }
    return create_jwt(
        jwt_settings.ACCESS_TOKEN_TYPE,
        jwt_payload,
        jwt_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
    )


def create_refresh_token(user: User) -> tuple[str, dict[str, Any]]:
    jwt_payload = {"sub": user.email, "token_revoked": False}
    return create_jwt(
        jwt_settings.REFRESH_TOKEN_TYPE,
        jwt_payload,
        jwt_settings.REFRESH_TOKEN_EXPIRE_SECONDS,
    )


def revoke_jwt(payload: dict[str, Any]) -> str:
    payload["token_revoked"] = True
    return jwt.encode(
        payload=payload,
        algorithm=security_settings.ALGORITHM,
        key=security_settings.SECRET_KEY,
    )


def decode_jwt(token: str):
    return jwt.decode(
        jwt=token,
        algorithms=[security_settings.ALGORITHM],
        key=security_settings.SECRET_KEY,
    )


def validate_token_type(payload: dict[str, Any], token_type: str) -> bool:
    return payload.get("type") == token_type
